# 13 — REST & WebSocket API (FastAPI)

> **Server:** `uvicorn src.api.app:app --port 8000` | Swagger at `/docs`

## Base URL

`http://localhost:8000/api/v1`

## REST Endpoints

| Method | Endpoint | Body / Query | Response | Description |
|--------|----------|--------------|----------|-------------|
| POST | `/run` | `{"firmware":"path","fault":"SF-01","duration":60,"params":{}}` | `TestResult` | Single fault test |
| POST | `/campaign` | `CampaignConfig` YAML/JSON (`05-CAMPAIGN_SCHEMA.md`) | `{"run_id":"uuid","status":"queued"}` | Full campaign |
| GET | `/status/{run_id}` | — | `{"status":"running","progress":12,"total":27}` | Poll status |
| GET | `/result/{run_id}` | — | `Result` JSON (`10-REPORT_SPEC.md`) | Get results |
| GET | `/report/{run_id}?format=html|pdf|json` | query `format` | File download | Generate report |
| POST | `/compare` | `{"baseline":"id1","optimized":"id2"}` | `ComparisonReport` | Side-by-side |
| GET | `/faults` | — | `Fault[]` 27 items (`06-FAULT_CATALOG.md`) | List faults |
| GET | `/platforms` | — | `["stm32f4","nrf52840","riscv_hifive1"]` | List platforms |

## Examples

```bash
# Run single
curl -X POST localhost:8000/api/v1/run \
  -H "Content-Type: application/json" \
  -d '{"firmware":"examples/sensor-firmware/build/sensor.elf","fault":"SF-01","duration":60}'

# Campaign from YAML file
curl -X POST localhost:8000/api/v1/campaign \
  -H "Content-Type: application/yaml" --data-binary @campaign.yaml

# Status
curl localhost:8000/api/v1/status/550e8400-e29b-41d4-a716-446655440000

# Report PDF
curl "localhost:8000/api/v1/report/550e8400...?format=pdf" --output report.pdf

# Compare
curl -X POST localhost:8000/api/v1/compare \
  -d '{"baseline":"id1","optimized":"id2"}'
```

## WebSocket Live Stream

`WS /api/v1/live/{run_id}` — subscribe to campaign progress.

Events:
| Event | Payload |
|-------|---------|
| `test.started` | `{"fault_id":"SF-01","timestamp":"2026-08-26T...Z"}` |
| `test.progress` | `{"current":12,"total":27,"eta_seconds":480}` |
| `test.result` | `TestResult` object |
| `test.completed` | `{"run_id":"...","final_ri":73,"grade":"B"}` |

JS client:
```js
const ws = new WebSocket("ws://localhost:8000/api/v1/live/"+run_id);
ws.onmessage = e => {
  const msg = JSON.parse(e.data);
  if(msg.event==="test.progress") updateProgress(msg.payload);
};
```

Python:
```python
import websockets, asyncio, json
async def stream():
    async with websockets.connect(f"ws://localhost:8000/api/v1/live/{run_id}") as ws:
        async for msg in ws:
            print(json.loads(msg))
```

## Auth & Security

- Local-only by default; no cloud upload (`16-SECURITY.md`).
- Optional `Authorization: Bearer <token>` if `src/config/defaults.py:api_token` set; read-only tokens for CI.
- CORS: allow `localhost:*` only.

## Error Codes

`400` ValidationError (bad Campaign YAML), `404` run_id not found, `503` Renode not running, `422` unknown fault ID.

## Code Map

- Router: `src/api/app.py` (FastAPI)
- Runner bridge: `src/core/test_runner.py` (same engine as GUI/CLI)
- Report: `src/core/report_generator.py`

## OpenAPI

Auto-generated at `http://localhost:8000/docs` (Swagger) and `/openapi.json`.
