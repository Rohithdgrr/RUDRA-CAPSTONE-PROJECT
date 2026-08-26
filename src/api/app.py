"""FastAPI stub."""
from fastapi import FastAPI

app = FastAPI(title="RenodeResilience API", version="1.0.0")

@app.get("/api/v1/faults")
def list_faults():
    from src.core.fault_injector import FAULT_CATALOG
    return list(FAULT_CATALOG.keys())

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
    return res.to_dict()
