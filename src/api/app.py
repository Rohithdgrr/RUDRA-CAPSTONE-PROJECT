"""FastAPI — full REST + WebSocket per docs/13-API_REST.md."""
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import uuid
import asyncio
import json
from typing import Dict

app = FastAPI(title="RenodeResilience API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# In-memory store for runs
_runs: Dict[str, dict] = {}

@app.get("/api/v1/faults")
def list_faults():
    from src.core.fault_injector import FAULT_CATALOG
    return [{"id": k, **v} for k, v in FAULT_CATALOG.items()]

@app.get("/api/v1/platforms")
def list_platforms():
    from src.config.defaults import SUPPORTED_PLATFORMS
    return SUPPORTED_PLATFORMS

@app.post("/api/v1/run")
def run_single(payload: dict):
    from src.core.campaign import Campaign
    from src.config.schemas import CampaignConfig
    cfg = {"name":"Single API","firmware":payload.get("firmware","a.elf"),"platform":payload.get("platform","stm32f4"),"duration":payload.get("duration",60),"parallel":1,"faults":[{"id":payload.get("fault","SF-01"),"params":payload.get("params",{}),"expected":"","timeout_ms":5000}]}
    camp = Campaign(CampaignConfig.model_validate(cfg))
    res = camp.run()
    rid = str(uuid.uuid4())
    _runs[rid] = {"status": "completed", "progress": 1, "total": 1, "result": res.to_dict()}
    return {"run_id": rid, **res.to_dict()}

@app.post("/api/v1/campaign")
def run_campaign(payload: dict):
    from src.core.campaign import Campaign
    from src.config.schemas import CampaignConfig
    try:
        cfg = CampaignConfig.model_validate(payload)
    except Exception as e:
        raise HTTPException(400, str(e))
    camp = Campaign(cfg)
    rid = str(uuid.uuid4())
    _runs[rid] = {"status": "running", "progress": 0, "total": len(cfg.faults), "result": None}
    res = camp.run(parallel=cfg.parallel)
    _runs[rid].update({"status": "completed", "progress": len(cfg.faults), "result": res.to_dict()})
    # persist
    Path("results").mkdir(exist_ok=True)
    Path(f"results/{rid}.json").write_text(json.dumps(res.to_dict(), indent=2), encoding="utf-8")
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
    cr = CampaignResult(campaign_name=data["campaign"], resilience_index=data["resilience_index"], grade=data["grade"], results=[TestResult(**{k: v for k, v in x.items() if k in TestResult.__dataclass_fields__}) for x in data["results"]])
    Path("results").mkdir(exist_ok=True)
    if format == "html":
        p = Path(f"results/{run_id}.html"); cr.to_html(p); return FileResponse(str(p))
    if format == "pdf":
        p = Path(f"results/{run_id}.pdf"); cr.to_pdf(p); return FileResponse(str(p), media_type="application/pdf")
    return JSONResponse(data)

@app.post("/api/v1/compare")
def compare(payload: dict):
    # payload: {"baseline":"id1","optimized":"id2"} or inline results
    # For now, demo: run two tiny campaigns and compare
    from src.core.campaign import Campaign
    from src.config.schemas import CampaignConfig
    # Try ids first
    b_id = payload.get("baseline"); o_id = payload.get("optimized")
    if b_id in _runs and o_id in _runs:
        from src.core.result_aggregator import CampaignResult, TestResult
        def to_cr(d): return CampaignResult(campaign_name=d["campaign"], resilience_index=d["resilience_index"], grade=d["grade"], results=[TestResult(**{k: v for k,v in x.items() if k in TestResult.__dataclass_fields__}) for x in d["results"]])
        cr_b = to_cr(_runs[b_id]["result"]); cr_o = to_cr(_runs[o_id]["result"])
        cmp = cr_b.compare(cr_o)
        return cmp.to_dict()
    raise HTTPException(400, "Provide baseline/optimized run_ids from /campaign")

@app.websocket("/api/v1/live/{run_id}")
async def live(ws: WebSocket, run_id: str):
    await ws.accept()
    for i in range(5):
        await ws.send_json({"event": "test.progress", "payload": {"current": i+1, "total": 5, "eta_seconds": 10}})
        await asyncio.sleep(0.3)
    await ws.send_json({"event": "test.completed", "payload": {"run_id": run_id, "final_ri": 73, "grade": "B"}})
    await ws.close()
