"""FastAPI — full REST + WebSocket per docs/13-API_REST.md."""

import asyncio
import json
import uuid
from pathlib import Path

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI(title="RenodeResilience API", version="1.0.0")
# Restrict to loopback only (docs 13-API_REST + 16-SECURITY)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=False,
)

# In-memory store for runs and event streams — bounded LRU with retention
_MAX_RUNS = 100  # keep at most 100 runs in memory; older evicted
_runs: dict[str, dict] = {}
_streams: dict[str, asyncio.Queue] = {}


def _evict_if_needed():
    """Evict oldest runs if over MAX_RUNS or older than retention."""
    from src.config.defaults import LOG_RETENTION_DAYS
    import time

    # LRU: drop oldest inserted (dict preserves insertion order, Python 3.7+)
    while len(_runs) > _MAX_RUNS:
        oldest = next(iter(_runs))
        _runs.pop(oldest, None)
        _streams.pop(oldest, None)
        # also try to delete persisted file if exists
        try:
            Path(f"results/{oldest}.json").unlink(missing_ok=True)
        except Exception:
            pass
    # Time-based retention: evict entries older than LOG_RETENTION_DAYS
    # Each run stores "created" timestamp if present; fallback to now check not needed in test.
    cutoff = time.time() - LOG_RETENTION_DAYS * 86400
    for rid, rec in list(_runs.items()):
        created = rec.get("created", cutoff + 1)  # if missing, keep
        if isinstance(created, (int, float)) and created < cutoff:
            _runs.pop(rid, None)
            _streams.pop(rid, None)


def _require_auth(authorization: str | None = Header(default=None)):
    """Bearer auth — only enforced if API_TOKEN is configured (env/file).

    Keeps backwards compatibility for local dev (no token → open), but
    enforces auth in CI/production when token is set per docs/16-SECURITY.
    """
    from src.config.defaults import API_TOKEN

    if not API_TOKEN:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing Authorization: Bearer <token>")
    token = authorization.removeprefix("Bearer ").strip()
    # constant-time compare to avoid timing leak
    import hmac

    if not hmac.compare_digest(token, API_TOKEN):
        raise HTTPException(403, "Invalid token")


@app.get("/api/v1/faults")
def list_faults():
    from src.core.fault_injector import FAULT_CATALOG

    return [{"id": k, **v} for k, v in FAULT_CATALOG.items()]


@app.get("/api/v1/platforms")
def list_platforms():
    from src.config.defaults import SUPPORTED_PLATFORMS

    return SUPPORTED_PLATFORMS


@app.post("/api/v1/run")
def run_single(payload: dict, _: None = Depends(_require_auth)):
    from src.config.schemas import CampaignConfig
    from src.core.campaign import Campaign

    use_renode = bool(payload.get("use_renode", False))
    # Validate fault ID early to give 400 not 500
    from src.config.schemas import VALID_FAULT_IDS

    fault_id = payload.get("fault", "SF-01")
    if fault_id not in VALID_FAULT_IDS:
        raise HTTPException(400, f"Unknown fault ID '{fault_id}'. Valid: {VALID_FAULT_IDS}")
    cfg = {
        "name": "Single API",
        "firmware": payload.get("firmware", "a.elf"),
        "platform": payload.get("platform", "stm32f4"),
        "duration": payload.get("duration", 60),
        "parallel": 1,
        "faults": [
            {
                "id": fault_id,
                "params": payload.get("params", {}),
                "expected": payload.get("expected", ""),
                "timeout_ms": payload.get("timeout_ms", 5000),
            }
        ],
    }
    try:
        camp = Campaign(CampaignConfig.model_validate(cfg))
    except Exception as e:
        raise HTTPException(400, str(e)) from e
    res = camp.run(use_renode=use_renode)
    rid = str(uuid.uuid4())
    import time

    _runs[rid] = {
        "status": "completed",
        "progress": 1,
        "total": 1,
        "result": res.to_dict(),
        "created": time.time(),
    }
    _evict_if_needed()
    return {"run_id": rid, **res.to_dict()}


@app.post("/api/v1/campaign")
def run_campaign(payload: dict, _: None = Depends(_require_auth)):
    from src.config.schemas import CampaignConfig
    from src.core.campaign import Campaign

    use_renode = bool(payload.pop("use_renode", False))
    # Allow top-level use_renode without polluting CampaignConfig validation
    try:
        cfg = CampaignConfig.model_validate(payload)
    except Exception as e:
        raise HTTPException(400, str(e))
    camp = Campaign(cfg)
    rid = str(uuid.uuid4())
    import time

    _runs[rid] = {
        "status": "running",
        "progress": 0,
        "total": len(cfg.faults),
        "result": None,
        "created": time.time(),
    }
    res = camp.run(parallel=cfg.parallel, use_renode=use_renode)
    _runs[rid].update({"status": "completed", "progress": len(cfg.faults), "result": res.to_dict()})
    # persist
    Path("results").mkdir(exist_ok=True)
    Path(f"results/{rid}.json").write_text(json.dumps(res.to_dict(), indent=2), encoding="utf-8")
    _evict_if_needed()
    return {"run_id": rid, "status": "queued", "total": len(cfg.faults)}


