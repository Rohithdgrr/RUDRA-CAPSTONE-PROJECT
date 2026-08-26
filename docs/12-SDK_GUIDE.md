# 12 — Python SDK Guide

> **Import:** `from renode_resilience import Campaign, FaultInjector` | `README.md:286-306`

## Install

```bash
pip install -e .
# or pip install renode-resilience (once published)
```

Requires `02-INSTALL.md` deps.

## Quick Start

```python
from pathlib import Path
from renode_resilience import Campaign

campaign = Campaign.from_yaml("campaign.yaml")
results = campaign.run(parallel=4)  # blocking; uses QThreadPool headless fallback

print(f"RI: {results.resilience_index}/100")
print(f"Grade: {results.grade}")  # A-F
print(f"Pass: {results.pass_count}/{results.total_count}")

for f in results.failures:
    diag = f.diagnose()
    print(f"{f.fault_id}: {diag.root_cause}")
    for rec in diag.recommendations:
        print(f"  → {rec}")

results.to_html(Path("report.html"))
results.to_pdf(Path("report.pdf"))
results.to_json(Path("report.json"))
results.to_junit(Path("junit.xml"))
```

## Campaign Construction

### From YAML (recommended)

```python
campaign = Campaign.from_yaml("campaigns/sensor_suite.yaml")
# Validates via src/config/schemas.py Pydantic; raises ValidationError
campaign.to_yaml("out.yaml")  # round-trip
```

### Programmatic

```python
from renode_resilience import Campaign, Fault
from pathlib import Path

campaign = Campaign(
    name="Sensor Suite Validation",
    firmware=Path("examples/sensor-firmware/build/sensor.elf"),
    platform=Path("resources/platforms/stm32f4_discovery.repl"),
    duration=60, parallel=4,
    faults=[
        Fault(id="SF-01", params={"value":25.0, "target":"i2c0.sensor0"},
              expected="detect_stuck_sensor", timeout_ms=5000),
        Fault(id="SF-02", params={"std_dev":2.5},
              expected="std_dev_filtered < 2.0", timeout_ms=10000),
    ],
    scoring={"weights":{"detection":0.4,"recovery":0.3,"safety":0.3}}
)
campaign.validate()  # explicit
```

## Results API

```python
results.resilience_index  # int 0-100
results.grade             # "A".."F"
results.pass_count, results.fail_count, results.warning_count
results.total_count
results.failures          # list[TestResult] where status != PASS
results.results           # list[TestResult] all
results.diagnose()        # aggregated Diagnosis
results.to_dict()         # JSON-serializable
```

`TestResult` fields: `fault_id`, `status` (PASS/FAIL/WARNING), `detected`, `recovered`, `safe`, `latency_ms`, `recovery_ms`, `resilience_index`, `logs`, `diagnosis`.

## FaultInjector Low-Level

```python
from renode_resilience import FaultInjector, RenodeBridge
from pathlib import Path

bridge = RenodeBridge()
bridge.start(Path("resources/platforms/stm32f4_discovery.repl"),  # vendored `renode/platforms/cpus/stm32f4.repl:1`
             Path("examples/sensor-firmware/build/sensor.elf"))

injector = FaultInjector(bridge)
injector.inject("SF-01", {"value":25.0, "target":"i2c0.sensor0"})  # maps to sysbus WriteDoubleWord
value = bridge.read_peripheral("sysbus.i2c0.sensor0")
# Optional typed path: from pyrenode3 import RPath; RPath("sysbus.i2c0") via pyrenode3/src/pyrenode3/rpath.py:1607
bridge.stop()
```

## Async / Headless

```python
# Non-blocking with callback
def on_progress(cur, total): print(f"{cur}/{total}")
campaign.run(parallel=4, on_progress=on_progress, on_result=lambda r: print(r.fault_id))

# If GUI running, uses QThread; else fallback ThreadPoolExecutor
```

## Comparison

```python
baseline = Campaign.from_yaml("baseline.yaml").run()
optimized = Campaign.from_yaml("optimized.yaml").run()
cmp = baseline.compare(optimized)
print(f"Delta RI: {cmp.delta_ri} (+{cmp.improvement_pct}%)")
cmp.to_html("comparison.html")
```

## Error Handling

```python
from pydantic import ValidationError
try:
    c = Campaign.from_yaml("bad.yaml")
except ValidationError as e:
    print(e.errors())
# Renode errors: RenodeNotFound, MonitorTimeout(15s)
```

## Testing

See `17-TESTING.md`: `tests/unit/test_campaign.py` mocks `RenodeBridge` for fast SDK tests without Renode.

## Reference

Full API docs via `pdoc` or `README.md:286` — `src/core/{campaign,resilience_index,diagnosis_engine}.py`.
