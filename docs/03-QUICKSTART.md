# 03 — Quickstart (10 Minutes)

> Goal: ELF → campaign → RI score → HTML report

## Prerequisites
Completed `02-INSTALL.md`. Renode 1.15+ (tested `1.16.1` `renode-docker/Dockerfile:8`) on PATH. For Robot integration, `renode/tests/requirements.txt` already installed via Docker; locally `pip install -r renode/tests/requirements.txt`.

## 1. Use Example Firmware (2 min)

```bash
# Example already in repo; build if needed
ls examples/sensor-firmware/build/sensor.elf
# If missing: arm-none-eabi-gcc build
cd examples/sensor-firmware && make
```

Fallback without toolchain: use prebuilt `examples/sensor-firmware/build/sensor.elf` (checked in).

## 2. Create Campaign YAML (2 min)

Create `my_first.yaml`:
```yaml
name: "Quickstart Sensor Check"
firmware: "examples/sensor-firmware/build/sensor.elf"
platform: "resources/platforms/stm32f4_discovery.repl"
duration: 30
parallel: 2
faults:
  - id: SF-01
    name: "Stuck-at"
    params: { value: 25.0, target: "i2c0.sensor0" }
    expected: "detect_stuck_sensor"
    timeout_ms: 5000
  - id: SF-02
    name: "Gaussian Noise"
    params: { std_dev: 2.5 }
    expected: "std_dev_filtered < 2.0"
    timeout_ms: 10000
scoring:
  weights: { detection: 0.4, recovery: 0.3, safety: 0.3 }
  thresholds: { grade_a: 90, grade_b: 70, grade_c: 50, grade_d: 30 }
```

Validate:
```bash
python -m src.config.validator my_first.yaml
```

## 3. Run — Choose One Path (3 min)

### CLI (headless)
```bash
renode-resilience campaign --config my_first.yaml --parallel 2 --output results/
renode-resilience report --results results/my_first.json --format html --output report.html
```

### Python SDK
```python
from renode_resilience import Campaign
campaign = Campaign.from_yaml("my_first.yaml")
results = campaign.run(parallel=2)
print(f"RI: {results.resilience_index}/100 Grade: {results.grade}")
results.to_html("report.html")
```

### Desktop GUI
1. `python -m src.main` → Welcome → New Project → Template `STM32 Sensor Validation`
2. Firmware Browse → `sensor.elf` → Platform `STM32F4 Discovery`
3. Fault selector check `Sensor Faults` → table shows SF-01/SF-02
4. Click **Run** → Test Runner progress `2/2`, console `[PASS] SF-01`
5. Auto-switch to Report Viewer → `Export HTML`

## 4. Read Results (2 min)

- **RI 90-100 A** Excellent, 70-89 B Good, 50-69 C Marginal, 30-49 D Poor, <30 F Fail — see `08-RESILIENCE_INDEX.md`.
- Console: `[PASS] SF-01 detect 23ms recover 45ms RI 100` vs `[FAIL] SF-02 RI 40`.
- Open `report.html` or `results/my_first.json` for evidence.

## 5. Next Steps (1 min)

- Add more faults: see `06-FAULT_CATALOG.md` IDs `TF-01` (Deadline Miss) etc.
- Full workflow `04-USER_GUIDE.md`, comparison `results/baseline.json vs optimized` → `renode-resilience compare`.
- If fail: `18-TROUBLESHOOTING.md` (Renode not starting? Port 1234 busy?).
