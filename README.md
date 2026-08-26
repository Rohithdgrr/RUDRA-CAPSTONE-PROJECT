# 📋 RenodeResilience — Complete Product Requirements Document (PRD)

[![CI](https://github.com/Rohithdgrr/RUDRA-CAPSTONE-PROJECT/actions/workflows/ci.yml/badge.svg)](https://github.com/Rohithdgrr/RUDRA-CAPSTONE-PROJECT/actions/workflows/ci.yml) [![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml) [![Renode 1.16.1](https://img.shields.io/badge/renode-1.16.1-green)](renode-docker/Dockerfile) [![Docs](https://img.shields.io/badge/docs-22%20md-blue)](docs/00-INDEX.md) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Live Repo:** https://github.com/Rohithdgrr/RUDRA-CAPSTONE-PROJECT — `main` branch `b289d67` (v1.1) · Desktop `src/main.py` · CLI `renode-resilience` · API `uvicorn src.api.app:app`

---

## 1. Executive Summary

**Product Name:** RenodeResilience  
**Version:** v1.0.0  
**Type:** Desktop Application (PyQt6) + Headless Framework  
**License:** MIT (Open Source)

**Tagline:** *"Find firmware bugs before they find you in the field."*

**What It Is:** RenodeResilience is an automated fault-injection and resilience-testing framework built on top of Renode (the open-source hardware emulation platform). It injects 27 types of hardware faults into virtual embedded systems, measures firmware resilience quantitatively via a 0-100 Resilience Index, and generates actionable diagnosis reports with fix recommendations.

**Target Users:** Embedded firmware engineers, QA teams, safety-critical system developers, automotive (ISO 26262), aerospace (DO-178C), and IoT product teams.

---

## 2. Problem Statement

### 2.1 The $500M+ Recall Problem
Embedded firmware failures in the field cost manufacturers billions in recalls, liability, and reputation damage. Traditional testing methods have critical gaps:

| Problem | Impact |
|---|---|
| **Hardware-in-the-Loop (HIL) testing is expensive** | Physical fault injection rigs cost $50K-$200K per setup |
| **Unit tests don't catch hardware-fault scenarios** | Mocked sensors/timers don't behave like real failing hardware |
| **No quantitative resilience metric exists** | Teams say "it feels robust" but can't measure it |
| **Debugging field failures is reactive** | Bugs are found by customers, not before shipment |
| **Safety standards lack automated verification** | ISO 26262/DO-178C compliance is manual and error-prone |
| **Renode has no structured testing layer** | The emulator exists, but no framework automates fault campaigns on top of it |

### 2.2 Market Gap
No existing tool provides:
- A structured taxonomy of 27 injectable hardware faults
- A quantitative 0-100 Resilience Index for firmware
- Automated diagnosis with fix recommendations
- A desktop-native UI for embedded engineers (93% prefer local tools)

---

## 3. Aim & Objectives

### 3.1 Primary Aim
Build a desktop application and headless framework that automates hardware fault-injection testing for embedded firmware using Renode emulation, producing quantitative resilience scores and actionable reports.

### 3.2 Objectives
| # | Objective | Success Criteria |
|---|---|---|
| 1 | Integrate with Renode 1.15+ | Can start/stop/emulate STM32, nRF52, RISC-V |
| 2 | Implement 27 fault types | All faults injectable via GUI and API |
| 3 | Compute Resilience Index (0-100) | RI = (D×0.4) + (Rec×0.3) + (S×0.3) |
| 4 | Generate diagnosis reports | HTML, PDF, JSON, JUnit XML outputs |
| 5 | Provide desktop GUI | PyQt6 app with dark theme, live charts |
| 6 | Support parallel execution | 4+ concurrent tests |
| 7 | Achieve Grade B (70+) on sample firmware | Demonstrate value end-to-end |

---

## 4. System Architecture

### 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RENODERESILIENCE v1.0                               │
│                    Desktop App + Headless Testing Framework                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PRESENTATION LAYER (PyQt6)                        │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │    │
│  │  │ Main Window  │  │ Campaign     │  │ Report Viewer            │  │    │
│  │  │ (QMainWindow)│  │ Designer     │  │ (HTML/PDF/JSON)          │  │    │
│  │  ├──────────────┤  ├──────────────┤  ├──────────────────────────┤  │    │
│  │  │ Sidebar      │  │ Test Runner  │  │ Comparison View          │  │    │
│  │  │ (QTreeView)  │  │ (Live/Async) │  │ (Side-by-Side)           │  │    │
│  │  ├──────────────┤  ├──────────────┤  ├──────────────────────────┤  │    │
│  │  │ Console Dock │  │ Charts       │  │ Settings Dialog          │  │    │
│  │  │ (QTextEdit)  │  │ (PyQtGraph)  │  │ (Pydantic-backed)        │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    API LAYER (FastAPI)                               │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │    │
│  │  │ POST /run    │  │ GET /status  │  │ GET /report/{id}         │  │    │
│  │  │ POST /campaign│  │ WS /live     │  │ GET /compare             │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                 CORE ENGINE (Python 3.11+)                         │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │    │
│  │  │ Campaign     │  │ Scheduler    │  │ Result Aggregator        │  │    │
│  │  │ Manager      │  │ (Parallel)   │  │ (Pass/Fail/Score)        │  │    │
│  │  ├──────────────┤  ├──────────────┤  ├──────────────────────────┤  │    │
│  │  │ Fault        │  │ Test Runner  │  │ Resilience Index         │  │    │
│  │  │ Injector     │  │ (QThread)    │  │ Calculator               │  │    │
│  │  ├──────────────┤  ├──────────────┤  ├──────────────────────────┤  │    │
│  │  │ Diagnosis    │  │ Report       │  │ Renode Bridge            │  │    │
│  │  │ Engine       │  │ Generator    │  │ (pyrenode3/QProcess)     │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │              RENODE ADAPTER LAYER                                    │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │    │
│  │  │ Board Config │  │ CPU Emulation│  │ Peripheral Hooks         │  │    │
│  │  │ (.repl/.json)│  │ (ARM/RISC-V) │  │ (I2C/SPI/UART/CAN/GPIO)  │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │              RENODE CORE (Existing, Open-Source)                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │    │
│  │  │ CPU Emulator │  │ Memory Model │  │ Peripheral Models        │  │    │
│  │  │ (ARM Cortex) │  │ (Flash/RAM)  │  │ (Timers/GPIO/UART/etc)   │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │              FIRMWARE UNDER TEST (User-provided)                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │    │
│  │  │ ELF/BIN      │  │ Source Maps  │  │ Test Harness             │  │    │
│  │  │ (compiled)   │  │ (optional)   │  │ (pytest/Robot)           │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Component Interaction Flow

```
User → GUI (PyQt6) → Core Engine → Renode Bridge → Renode Process → Firmware
                ↓         ↓              ↓
           Campaign   Fault YAML    Monitor Port (1234)
           Config     Taxonomy      Python API / REPL
                ↓         ↓              ↓
           Scheduler  Injector     Peripheral Hooks
                ↓         ↓              ↓
           Results ← Aggregator ← Sensor/Timer/Comm Values
                ↓
           RI Calculator → Diagnosis → Report Generator → HTML/PDF/JSON
```

---

## 5. Tech Stack

### 5.1 Complete Technology Matrix

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **GUI Framework** | PyQt6 | 6.6+ | Native desktop widgets, cross-platform |
| **Qt Designer** | Qt Creator | 6.6+ | Drag-and-drop UI design |
| **Styling** | QSS (Qt StyleSheets) | — | Dark theme, custom appearance |
| **Real-Time Charts** | PyQtGraph | 0.13+ | 60fps live plots, gauges, heatmaps |
| **Tables** | QTableView + PandasModel | — | Large dataset display |
| **PDF Viewer** | Qt PDF Module | 6.6+ | In-app report viewing |
| **HTML Preview** | QWebEngineView | 6.6+ | HTML report rendering |
| **Core Language** | Python | 3.11+ | Business logic, framework |
| **Renode Bridge** | pyrenode3 / QProcess | 1.15+ | Renode integration |
| **Data Processing** | Pandas + NumPy | 2.0+ | Result aggregation, statistics |
| **Config Validation** | Pydantic + YAML | 2.0+ | Schema validation, campaign configs |
| **Reports** | Jinja2 + WeasyPrint | — | HTML/PDF generation |
| **ML Diagnosis** | scikit-learn | 1.3+ | Failure classification |
| **REST API** | FastAPI | 0.100+ | Headless API access |
| **WebSocket** | FastAPI WebSocket | — | Live test progress streaming |
| **Test Runner** | pytest + Robot Framework | — | Test harness execution |
| **CLI** | Typer | 0.9+ | Command-line interface |
| **Packaging** | PyInstaller | 6.0+ | .exe / .dmg / .AppImage |
| **Auto-Updater** | pyupdater | 4.0+ | OTA updates |
| **CI/CD** | GitHub Actions | — | Automated testing, releases |
| **Container** | Docker (optional) | — | Portable deployment |

---

## 6. Backend / Core Engine

### 6.1 Module Breakdown

| Module | File | Responsibility |
|---|---|---|
| **Renode Bridge** | `src/core/renode_bridge.py` | Start/stop Renode, send monitor commands, read peripheral state |
| **Fault Injector** | `src/core/fault_injector.py` | Translate fault IDs to Renode monitor commands, inject 27 fault types |
| **Campaign Manager** | `src/core/campaign.py` | Load/save/validate campaign YAML, manage test suites |
| **Test Runner** | `src/core/test_runner.py` | Sequential and parallel test execution via QThreadPool |
| **Result Aggregator** | `src/core/result_aggregator.py` | Collect pass/fail, detection latency, recovery time, safety state |
| **Resilience Index** | `src/core/resilience_index.py` | Compute RI = (D×0.4) + (Rec×0.3) + (S×0.3), assign Grade A-F |
| **Diagnosis Engine** | `src/core/diagnosis_engine.py` | Rule-based failure classification + fix recommendations |
| **Report Generator** | `src/core/report_generator.py` | Export HTML (interactive), PDF (audit), JSON (CI/CD), JUnit XML |

### 6.2 Renode Bridge (Critical Backend Component)

```python
class RenodeBridge:
    def __init__(self):
        self.process: subprocess.Popen | None = None
        self.log_file: tempfile._TemporaryFileWrapper | None = None
        
    def start(self, platform_file: Path, firmware_file: Path) -> bool:
        """Launch Renode headless with platform + firmware."""
        script = f"""
            include @{platform_file}
            sysbus LoadELF @{firmware_file}
            start
        """
        self.log_file = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False)
        self.process = subprocess.Popen(
            ['renode', '--disable-xwt', '--port', '1234'],
            stdin=subprocess.PIPE,
            stdout=self.log_file,
            stderr=subprocess.STDOUT,
            text=True
        )
        # Wait for monitor port readiness
        return self._wait_for_monitor(timeout=15.0)
        
    def inject_fault(self, fault_id: str, params: dict) -> bool:
        """Send fault injection command to Renode monitor."""
        command = self._build_fault_command(fault_id, params)
        if self.process and self.process.stdin:
            self.process.stdin.write(f"{command}\n")
            self.process.stdin.flush()
            return True
        return False
        
    def read_peripheral(self, path: str) -> str | float | int:
        """Read value from Renode sysbus peripheral."""
        # Uses Renode's Python API or monitor 'sysbus ReadDoubleWord' etc.
        pass
        
    def stop(self, graceful: bool = True) -> bool:
        """Shutdown Renode process."""
        if self.process:
            if graceful:
                self.process.stdin.write("quit\n")
            self.process.wait(timeout=10)
            self.process.kill()
            self.process = None
        return True
```

### 6.3 Fault Injection Taxonomy (27 Types)

| Category | Count | Types |
|---|---|---|
| **Sensor Faults** | 8 | Stuck-at, Gaussian Noise, Impulse Noise, Drift, Bias, Missing Samples, Outliers, Sampling Jitter |
| **Timing Faults** | 5 | Deadline Miss, Clock Skew, Interrupt Storm, Watchdog Timeout, Race Condition |
| **Communication Faults** | 6 | Packet Loss, Latency Spike, Bus Flooding, Frame Corruption, Bus-Off State, Arbitration Loss |
| **Memory Faults** | 4 | Stack Overflow, Heap Corruption, Flash Bit-Flip, ECC Error |
| **Power Faults** | 3 | Brownout, Power Glitch, Sleep Failure |
| **GPIO/Peripheral Faults** | 5 | Pin Float, Pin Short, ADC Saturation, PWM Jitter, DMA Overrun |

---

## 7. API Design

### 7.1 REST Endpoints (FastAPI)

| Method | Endpoint | Description | Request | Response |
|---|---|---|---|
| `POST` | `/api/v1/run` | Run single fault test | `{"firmware": "path", "fault": "SF-01", "duration": 60}` | `TestResult` |
| `POST` | `/api/v1/campaign` | Run full campaign | `CampaignConfig` YAML/JSON | `CampaignResult` |
| `GET` | `/api/v1/status/{run_id}` | Check test status | — | `{"status": "running", "progress": 12, "total": 27}` |
| `GET` | `/api/v1/result/{run_id}` | Get test results | — | `Result` JSON |
| `GET` | `/api/v1/report/{run_id}` | Generate report | `?format=html|pdf|json` | File download |
| `POST` | `/api/v1/compare` | Compare two runs | `{"baseline": "id1", "optimized": "id2"}` | `ComparisonReport` |
| `GET` | `/api/v1/faults` | List all fault types | — | Array of 27 fault definitions |
| `GET` | `/api/v1/platforms` | List supported platforms | — | `["stm32f4", "nrf52840", "riscv_hifive1"]` |

### 7.2 WebSocket Endpoint

| Endpoint | Event | Payload |
|---|---|---|
| `WS /api/v1/live/{run_id}` | `test.started` | `{"fault_id": "SF-01", "timestamp": "..."}` |
| | `test.progress` | `{"current": 12, "total": 27, "eta_seconds": 480}` |
| | `test.result` | `TestResult` object |
| | `test.completed` | `{"run_id": "...", "final_ri": 73, "grade": "B"}` |

### 7.3 Python SDK API

```python
from renode_resilience import Campaign, FaultInjector

# Load campaign from YAML
campaign = Campaign.from_yaml("campaign.yaml")

# Run tests (blocking or async)
results = campaign.run(parallel=4)

# Access metrics
ri = results.resilience_index          # 0-100
grade = results.grade                   # 'A'-'F'
diagnosis = results.diagnose()          # Failure classification
recommendations = diagnosis.fixes     # List of suggested fixes

# Export reports
results.to_html("report.html")
results.to_pdf("report.pdf")
results.to_json("report.json")
results.to_junit("junit.xml")
```

---

## 8. UI/UX Design

### 8.1 Design Philosophy
- **Dark theme first** — reduces eye strain during long test campaigns
- **Embedded engineer-native** — sidebar navigation, dockable panels, monospace console
- **Real-time feedback** — live charts, progress bars, color-coded logs
- **Information density** — show everything important without clutter

### 8.2 Screen Inventory

| Screen | Widget | Key Elements |
|---|---|---|
| **Welcome / Project Browser** | `WelcomeScreen` | Recent projects, templates (STM32 Sensor, Motor, CAN, Power, Comm), import |
| **Campaign Designer** | `CampaignEditor` | Name, firmware upload, platform dropdown, fault checkboxes, severity/duration table, expected behavior rules, scoring weights |
| **Live Test Runner** | `TestRunnerView` | Progress bar, ETA, live results table (ID, Fault, Status, Detect, Recover, Safety, RI), real-time charts (line, bar, pie), console output |
| **Report Viewer** | `ReportViewer` | Summary card, critical findings list, detailed charts (radar, heatmap, timeline), export buttons |
| **Comparison View** | `ComparisonView` | Side-by-side baseline vs optimized, delta table, improvement percentage, key changes list |
| **Settings** | `SettingsDialog` | Renode path, theme, default weights, export paths |

### 8.3 Layout Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  QMainWindow (1400×900 min)                                                  │
│  ┌────────┬──────────────────────────────────────────────┬────────────────┐ │
│  │Sidebar │        Central StackedWidget                 │  Properties    │ │
│  │(250px) │                                              │  Panel (250px)   │ │
│  │        │  ┌────────────────────────────────────────┐  │                │ │
│  │Campaign│  │  Welcome → Designer → Runner →       │  │  Fault Params  │ │
│  │├─ New  │  │  Report → Compare                    │  │  ├─ Type       │ │
│  │├─ Open │  │                                        │  │  ├─ Severity   │ │
│  │├─ Save │  │  [Screen content changes here]       │  │  ├─ Duration   │ │
│  │└─ Exit │  │                                        │  │  └─ Target     │ │
│  │        │  └────────────────────────────────────────┘  │                │ │
│  │Firmware│                                              │  Expected      │ │
│  │├─ Load │                                              │  Behavior      │ │
│  │├─ Build│                                              │                │ │
│  │└─ Verify│                                             │  Resilience    │ │
│  │        │                                              │  Threshold     │ │
│  │Platform│                                              │                │ │
│  │├─ STM32│                                              │  Scoring       │ │
│  │├─ NRF52│                                              │  Weights       │ │
│  │└─ RISC-V│                                             │                │ │
│  │        │                                              │                │ │
│  │Settings│                                              │                │ │
│  └────────┴──────────────────────────────────────────────┴────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │  Console Dock (Bottom, 200px) — QTextEdit, color-coded, monospace       │  │
│  │  [INFO] Campaign started | [PASS] SF-01 | [FAIL] TF-01 | [WARN] CF-03  │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│  Status Bar: Renode ● Running | Tests: 12/27 | RI: 73/100 | Grade: B         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.4 Color Coding

| Severity/Status | Color | Hex |
|---|---|---|
| PASS / Safe | Green | `#4CAF50` |
| FAIL / Unsafe | Red | `#F44336` |
| WARNING / Partial | Amber | `#FF9800` |
| INFO | Blue | `#2196F3` |
| Grade A | Emerald | `#2ECC71` |
| Grade B | Blue | `#3498DB` |
| Grade C | Yellow | `#F1C40F` |
| Grade D | Orange | `#E67E22` |
| Grade F | Red | `#E74C3C` |

---

## 9. Security

### 9.1 Threat Model & Mitigations

| Threat | Risk | Mitigation |
|---|---|---|
| **Firmware IP Theft** | High | All execution is local; no cloud upload ever |
| **Test Data Leakage** | Medium | No external services; data stays on disk |
| **Malicious Firmware** | Medium | Sandboxed Renode process; resource limits; timeout guards; no network access from emulator |
| **Report Sensitivity** | Low | Optional AES-256 encryption for report files; access control via token |
| **CI/CD Secret Exposure** | Medium | Read-only tokens; no secrets in YAML configs; `.gitignore` for `campaigns/private/` |
| **Dependency Supply Chain** | Medium | Pinned versions in `requirements.txt`; hash verification; no unvetted packages |

### 9.2 Security Features
- **Local-only execution** — Renode runs on user's machine; zero network dependency
- **Firmware sandboxing** — ELF files are loaded into emulator, never executed natively
- **Resource guards** — CPU/memory limits on Renode subprocess; auto-kill after timeout
- **Encrypted reports** (optional) — `report.pdf.enc` with user-provided passphrase
- **Audit logging** — All fault injections and results logged to tamper-evident file

---

## 10. Performance

### 10.1 Target Metrics

| Metric | Target | Strategy |
|---|---|---|
| **Test Throughput** | 100 fault injections/hour | Parallel execution (4+ workers), lightweight firmware |
| **Report Generation** | <5 seconds | Jinja2 template caching, async WeasyPrint rendering |
| **Dashboard Load** | <2 seconds | Lazy loading, result pagination (50 rows/page) |
| **Memory Footprint** | <2GB RAM | Streaming logs (no full load), chunked Pandas processing |
| **Startup Time** | <10 seconds | Pre-compiled Renode, cached configs, lazy imports |
| **Chart FPS** | 60 fps | PyQtGraph GPU-accelerated plots, decimated data |
| **Campaign Load** | <1 second | Pydantic validation, YAML caching |

### 10.2 Optimization Strategies
- **QThreadPool** for parallel test execution (not multiprocessing — GIL acceptable for I/O-bound Renode)
- **Lazy widget initialization** — screens created on first access
- **Log rotation** — Console keeps last 10,000 lines; older lines archived
- **Pandas chunking** — Result tables use `pd.read_json(chunksize=1000)` for large campaigns
- **Template precompilation** — Jinja2 env with `bytecode_cache`

---

## 11. Workflow / Working Process

### 11.1 Typical User Workflow

```
┌─────────┐    ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  START  │───→│ 1. Create   │───→│ 2. Configure │───→│ 3. Design   │
│         │    │    Project  │    │   Platform   │    │   Campaign  │
└─────────┘    └─────────────┘    └──────────────┘    └─────────────┘
                                                           │
                                                           ▼
┌─────────┐    ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  DONE   │←───│ 6. Report   │←───│ 5. Analyze   │←───│ 4. Run Tests│
│         │    │   & Export  │    │   Results    │    │  (Live)     │
└─────────┘    └─────────────┘    └──────────────┘    └─────────────┘
     ▲
     │    ┌─────────────┐    ┌──────────────┐
     └───│ 7. Compare  │←───│ 8. Iterate  │
          │   Runs      │    │   & Fix     │
          └─────────────┘    └──────────────┘
```

### 11.2 Detailed Process Steps

**Step 1: Project Creation**
- User launches app → Welcome screen
- Selects "New Project" or opens recent
- Chooses template (STM32 Sensor, Motor Controller, CAN Bus, Power Management, Communication Stack)

**Step 2: Platform Configuration**
- Select platform from dropdown: STM32F4 Discovery, nRF52840 DK, HiFive1 RISC-V
- Upload firmware ELF file (validated: correct architecture, entry point exists)
- App auto-detects firmware info (size, symbols if available)

**Step 3: Campaign Design**
- Name the campaign
- Select fault categories via checkboxes (Sensor, Timing, Comm, Memory, Power, GPIO)
- Fine-tune individual faults: severity, duration, target peripheral
- Define expected behavior for each fault (e.g., `detect_stuck_sensor()` within 5000ms)
- Set scoring weights (default: Detection 40%, Recovery 30%, Safety 30%)
- Set minimum grade threshold (default: B = 70/100)

**Step 4: Test Execution**
- Click "Run Campaign"
- App launches Renode via QProcess
- Tests run sequentially or in parallel (configurable)
- Live updates: progress bar, results table, charts, console logs
- User can pause/stop at any time

**Step 5: Analysis**
- Campaign completes → auto-switch to Report Viewer
- View Overall RI, Grade, Pass/Fail counts
- Review Critical Findings with severity icons
- Inspect detailed charts: radar (6 categories), heatmap (fault vs score), timeline (detection latency)

**Step 6: Reporting**
- Export HTML (interactive, shareable)
- Export PDF (audit-ready, printable)
- Export JSON (CI/CD integration)
- Export JUnit XML (Jenkins/GitLab compatibility)

**Step 7: Comparison**
- Load two campaign results side-by-side
- View delta scores per fault
- Identify which fixes improved resilience
- Export comparison report

**Step 8: Iteration**
- Engineer fixes firmware based on recommendations
- Re-runs campaign
- Compares before/after to verify improvement

---

## 12. Complete Features List

### 12.1 Core Testing Features
| # | Feature | Status |
|---|---|---|
| 1 | 27 hardware fault types across 6 categories | ✅ Planned |
| 2 | Automated test campaigns (YAML-defined) | ✅ Planned |
| 3 | Parallel test execution (4+ concurrent) | ✅ Planned |
| 4 | Resilience Index scoring (0-100, Grade A-F) | ✅ Planned |
| 5 | Real-time test monitoring (live charts, logs) | ✅ Planned |
| 6 | Pass/fail/warning classification with evidence | ✅ Planned |
| 7 | Sequential and parallel scheduler modes | ✅ Planned |
| 8 | Campaign save/load/reuse | ✅ Planned |
| 9 | Firmware upload and validation | ✅ Planned |
| 10 | Platform selection (STM32, nRF52, RISC-V) | ✅ Planned |

### 12.2 Diagnosis Features
| # | Feature | Status |
|---|---|---|
| 11 | Rule-based failure classifier | ✅ Planned |
| 12 | Root cause analysis (fault → code path trace) | ✅ Planned |
| 13 | Fix recommendations with code examples | ✅ Planned |
| 14 | ISO 26262 compliance mapping | ✅ Planned |
| 15 | DO-178C compliance mapping | ✅ Planned |

### 12.3 Reporting Features
| # | Feature | Status |
|---|---|---|
| 16 | Interactive HTML report | ✅ Planned |
| 17 | Audit-ready PDF report | ✅ Planned |
| 18 | JSON export (CI/CD integration) | ✅ Planned |
| 19 | JUnit XML export (Jenkins/GitLab) | ✅ Planned |
| 20 | Trend analysis (compare runs over time) | ✅ Planned |
| 21 | Side-by-side campaign comparison | ✅ Planned |

### 12.4 UI Features
| # | Feature | Status |
|---|---|---|
| 22 | PyQt6 native desktop app (Windows/macOS/Linux) | ✅ Planned |
| 23 | Dark theme with QSS | ✅ Planned |
| 24 | Drag-and-drop campaign designer | ✅ Planned |
| 25 | Live test runner with progress/charts/logs | ✅ Planned |
| 26 | Console output with color-coded severity | ✅ Planned |
| 27 | Report viewer with HTML/PDF/JSON tabs | ✅ Planned |
| 28 | Comparison view (baseline vs optimized) | ✅ Planned |
| 29 | Settings dialog with validation | ✅ Planned |

### 12.5 API & Integration Features
| # | Feature | Status |
|---|---|---|
| 30 | FastAPI REST endpoints | ✅ Planned |
| 31 | WebSocket live streaming | ✅ Planned |
| 32 | Python SDK (`import renode_resilience`) | ✅ Planned |
| 33 | CLI with Typer (`renode-resilience run`) | ✅ Planned |
| 34 | GitHub Actions CI/CD integration | ✅ Planned |
| 35 | Docker container (optional) | ✅ Planned |

---

## 13. Setup & Installation

### 13.1 Prerequisites
- Python 3.11+
- Renode 1.15+ (installed and on PATH)
- Qt 6.6+ (for PyQt6)
- 4GB RAM minimum, 8GB recommended
- 2GB disk space

### 13.2 Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/user/renode-resilience.git
cd renode-resilience

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify Renode installation
renode --version  # Should print 1.15+

# 5. Launch desktop app
python -m src.main

# 6. Or use CLI
renode-resilience --help
```

### 13.3 Platform-Specific Notes

| Platform | Additional Steps |
|---|---|
| **Windows** | Install Visual C++ Redistributable; add Renode to PATH |
| **macOS** | `brew install renode`; may need Xcode Command Line Tools |
| **Linux** | `sudo apt install renode`; ensure `/usr/bin/renode` is executable |

---

## 14. Usage Guide

### 14.1 CLI Usage

```bash
# Run single fault test
renode-resilience run \
  --firmware examples/sensor-firmware/build/sensor.elf \
  --platform platforms/stm32f4_discovery.repl \
  --fault SF-01 \
  --duration 60

# Run full campaign from YAML
renode-resilience campaign \
  --config campaigns/sensor_suite.yaml \
  --parallel 4 \
  --output results/

# Generate report from results
renode-resilience report \
  --results results/campaign_2026-08-26.json \
  --format pdf \
  --output report.pdf

# Compare two runs
renode-resilience compare \
  --baseline results/baseline.json \
  --optimized results/optimized.json \
  --output comparison.html
```

### 14.2 Campaign YAML Example

```yaml
name: "Sensor Suite Validation"
description: "Validate temperature sensor fault handling"
firmware: "examples/sensor-firmware/build/sensor.elf"
platform: "platforms/stm32f4_discovery.repl"
duration: 60
parallel: 4

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
    
  - id: TF-01
    name: "Deadline Miss"
    params: { delay_ms: 100, target: "control_loop" }
    expected: "watchdog_reset"
    timeout_ms: 200

scoring:
  weights:
    detection: 0.4
    recovery: 0.3
    safety: 0.3
  thresholds:
    grade_a: 90
    grade_b: 70
    grade_c: 50
    grade_d: 30
```

### 14.3 Python SDK Usage

```python
from renode_resilience import Campaign, FaultInjector
from pathlib import Path

# Load and run
campaign = Campaign.from_yaml("campaign.yaml")
results = campaign.run(parallel=4)

# Inspect
print(f"Resilience Index: {results.resilience_index}/100")
print(f"Grade: {results.grade}")
print(f"Passed: {results.pass_count}/{results.total_count}")

# Diagnose
for failure in results.failures:
    diag = failure.diagnose()
    print(f"{failure.fault_id}: {diag.root_cause}")
    for rec in diag.recommendations:
        print(f"  → {rec}")

# Export
results.to_pdf(Path("report.pdf"))
results.to_junit(Path("junit.xml"))
```

---

## 15. Precautions & Limitations

### 15.1 Usage Precautions
| # | Precaution | Reason |
|---|---|---|
| 1 | **Always test in Renode, never on physical hardware** | Fault injection can damage real boards (voltage spikes, pin shorts) |
| 2 | **Keep firmware ELF files backed up** | Campaigns may reference paths that move |
| 3 | **Set reasonable timeouts** | Infinite loops in firmware under test can hang Renode |
| 4 | **Monitor disk space** | Renode logs can grow to 100MB+ per long campaign |
| 5 | **Close Renode gracefully** | Force-killing may leave zombie processes on port 1234 |
| 6 | **Validate YAML before running** | Invalid fault params crash the test runner mid-campaign |
| 7 | **Use virtualenv** | Avoid dependency conflicts with system Python packages |

### 15.2 Known Limitations
- **Renode platform coverage** — Only STM32F4, nRF52840, and HiFive1 are pre-built; other platforms need custom `.repl` files
- **Fault realism** — Injected faults are approximations; real hardware failure modes may differ
- **Performance** — Emulation is 10-100x slower than real hardware; long campaigns take hours
- **ML diagnosis** — Rule-based only in v1.0; ML classifier requires training dataset
- **Network protocols** — Limited to I2C/SPI/UART/CAN; Ethernet/USB not supported in v1.0

---

## 16. Advantages

### 16.1 vs. Physical HIL Testing
| Factor | RenodeResilience | Physical HIL |
|---|---|---|
| **Cost** | Free (open source) | $50K-$200K per rig |
| **Setup Time** | 10 minutes | Days to weeks |
| **Fault Coverage** | 27 types, reproducible | Limited by physical hardware |
| **Parallel Tests** | 4+ simultaneous | 1 per rig |
| **Safety** | No risk of hardware damage | Voltage spikes can destroy boards |
| **CI/CD Integration** | Native (JSON/JUnit) | Requires custom adapters |

### 16.2 vs. Manual Testing
| Factor | RenodeResilience | Manual Testing |
|---|---|---|
| **Coverage** | 100% of defined faults | Spot-check only |
| **Quantification** | 0-100 Resilience Index | "Seems okay" |
| **Reproducibility** | Identical every run | Human error, inconsistent |
| **Reporting** | Auto-generated PDF/HTML | Manual documentation |
| **Speed** | 100 tests/hour | 5-10 tests/day |

### 16.3 vs. Other Emulation Tools
| Factor | RenodeResilience | QEMU + Custom | Proprietary (Vector) |
|---|---|---|---|
| **Fault Injection** | Built-in 27 types | Must build yourself | Limited, expensive |
| **Resilience Metric** | RI (0-100) | None | Proprietary |
| **Cost** | Free | Free (high effort) | $10K+ per seat |
| **Desktop UI** | Native PyQt6 | None | Windows-only |
| **Open Source** | MIT | Varies | No |

---

## 17. Future Scope

### 17.1 v1.1 (Near-term, 1-2 months)
- [ ] **Additional platforms**: ESP32, RP2040, SAMD21
- [ ] **More fault types**: EMI interference, temperature drift, clock domain crossing
- [ ] **ML-based diagnosis**: Train classifier on accumulated campaign data
- [ ] **Plugin system**: Third-party fault injectors
- [ ] **VS Code extension**: Inline resilience annotations

### 17.2 v2.0 (Mid-term, 3-6 months)
- [ ] **Distributed testing**: Run campaigns across multiple machines
- [ ] **Cloud dashboard** (optional): Upload results for team analytics
- [ ] **Fuzzing integration**: Combine with AFL/libFuzzer for input fuzzing
- [ ] **RTOS-aware faults**: FreeRTOS/ Zephyr task-specific injections
- [ ] **Hardware trace correlation**: Map failures to actual instruction traces

### 17.3 v3.0 (Long-term, 6-12 months)
- [ ] **AI-generated fixes**: LLM suggests code patches based on diagnosis
- [ ] **Formal verification bridge**: Export counterexamples to SPIN/UPPAAL
- [ ] **Industry certification**: TÜV approval for ISO 26262 tool qualification
- [ ] **Enterprise features**: LDAP auth, audit trails, multi-user campaigns

---

## 18. Deliverables Checklist

| # | Deliverable | Format | Status |
|---|---|---|---|
| 1 | GitHub Repository | Source code | ✅ https://github.com/Rohithdgrr/RUDRA-CAPSTONE-PROJECT (`main` b289d67) |
| 2 | Desktop Application | `.exe` / `.dmg` / `.AppImage` | ✅ `src/main.py` PyQt6 1400×900 + `RenodeResilience.spec` + `scripts/build.py` |
| 3 | README Documentation | Markdown | ✅ `README.md` + `docs/00-INDEX.md` 22 md |
| 4 | User Guide | PDF | ✅ `docs/04-USER_GUIDE.md` + HTML report via `report_generator` |
| 5 | API Documentation | Markdown / Swagger | ✅ `docs/13-API_REST.md` + `src/api/app.py` Swagger `/docs` |
| 6 | 5 Example Campaigns | YAML + ELF | ✅ `campaigns/sensor_suite.yaml` + `examples/*/campaign.yaml` (3) + placeholders ELF |
| 7 | 3 Sample Firmwares | C + build scripts | ✅ `examples/sensor-firmware/src/main.c` + `motor-controller` + `can-validator` + Makefiles |
| 8 | Platform Definitions | `.repl` files | ✅ `resources/platforms/stm32f4_discovery.repl` + `nrf52840dk` + `riscv_hifive1` (from `renode/platforms/`) |
| 9 | Demo Video | 5-minute MP4 / YouTube | 🚧 Guide `docs/DEMO_VIDEO_GUIDE.md` — auto-capture `preview.py` 1400×900 |
| 10 | Methodology Paper | 8-10 pages, IEEE format | 🚧 Outline `docs/METHODOLOGY_PAPER.md` — RI formula + fault taxonomy + evaluation |
| 11 | CI/CD Pipeline | GitHub Actions | ✅ `.github/workflows/ci.yml` + `release.yml` + `renode-test-action` |
| 12 | Docker Image | `Dockerfile` + compose | ✅ `Dockerfile` python:3.11-slim + `renode-docker/Dockerfile:8` 1.16.1 |
| 13 | Unit Tests | pytest (90%+ coverage) | ✅ `tests/unit/` 17 tests `test_resilience/api/diagnosis/report` — run `pytest -q` |
| 14 | Integration Tests | Robot Framework | ✅ `renode/tests/*.robot` + `renode-test-action` — `tests/integration/` ready |

---

## 19. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Renode API changes | Medium | High | Pin version, abstraction layer |
| PyQt6 licensing confusion | Low | Medium | MIT-compatible, commercial use allowed |
| Performance on large firmwares | High | Medium | Streaming, chunked processing, progress save |
| User adoption (embedded engineers resistant to new tools) | Medium | High | Focus on CLI first, GUI as convenience |
| Complex platform setup | Medium | Medium | One-click installer, bundled Renode |

---

## 20. Conclusion

RenodeResilience fills a critical gap in embedded firmware testing by providing the first structured, quantitative, and automated fault-injection framework built on Renode. It combines:

- **27 hardware fault types** with one-click injection
- **A 0-100 Resilience Index** that turns "robustness" into a measurable metric
- **A native desktop UI** designed for embedded engineers
- **Actionable diagnosis** with fix recommendations
- **Full CI/CD integration** via JSON/JUnit exports

The 14-day development plan is aggressive but achievable by leveraging Renode's existing emulation engine and focusing on the **layer on top** that no one has built yet. The result is a portfolio project that demonstrates deep embedded systems knowledge, testing methodology, and full-stack Python development — directly addressing a $500M+ industry problem.

---


# Hardware Components Testable with RenodeResilience

| Component | Description |
|---|---|
| **ARM Cortex-M CPUs** | STM32F4, STM32F7 and other ARM-based MCUs |
| **RISC-V CPUs** | HiFive1, FE310 and other RISC-V cores |
| **nRF52 SoC** | Nordic Bluetooth SoC with ARM Cortex-M4 |
| **Flash Memory** | Program memory with bit-flip and ECC fault injection |
| **RAM / SRAM** | Volatile memory with corruption and ECC error testing |
| **Stack** | Call stack with overflow boundary testing |
| **Heap** | Dynamic memory with corruption injection |
| **I2C Sensors** | Temperature, accelerometer, gyroscope sensors |
| **SPI Peripherals** | External flash, displays, ADCs |
| **UART** | Serial communication ports |
| **CAN Bus** | Automotive controller area network |
| **GPIO Pins** | Digital input/output pins |
| **ADC** | Analog-to-digital converters |
| **PWM** | Pulse-width modulation timers |
| **DMA** | Direct memory access controllers |
| **RTC** | Real-time clock with skew injection |
| **Watchdog Timer** | System reset watchdog |
| **Interrupt Controller** | NVIC / PLIC with storm injection |
| **Power Management** | Voltage regulators, sleep controllers |
| **Timers** | General-purpose and system tick timers |

**Document Version:** 1.0.0  
**Last Updated:** 2026-08-26  
**Author:** RenodeResilience Team  
**Status:** Draft / Ready for Development