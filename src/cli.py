"""Typer CLI — renode-resilience."""
import typer
from pathlib import Path
import json
from src.core.campaign import Campaign

app = typer.Typer(help="RenodeResilience CLI")

@app.command()
def run(firmware: str = typer.Option(..., help="ELF path"), platform: str = typer.Option(..., help="REPL"), fault: str = typer.Option(..., help="Fault ID"), duration: int = typer.Option(60), target: str = typer.Option(None), output: str = typer.Option(None)):
    cfg = {"name":"Single","firmware":firmware,"platform":platform,"duration":duration,"parallel":1,"faults":[{"id":fault,"params":{"target":target} if target else {},"expected":"","timeout_ms":5000}]}
    from src.config.schemas import CampaignConfig
    camp = Campaign(CampaignConfig.model_validate(cfg))
    res = camp.run()
    typer.echo(f"RI {res.resilience_index} Grade {res.grade} {res.results[0].status}")
    if output:
        res.to_json(output)
    raise typer.Exit(code=0 if res.results[0].status=="PASS" else 1)

@app.command()
def campaign(config: str = typer.Option(..., "--config"), parallel: int = typer.Option(1), output: str = typer.Option("results")):
    camp = Campaign.from_yaml(config)
    res = camp.run(parallel=parallel)
    Path(output).mkdir(parents=True, exist_ok=True)
    out = Path(output) / f"{camp.config.name.replace(' ','_')}.json"
    res.to_json(out)
    typer.echo(f"Done {res.resilience_index}/100 Grade {res.grade} -> {out}")

@app.command()
def report(results: str = typer.Option(..., "--results"), format: str = typer.Option("html", "--format"), output: str = typer.Option("report.html", "--output")):
    data = json.loads(Path(results).read_text(encoding="utf-8"))
    typer.echo(f"Report stub: {data.get('campaign')} {format} -> {output}")

@app.command()
def compare(baseline: str = typer.Option(...), optimized: str = typer.Option(...), output: str = typer.Option("comparison.html")):
    typer.echo(f"Compare {baseline} vs {optimized} -> {output}")

@app.command()
def faults():
    from src.core.fault_injector import FAULT_CATALOG
    for k in FAULT_CATALOG: typer.echo(k)

@app.command()
def platforms():
    from src.config.defaults import SUPPORTED_PLATFORMS
    for p in SUPPORTED_PLATFORMS: typer.echo(p)

if __name__ == "__main__":
    app()
