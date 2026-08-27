# 05 — Campaign Schema

> **Files:** `src/core/campaign.py`, `src/config/schemas.py`, `src/config/validator.py` | Example `README.md:633-671`

## 1. Top-Level YAML

```yaml
name: "Sensor Suite Validation"          # str, required, 3-64 chars
description: "Validate temp sensor"     # str, optional
firmware: "examples/sensor-firmware/build/sensor.elf"  # Path, must exist, ELF magic
platform: "resources/platforms/stm32f4_discovery.repl" # Path or enum: stm32f4/nRF52840/riscv_hifive1
duration: 60                            # int seconds per test, 1-3600, default 60
parallel: 4                             # int workers 1-8, default 1 sequential
faults: [...]                           # list[Fault], 1-27 items
scoring: { weights: {...}, thresholds: {...} }  # optional, defaults 0.4/0.3/0.3
```

Pydantic validation: `Campaign.from_yaml(path)` → `ValidationError` on miss.

## 2. Fault Entry

```yaml
faults:
  - id: SF-01                           # str, enum of 27 IDs (see 06-FAULT_CATALOG)
    name: "Stuck-at"                    # str, human readable, must match catalog
    params: { value: 25.0, target: "i2c0.sensor0" }  # dict, schema per fault
    expected: "detect_stuck_sensor"     # str, rule expression or function name
    timeout_ms: 5000                    # int, 100-60000, detection window
    severity: HIGH                      # enum LOW|MEDIUM|HIGH|CRITICAL (UI only)
```

- `expected` is evaluated by `src/core/result_aggregator.py`: function exists in harness OR expression `std_dev_filtered < 2.0` → polled via `RenodeBridge.read_peripheral()`.
- Unknown `id` → `validator.py` error `Unknown fault ID 'XX-99'`.

## 3. Scoring

```yaml
scoring:
  weights:
    detection: 0.4   # float 0-1, sum must ==1.0
    recovery: 0.3
    safety: 0.3
  thresholds:
    grade_a: 90      # must be > grade_b > grade_c > grade_d
    grade_b: 70
    grade_c: 50
    grade_d: 30
    # grade_f implicit <30
```

Validation rules:
- `weights`: `detection + recovery + safety` must sum to 1.0 (tolerance 1e-6)
- `thresholds`: `grade_a > grade_b > grade_c > grade_d` enforced by `@model_validator`
- `faults`: `min_length=1`, `max_length=27`, unique IDs required

Maps to `src/core/resilience_index.py`: `RI=(D*0.4)+(Rec*0.3)+(S*0.3)` normalized 0-100.

## 4. Full Example (3 faults)

```yaml
name: "Sensor Suite Validation"
description: "Validate temperature sensor fault handling"
firmware: "examples/sensor-firmware/build/sensor.elf"
platform: "resources/platforms/stm32f4_discovery.repl"
duration: 60
parallel: 4
faults:
  - id: SF-01
    params: { value: 25.0, target: "i2c0.sensor0" }
    expected: "detect_stuck_sensor"
    timeout_ms: 5000
  - id: SF-02
    params: { std_dev: 2.5 }
    expected: "std_dev_filtered < 2.0"
    timeout_ms: 10000
  - id: TF-01
    params: { delay_ms: 100, target: "control_loop" }
    expected: "watchdog_reset"
    timeout_ms: 200
scoring:
  weights: { detection: 0.4, recovery: 0.3, safety: 0.3 }
  thresholds: { grade_a: 90, grade_b: 70, grade_c: 50, grade_d: 30 }
```

## 5. Python SDK Equivalent

```python
from renode_resilience import Campaign, Fault
from pathlib import Path
campaign = Campaign(
    name="Sensor Suite Validation",
    firmware=Path("examples/sensor-firmware/build/sensor.elf"),
    platform=Path("resources/platforms/stm32f4_discovery.repl"),
    duration=60, parallel=4,
    faults=[Fault(id="SF-01", params={"value":25.0}, expected="detect_stuck_sensor", timeout_ms=5000)]
)
campaign.to_yaml("out.yaml")
```

## 6. Validation Errors (Common)

| Error | Cause | Fix |
|-------|-------|-----|
| `firmware not found` | Path typo | Absolute or repo-relative |
| `weights sum !=1.0` | 0.4+0.3+0.2=0.9 | Adjust to 1.0 |
| `timeout_ms out of range` | 5 (too low) | 100-60000 |
| `duplicate fault id` | SF-01 twice | Unique per campaign |

## 7. Storage

- Campaigns: `campaigns/<name>.yaml` (gitignore `campaigns/private/` for secrets — none should be in YAML per `README.md:391`).
- Results: `results/campaign_YYYY-MM-DD.json` (used by `src/core/report_generator.py`).
