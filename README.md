# RenodeResilience

[![CI](https://github.com/Rohithdgrr/RUDRA-CAPSTONE-PROJECT/actions/workflows/ci.yml/badge.svg)](https://github.com/Rohithdgrr/RUDRA-CAPSTONE-PROJECT/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![Renode 1.15+](https://img.shields.io/badge/renode-1.15%2B-green)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Automated fault-injection and resilience-testing framework for embedded firmware on Renode.
> Injects 27 hardware faults, scores firmware resilience (RI 0-100), and generates diagnosis reports.

---

## Quick Start

```bash
git clone https://github.com/Rohithdgrr/RUDRA-CAPSTONE-PROJECT.git
cd RUDRA-CAPSTONE-PROJECT
pip install -r requirements.txt

# Launch desktop app
python src/main.py

# Or use CLI
python -m src.cli campaign --config campaigns/sensor_suite.yaml
```

### Prerequisites

- **Python 3.11+**
- **Renode 1.15+** (on PATH)
- **PyQt6 6.6+**

---

## Features

| Feature | Description |
|---|---|
| **27 Fault Types** | Sensor (7), Timing (5), Communication (6), Memory (4), Power (3), GPIO (2) |
| **Resilience Index** | Quantitative 0-100 score: `RI = (Detection x 0.4) + (Recovery x 0.3) + (Safety x 0.3)` |
| **Grading** | A (90+), B (70+), C (50+), D (30+), F (<30) |
| **Diagnosis Engine** | Rule-based failure classification with fix recommendations |
| **3 Platforms** | STM32F4 Discovery, nRF52840 DK, HiFive1 RISC-V |
| **GUI** | PyQt6 desktop app with dark/light themes, live charts, sidebar navigation |
| **REST API** | FastAPI endpoints for headless/CI integration |
| **CLI** | Typer-based command-line interface |
| **Reports** | HTML, PDF, JSON, JUnit XML export |

---

## Screenshots

> **GUI Preview** — Dark theme with Welcome screen, Campaign Editor, Test Runner, and Report Viewer.
>
> Run `python src/main.py` to see the live application.

---

## Project Structure

```
src/
  main.py                    # GUI entry point
  main_window.py             # MainWindow + WelcomeScreen (5 screens)
  cli.py                     # Typer CLI
  core/
    renode_bridge.py         # Renode subprocess wrapper
    fault_injector.py        # 27 fault types
    campaign.py              # Campaign execution engine
    resilience_index.py      # RI calculator (0-100)
    result_aggregator.py     # Results + comparison
    diagnosis_engine.py      # Failure classification
    report_generator.py      # HTML/PDF/JSON reports
    test_runner.py           # QThread runner
  gui/
    widgets/                 # 12 PyQt6 widgets
    styles/                  # Dark + Light QSS themes
    utils/icons.py           # 20 vector icons
  api/app.py                 # FastAPI REST + WebSocket
  config/schemas.py          # Pydantic validation
campaigns/                   # YAML campaign configs
tests/unit/                  # 27 pytest tests
docs/                        # 22 documentation files
resources/platforms/         # .repl board definitions
```

---

## CLI Usage

```bash
# Run single fault test
python -m src.cli run --firmware path/to/firmware.elf --fault SF-01

# Run full campaign
python -m src.cli campaign --config campaigns/sensor_suite.yaml --parallel 4

# Generate report
python -m src.cli report --results results/campaign.json --format pdf

# Compare two runs
python -m src.cli compare --baseline results/a.json --optimized results/b.json

# List all fault types
python -m src.cli faults

# List supported platforms
python -m src.cli platforms
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/run` | Run single fault test |
| `POST` | `/api/v1/campaign` | Run full campaign |
| `GET` | `/api/v1/status/{run_id}` | Check test status |
| `GET` | `/api/v1/result/{run_id}` | Get results |
| `GET` | `/api/v1/report/{run_id}?format=html\|pdf\|json` | Download report |
| `POST` | `/api/v1/compare` | Compare two runs |
| `GET` | `/api/v1/faults` | List 27 fault types |
| `GET` | `/api/v1/platforms` | List supported platforms |
| `WS` | `/api/v1/live/{run_id}` | Live progress stream |
| `POST` | `/api/v1/upload/firmware` | Upload and validate ELF |

Start API server: `uvicorn src.api.app:app --reload`

---

## Campaign YAML Example

```yaml
name: "Sensor Suite Validation"
firmware: "examples/sensor-firmware/build/sensor.elf"
platform: "platforms/stm32f4_discovery.repl"
duration: 60
parallel: 4

faults:
  - id: SF-01
    params: { value: 25.0, target: "i2c0.sensor0" }
    expected: "detect_stuck_sensor"
    timeout_ms: 5000

  - id: TF-01
    params: { delay_ms: 100 }
    expected: "watchdog_reset"
    timeout_ms: 200

scoring:
  weights: { detection: 0.4, recovery: 0.3, safety: 0.3 }
  thresholds: { grade_a: 90, grade_b: 70, grade_c: 50, grade_d: 30 }
```

---

## Testing

```bash
# Run all 27 unit tests
python -m pytest tests/unit/ -v

# Run with coverage
python -m pytest tests/unit/ --cov=src --cov-report=term
```

---

## Fault Taxonomy

| Category | Types | Examples |
|---|---|---|
| **Sensor** | 7 | SF-01 Stuck-at, SF-02 Gaussian Noise, SF-03 Impulse Noise, SF-04 Drift, SF-05 Bias, SF-06 Missing Samples, SF-07 Outliers |
| **Timing** | 5 | TF-01 Deadline Miss, TF-02 Clock Skew, TF-03 Interrupt Storm, TF-04 Watchdog Timeout, TF-05 Race Condition |
| **Communication** | 6 | CF-01 Packet Loss, CF-02 Latency Spike, CF-03 Bus Flooding, CF-04 Frame Corruption, CF-05 Bus-Off, CF-06 Arbitration Loss |
| **Memory** | 4 | MF-01 Stack Overflow, MF-02 Heap Corruption, MF-03 Flash Bit-Flip, MF-04 ECC Error |
| **Power** | 3 | PF-01 Brownout, PF-02 Power Glitch, PF-03 Sleep Failure |
| **GPIO** | 2 | GF-01 Pin Float, GF-02 ADC Saturation |

---

## Documentation

Full documentation in [`docs/`](docs/00-INDEX.md):

| Doc | Topic |
|---|---|
| [00-INDEX](docs/00-INDEX.md) | Documentation index |
| [01-ARCHITECTURE](docs/01-ARCHITECTURE.md) | System architecture |
| [02-FAULT_TAXONOMY](docs/02-FAULT_TAXONOMY.md) | 27 fault types |
| [05-CAMPAIGN_SCHEMA](docs/05-CAMPAIGN_SCHEMA.md) | YAML schema |
| [08-RI_FORMULA](docs/08-RI_FORMULA.md) | Resilience Index math |
| [13-API_REST](docs/13-API_REST.md) | REST API spec |
| [14-GUI_SPEC](docs/14-GUI_SPEC.md) | GUI design |
| [17-TESTING](docs/17-TESTING.md) | Test strategy |
| [PRD](docs/00-PRD.md) | Full product requirements |

---

## Tech Stack

| Layer | Technology |
|---|---|
| GUI | PyQt6 6.6+, QSS dark/light themes |
| Core | Python 3.11+, Pydantic 2, PyYAML |
| Emulation | Renode 1.15+ (subprocess bridge) |
| API | FastAPI, WebSocket, uvicorn |
| CLI | Typer |
| Reports | Jinja2, WeasyPrint (PDF) |
| Charts | PyQtGraph |
| Tests | pytest (27 unit tests) |
| CI | GitHub Actions |
| Packaging | PyInstaller 6.22+ |

---

## License

MIT License. See [LICENSE](LICENSE).

---

## Acknowledgments

- [Renode](https://renode.io/) — Open-source hardware emulation framework
- [Antmicro](https://antmicro.com/) — Renode creators
- [PyQt6](https://www.riverbankcomputing.com/) — Python Qt bindings
