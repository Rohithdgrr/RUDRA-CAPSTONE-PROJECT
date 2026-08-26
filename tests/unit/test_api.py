from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_platforms():
    r = client.get("/api/v1/platforms")
    assert r.status_code == 200
    assert "stm32f4" in r.json()

def test_faults():
    r = client.get("/api/v1/faults")
    assert r.status_code == 200
    assert len(r.json()) == 27

def test_run_single():
    r = client.post("/api/v1/run", json={"firmware": "a.elf", "fault": "SF-01"})
    assert r.status_code == 200
    data = r.json()
    assert "resilience_index" in data

def test_campaign_flow():
    payload = {
        "name": "API Test",
        "firmware": "examples/sensor-firmware/build/sensor.elf",
        "platform": "resources/platforms/stm32f4_discovery.repl",
        "duration": 10,
        "parallel": 1,
        "faults": [{"id": "SF-01", "params": {}, "expected": "", "timeout_ms": 1000}]
    }
    r = client.post("/api/v1/campaign", json=payload)
    assert r.status_code == 200
    rid = r.json()["run_id"]
    s = client.get(f"/api/v1/status/{rid}")
    assert s.json()["status"] == "completed"
    res = client.get(f"/api/v1/result/{rid}")
    assert res.json()["campaign"] == "API Test"
