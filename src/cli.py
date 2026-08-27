"""Typer CLI — renode-resilience."""

import json
import re
from pathlib import Path

import typer

from src.core.campaign import Campaign

app = typer.Typer(help="RenodeResilience CLI")

_SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9._-]+")


def _safe_filename(name: str) -> str:
    """Sanitize campaign name for filesystem: no traversal, only safe chars."""
    # Remove path separators and parent refs
    name = name.replace("/", "_").replace("\\", "_").replace("..", "_")
    name = _SAFE_NAME_RE.sub("_", name).strip("._")
    return name or "campaign"

def _check_file(path: str, label: str):
    """Warn if file does not exist; error only in --renode mode is handled by caller."""
    p = Path(path)
    if not p.exists():
        typer.echo(f"Warning: {label} not found: {path} (simulation mode will still run)", err=True)
    return p.exists()


@app.command()
def run(
    firmware: str = typer.Option(..., help="ELF path"),
    platform: str = typer.Option(..., help="REPL"),
    fault: str = typer.Option(..., help="Fault ID"),
    duration: int = typer.Option(60),
    target: str = typer.Option(None),
    output: str = typer.Option(None),
    renode: bool = typer.Option(
        False, "--renode", help="Use real Renode emulation (requires renode on PATH)"
    ),
    renode_bin: str = typer.Option("renode", help="Renode binary"),
    renode_port: int = typer.Option(1234, help="Renode monitor port"),
):
    # Validate fault ID early to give friendly error before campaign creation
    from src.config.schemas import VALID_FAULT_IDS
    if fault not in VALID_FAULT_IDS:
        typer.echo(f"Error: unknown fault ID '{fault}'. Valid: {VALID_FAULT_IDS}", err=True)
        raise typer.Exit(code=2)
    if renode:
        # In renode mode, firmware/platform must exist
        for p, lbl in [(firmware, "firmware"), (platform, "platform")]:
            if not Path(p).exists():
                typer.echo(f"Error: {lbl} not found: {p} (required for --renode)", err=True)
                raise typer.Exit(code=2)
    else:
        _check_file(firmware, "firmware")
        _check_file(platform, "platform")
    cfg = {
        "name": "Single",
        "firmware": firmware,
        "platform": platform,
        "duration": duration,
        "parallel": 1,
        "faults": [
            {
                "id": fault,
                "params": {"target": target} if target else {},
                "expected": "",
                "timeout_ms": 5000,
            }
        ],
    }
    from src.config.schemas import CampaignConfig

    camp = Campaign(CampaignConfig.model_validate(cfg))
    res = camp.run(use_renode=renode, renode_bin=renode_bin, renode_port=renode_port)
    typer.echo(
        f"RI {res.resilience_index} Grade {res.grade} {res.results[0].status} [{'renode' if renode else 'sim'}]"
    )
    if output:
        out_path = Path(output)
        # Sanitize output path traversal
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        res.to_json(str(out_path))
    raise typer.Exit(code=0 if res.results[0].status == "PASS" else 1)


@app.command()
def campaign(
    config: str = typer.Option(..., "--config"),
    parallel: int = typer.Option(1),
    output: str = typer.Option("results"),
    renode: bool = typer.Option(False, "--renode", help="Use real Renode emulation"),
    renode_bin: str = typer.Option("renode", help="Renode binary"),
    renode_port: int = typer.Option(1234, help="Renode monitor port"),
):
    cfg_path = Path(config)
    if not cfg_path.exists():
        typer.echo(f"Error: config not found: {config}", err=True)
        raise typer.Exit(code=2)
    camp = Campaign.from_yaml(config)
    # In renode mode, validate platform/firmware exist
    if renode:
        for p, lbl in [(camp.config.firmware, "firmware"), (camp.config.platform, "platform")]:
            if not Path(p).exists():
                typer.echo(f"Error: {lbl} not found: {p} (required for --renode)", err=True)
                raise typer.Exit(code=2)
    res = camp.run(
        parallel=parallel, use_renode=renode, renode_bin=renode_bin, renode_port=renode_port
    )
    out_dir = Path(output)
    out_dir.mkdir(parents=True, exist_ok=True)
    # Sanitize filename to avoid traversal via campaign name
    safe_name = _safe_filename(camp.config.name)
    out = out_dir / f"{safe_name}.json"
    # Ensure out is inside out_dir (no traversal)
    try:
        out.resolve().relative_to(out_dir.resolve())
    except ValueError:
        typer.echo(f"Error: campaign name would escape output dir: {camp.config.name}", err=True)
        raise typer.Exit(code=2)
    res.to_json(out)
    mode = "renode" if renode else "sim"
    typer.echo(f"Done {res.resilience_index}/100 Grade {res.grade} [{mode}] -> {out}")


@app.command()
def report(
    results: str = typer.Option(..., "--results"),
    format: str = typer.Option("html", "--format"),
    output: str = typer.Option("report.html", "--output"),
):
    data = json.loads(Path(results).read_text(encoding="utf-8"))
    from src.core.result_aggregator import CampaignResult, TestResult

    cr = CampaignResult(
        campaign_name=data["campaign"],
        resilience_index=data["resilience_index"],
        grade=data["grade"],
        results=[
            TestResult(**{k: v for k, v in x.items() if k in TestResult.__dataclass_fields__})
            for x in data["results"]
        ],
    )
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    if format == "html":
        cr.to_html(output)
    elif format == "pdf":
        cr.to_pdf(output)
    elif format == "json":
        cr.to_json(output)
    elif format == "junit":
        cr.to_junit(output)
    else:
        cr.to_html(output)
    typer.echo(
        f"Report {data.get('campaign')} {format} -> {output} RI {cr.resilience_index} Grade {cr.grade}"
    )


@app.command()
def compare(
    baseline: str = typer.Option(...),
    optimized: str = typer.Option(...),
    output: str = typer.Option("comparison.html"),
):
    import json

    b = json.loads(Path(baseline).read_text(encoding="utf-8"))
    o = json.loads(Path(optimized).read_text(encoding="utf-8"))
    from src.core.result_aggregator import CampaignResult, TestResult

    def to_cr(d):
        return CampaignResult(
            campaign_name=d["campaign"],
            resilience_index=d["resilience_index"],
            grade=d["grade"],
            results=[
                TestResult(**{k: v for k, v in x.items() if k in TestResult.__dataclass_fields__})
                for x in d["results"]
            ],
        )

    cr_b, cr_o = to_cr(b), to_cr(o)
    cmp = cr_b.compare(cr_o)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    cmp.to_html(output)
    typer.echo(f"Comparison delta {cmp.delta_ri:+d} (+{cmp.improvement_pct}%) -> {output}")
    for d in cmp.deltas:
        typer.echo(f"  {d['fault_id']}: {d['baseline']} -> {d['optimized']} ({d['delta']:+d})")


@app.command()
def faults():
    from src.core.fault_injector import FAULT_CATALOG

    for k in FAULT_CATALOG:
        typer.echo(k)


@app.command()
def platforms():
    from src.config.defaults import SUPPORTED_PLATFORMS

    for p in SUPPORTED_PLATFORMS:
        typer.echo(p)


if __name__ == "__main__":
    app()
