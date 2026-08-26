# 09 — Diagnosis Engine

> **File:** `src/core/diagnosis_engine.py` | Rule-based v1.0, ML planned v1.1

## 1. Purpose

Classify each `TestResult` failure and emit `root_cause` + `recommendations[]` with code examples. Feeds `Report Viewer Critical Findings`.

## 2. Inputs

- `TestResult`: `fault_id`, `detected`, `recovered`, `safe`, `latency_ms`, `logs`, optional stack trace from `RenodeBridge.read_peripheral()`.
- `Campaign` weights/thresholds, `CampaignResult` aggregates.

## 3. Rule Set (Examples)

| Fault | Failure Pattern | Classification | Recommendation |
|-------|-----------------|----------------|----------------|
| SF-01 Stuck-at | `detected==False` | Missing stuck-value check | Add `if abs(value - last)>eps for N samples → flag; median filter 3-sample` |
| SF-03 Impulse | `detected==False` latency `--` | No outlier filter | `median = sorted(window)[1]; if abs(x-median)>3*sigma → discard` |
| TF-01 Deadline | `detected True but safe==False` | Unsafe deadline miss | `Add task timeout + watchdog: wdg_timeout 50ms (was 10ms), yield points in control loop` |
| CF-03 Bus Flood | `anomaly threshold exceeded` | Threshold too high | `Lower anomaly threshold to 50Hz (was 200Hz)` |
| MF-01 Stack Overflow | `safe==False` | No stack guard | `Increase stack 512→1024, add canary, -fstack-protector` |

Rules are `if fault_id and not detected → diag`; see `src/core/diagnosis_engine.py:diagnose()`.

## 4. Output Schema

```python
@dataclass
class Diagnosis:
    fault_id: str
    root_cause: str          # e.g. "Impulse noise not detected"
    category: str            # "sensor_filter" | "timing" | "safety"
    severity: str            # CRITICAL | WARNING | INFO
    recommendations: list[str]  # code snippets + param tweaks
    iso_mapping: str | None    # e.g. "ISO26262-6 7.4.3"
```

Example JSON in `10-REPORT_SPEC.md`.

## 5. ISO / DO-178C Mapping

| Standard | Clause | Fault Example |
|----------|--------|---------------|
| ISO 26262-4 7.4.3 | Fault handling | SF-01 → requires detection within FTTI |
| ISO 26262-6 7.4 | Software safety | TF-01 watchdog |
| DO-178C Level A | Robustness | MF-01 stack overflow |

Checklist template `resources/templates/iso26262_checklist.html`.

## 6. Usage

```python
from renode_resilience import Campaign
results = Campaign.from_yaml("campaign.yaml").run()
for f in results.failures:
    diag = f.diagnose()
    print(diag.root_cause)
    for r in diag.recommendations: print(f" → {r}")
```

GUI: Report Viewer → Critical Findings → expands `Recommendation: Add median filter (3-sample)`.

## 7. Future (v1.1)

- `scikit-learn` classifier trained on accumulated campaigns (`README.md:761`).
- Plugin `FaultInjector.register()` hooks for custom diagnosis rules.

## 8. Adding Rules

Edit `src/core/diagnosis_engine.py`:
```python
RULES.append(Rule(fault="SF-03", condition=lambda r: not r.detected,
                  cause="Impulse noise not detected",
                  fix="Add median filter ..."))
```
Add test in `tests/unit/test_diagnosis.py` → maintain 90% coverage (`17-TESTING.md`).
