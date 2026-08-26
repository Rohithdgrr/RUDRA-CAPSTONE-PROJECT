# 08 — Resilience Index (RI)

> **Formula:** `RI = (D×0.4)+(Rec×0.3)+(S×0.3)` normalized 0-100 | **File:** `src/core/resilience_index.py` | PRD `README.md:52-53`

## 1. Components

| Symbol | Name | Meaning | Measurement |
|--------|------|---------|-------------|
| D | Detection | Did firmware detect fault within `timeout_ms`? | `bool` → 100 if yes / 0 if no; or graded by latency `100*(1 - latency/timeout)` |
| Rec | Recovery | Did firmware recover to nominal within observation window? | `bool` + recovery time; `check_recovery()` |
| S | Safety | Did system stay in safe state (no unsafe actuation/memory corruption)? | `bool` `_check_safety()` |

Each 0-100 before weighting. Example `_calculate_ri()` in `desktop-application.md:533`:
```python
def _calculate_ri(detected, recovered, safe, w_d=0.4, w_r=0.3, w_s=0.3):
    D = 100 if detected else 0
    Rec = 100 if recovered else 0
    S = 100 if safe else 0
    return round(D*w_d + Rec*w_r + S*w_s)
```

Graded variant (optional): D = `max(0, 100 - 100*latency/timeout)` for partial credit.

## 2. Worked Examples

| Scenario | D | Rec | S | RI | Grade |
|----------|---|-----|---|----|-------|
| Perfect: SF-01 detect 23ms, recover 45ms, safe | 100 | 100 | 100 | 100 | A |
| Fail detect (SF-03 no outlier) | 0 | 0 | 100 | 30 | D* | 
| Detect but no recover, safe | 100 | 0 | 100 | 70 | B |
| Detect/recover but unsafe (TF-01 unsafe actuation) | 100 | 100 | 0 | 70 | B? Actually 70 but safety fail → Diagnosis flags CRITICAL |
| All fail | 0 | 0 | 0 | 0 | F |

*Note: single test RI vs campaign avg — campaign RI = mean of per-fault RIs.

## 3. Campaign Aggregation

```
campaign_RI = mean(per_fault_RI for fault in campaign.faults)
pass_count = count(RI >= threshold_B)
Grade thresholds from campaign.yaml scoring.thresholds:
  A ≥90, B ≥70, C ≥50, D ≥30, F <30  (defaults, configurable)
```

Stored in `ResultAggregator`: `pass_count/total_count`, `failures: list[TestResult]`, `resilience_index`, `grade`.

## 4. Live Calculation

`TestRunner._run_single_test()` → `detected = _wait_for_detection(fault, timeout=5.0)` → `recovered = _check_recovery()` → `safe = _check_safety()` → `TestResult(resilience_index=...)` → signal `result` → GUI table `RI` col + PyQtGraph line chart `RI over time`.

## 5. Configuring Weights

Weights sum to 1.0 (`05-CAMPAIGN_SCHEMA.md`). Defaults `0.4/0.3/0.3` emphasize detection. For safety-critical (ISO 26262 ASIL-D) recommend `0.3/0.2/0.5` to weight safety higher — see `09-DIAGNOSIS_ENGINE.md` mapping.

Overridable per-campaign via:
```yaml
scoring: { weights: { detection: 0.3, recovery: 0.2, safety: 0.5 } }
```

## 6. Export

`ReportGenerator` includes RI in all exports: HTML gauge (circular progress), PDF summary card `Overall RI: 73/100 Grade: B`, JSON `{"resilience_index":73,"grade":"B"}`, JUnit `properties`.

## 7. Interpreting Grades

| Grade | Range | Action |
|-------|-------|--------|
| A | 90-100 | Ship — excellent resilience |
| B | 70-89 | Ship with notes — target ≥70 (PRD objective 7) |
| C | 50-69 | Marginal — fix critical findings |
| D | 30-49 | Poor — requires rework |
| F | 0-29 | Fail — unsafe |

Color mapping `15-STYLE_GUIDE.md`: A `#2ECC71`, B `#3498DB`, C `#F1C40F`, D `#E67E22`, F `#E74C3C`.