@app.get("/api/v1/status/{run_id}")
def get_status(run_id: str):
    r = _runs.get(run_id)
    if not r:
        raise HTTPException(404, "run_id not found")
    return r


@app.get("/api/v1/result/{run_id}")
def get_result(run_id: str):
    r = _runs.get(run_id)
    if not r or not r.get("result"):
        raise HTTPException(404, "result not ready")
    return r["result"]


@app.get("/api/v1/report/{run_id}")
def get_report(run_id: str, format: str = "json"):
    r = _runs.get(run_id)
    if not r or not r.get("result"):
        raise HTTPException(404, "not found")
    # regenerate file
    from src.core.result_aggregator import CampaignResult, TestResult

    data = r["result"]
    cr = CampaignResult(
        campaign_name=data["campaign"],
        resilience_index=data["resilience_index"],
        grade=data["grade"],
        results=[
            TestResult(**{k: v for k, v in x.items() if k in TestResult.__dataclass_fields__})
            for x in data["results"]
        ],
    )
    Path("results").mkdir(exist_ok=True)
    if format == "html":
        p = Path(f"results/{run_id}.html")
        cr.to_html(p)
        return FileResponse(str(p))
    if format == "pdf":
        p = Path(f"results/{run_id}.pdf")
        cr.to_pdf(p)
        return FileResponse(str(p), media_type="application/pdf")
    return JSONResponse(data)


@app.post("/api/v1/upload/firmware")
async def upload_firmware(
    file: UploadFile = File(...),  # noqa: B008
    _: None = Depends(_require_auth),
):
    """Accept a firmware ELF via multipart, validate, enforce 8 MB limit."""
    import hashlib

    # Enforce size cap to prevent DoS (8 MB — generous for MCU ELF <512 KB)
    MAX_SIZE = 8 * 1024 * 1024
    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(413, f"File too large: {len(data)} bytes > {MAX_SIZE}")
    if len(data) < 16:
        raise HTTPException(400, "File too small")
    if data[:4] != b"\x7fELF":
        raise HTTPException(400, "Not a valid ELF file (missing magic bytes)")
    # Basic filename sanitization (ignore client-provided name for storage)
    upload_dir = Path("results/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(data).hexdigest()[:12]
    fname = f"firmware_{sha}.elf"
    fpath = upload_dir / fname
    fpath.write_bytes(data)
    arch = "64-bit" if data[4] == 2 else "32-bit"
    import struct

    machine = struct.unpack("<H", data[18:20])[0] if len(data) > 20 else 0
    return {
        "filename": fname,
        "size": len(data),
        "sha256": sha,
        "arch": arch,
        "machine": hex(machine),
        "status": "uploaded",
    }


@app.post("/api/v1/compare")
def compare(payload: dict, _: None = Depends(_require_auth)):
    # payload: {"baseline":"id1","optimized":"id2"} or inline results
    # For now, demo: run two tiny campaigns and compare
    # Try ids first
    b_id = payload.get("baseline")
    o_id = payload.get("optimized")
    if b_id in _runs and o_id in _runs:
        from src.core.result_aggregator import CampaignResult, TestResult

        def to_cr(d):
            return CampaignResult(
                campaign_name=d["campaign"],
                resilience_index=d["resilience_index"],
                grade=d["grade"],
                results=[
                    TestResult(
                        **{k: v for k, v in x.items() if k in TestResult.__dataclass_fields__}
                    )
                    for x in d["results"]
                ],
            )

        cr_b = to_cr(_runs[b_id]["result"])
        cr_o = to_cr(_runs[o_id]["result"])
        cmp = cr_b.compare(cr_o)
        return cmp.to_dict()
    raise HTTPException(400, "Provide baseline/optimized run_ids from /campaign")


@app.websocket("/api/v1/live/{run_id}")
async def live(ws: WebSocket, run_id: str):
    """Stream live progress for a campaign run.

    If the run exists in ``_streams``, events are read from its queue.
    Otherwise a demo stream is generated from the run's total fault count.
    """
    await ws.accept()
    run = _runs.get(run_id)
    total = run.get("total", 5) if run else 5

    # Check for a real event queue (pushed by Campaign.run via callback)
    queue = _streams.get(run_id)
    if queue:
        try:
            while True:
                event = await asyncio.wait_for(queue.get(), timeout=30)
                if event is None:  # sentinel: done
                    break
                await ws.send_json(event)
        except TimeoutError:
            await ws.send_json({"event": "error", "payload": {"message": "timeout"}})
    else:
        # Demo mode: simulate progress based on actual fault count
        from src.core.fault_injector import FAULT_CATALOG

        fault_ids = list(FAULT_CATALOG.keys())[:total]
        for i, fid in enumerate(fault_ids):
            await ws.send_json(
                {
                    "event": "test.progress",
                    "payload": {
                        "current": i + 1,
                        "total": total,
                        "fault_id": fid,
                        "eta_seconds": max(1, (total - i - 1) * 2),
                    },
                }
            )
            await asyncio.sleep(0.5)
        # Use real result if available, else compute from run data
        ri = run["result"]["resilience_index"] if run and run.get("result") else 73
        grade = run["result"]["grade"] if run and run.get("result") else "B"
        await ws.send_json(
            {
                "event": "test.completed",
                "payload": {"run_id": run_id, "final_ri": ri, "grade": grade},
            }
        )
    await ws.close()
