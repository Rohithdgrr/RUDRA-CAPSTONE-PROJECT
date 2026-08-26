 # 🖥️ RENODERESILIENCE DESKTOP APPLICATION — Complete Build Plan

---

## 1. APP TYPE DECISION

| Factor | Desktop App | Web App |
|---|---|---|
| Renode Integration | Native process control | Requires server wrapper |
| Firmware IP Security | Local only, no cloud | Risk of upload |
| Embedded Engineer Preference | 93% use local tools | Browser = secondary |
| Offline Capability | Full | Limited |
| Performance | Direct hardware access | Network latency |
| **Winner** | **✅ DESKTOP** | ❌ |

**Framework:** PyQt6 (Python-native, Renode-compatible, cross-platform)

---

## 2. COMPLETE ARCHITECTURE (Desktop)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RENODERESILIENCE DESKTOP v1.0                             │
│                         PyQt6 + Renode Integration                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  MAIN WINDOW (QMainWindow)                                         │    │
│  │  ┌────────────┬──────────────────────────────┬──────────────────┐  │    │
│  │  │  Sidebar   │        Central Area          │   Properties     │  │    │
│  │  │  (QTree)   │                              │   Panel          │  │    │
│  │  │            │  ┌────────────────────────┐  │   (QDock)        │  │    │
│  │  │  Campaigns │  │    Stacked Widgets     │  │                  │  │    │
│  │  │  ├─ New    │  │  ┌──────────────────┐  │  │  Fault Params    │  │    │
│  │  │  ├─ Recent │  │  │  Dashboard View  │  │  │  ├─ Type        │  │    │
│  │  │  ├─ Results│  │  │  (Live Charts)   │  │  │  ├─ Severity    │  │    │
│  │  │  └─ Templates│  │  └──────────────────┘  │  │  ├─ Duration    │  │    │
│  │  │            │  │  ┌──────────────────┐  │  │  └─ Target      │  │    │
│  │  │  Firmware  │  │  │  Test Runner     │  │  │                  │  │    │
│  │  │  ├─ Upload │  │  │  (Progress/Logs) │  │  │  Expected        │  │    │
│  │  │  ├─ Select │  │  └──────────────────┘  │  │  Behavior        │  │    │
│  │  │  └─ Build  │  │  ┌──────────────────┐  │  │                  │  │    │
│  │  │            │  │  │  Report Viewer   │  │  │  Resilience      │  │    │
│  │  │  Platforms │  │  │  (HTML/PDF/JSON) │  │  │  Threshold       │  │    │
│  │  │  ├─ STM32  │  │  └──────────────────┘  │  │                  │  │    │
│  │  │  ├─ NRF52  │  │  ┌──────────────────┐  │  │  Scoring Weights │  │    │
│  │  │  └─ RISC-V │  │  │  Comparison View │  │  │  ├─ Detection   │  │    │
│  │  │            │  │  │  (Side-by-Side)  │  │  │  ├─ Recovery    │  │    │
│  │  │  Settings  │  │  │                  │  │  │  └─ Safety      │  │    │
│  │  │            │  │  └──────────────────┘  │  │                  │  │    │
│  │  └────────────┴──────────────────────────────┴──────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  BOTTOM PANEL (QDock)                                              │    │
│  │  ┌──────────────────────────────────────────────────────────────┐  │    │
│  │  │  Console Output (QTextEdit, monospace, color-coded)          │  │    │
│  │  │  [INFO]  Campaign started: sensor_validation                 │  │    │
│  │  │  [PASS]  SF-01: Stuck-at fault detected in 23ms            │  │    │
│  │  │  [FAIL]  TF-01: Deadline miss caused watchdog reset        │  │    │
│  │  │  [WARN]  CF-03: Bus flooding - anomaly threshold exceeded  │  │    │
│  │  └──────────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  STATUS BAR                                                        │    │
│  │  Renode: ● Running | Tests: 12/27 | RI: 73/100 | Grade: B        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. COMPLETE TECH STACK (Desktop)

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **GUI Framework** | PyQt6 | 6.6+ | Native desktop widgets |
| **Qt Designer** | Qt Creator | 6.6+ | Drag-and-drop UI design |
| **Styling** | QSS (Qt StyleSheets) | — | Dark theme, custom look |
| **Charts** | PyQtGraph | 0.13+ | Real-time plots, 60fps |
| **Tables** | QTableView + PandasModel | — | Large dataset display |
| **PDF Viewer** | Qt PDF Module | 6.6+ | In-app report viewing |
| **Web Preview** | QWebEngineView | 6.6+ | HTML report rendering |
| **Core Engine** | Python 3.11+ | — | Business logic |
| **Renode Bridge** | pyrenode3 | 1.15+ | Python API for Renode |
| **Process Control** | QProcess | — | Launch/manage Renode |
| **Config** | Pydantic + YAML | 2.0+ | Schema validation |
| **Data** | Pandas + NumPy | 2.0+ | Result processing |
| **Reports** | Jinja2 + WeasyPrint | — | PDF generation |
| **ML Diagnosis** | scikit-learn | 1.3+ | Failure classification |
| **Packaging** | PyInstaller | 6.0+ | .exe/.dmg/.AppImage |
| **Updater** | pyupdater | 4.0+ | Auto-update mechanism |

---

## 4. SCREEN-BY-SCREEN UI DESIGN

### Screen 1: Welcome / Project Browser
```
┌─────────────────────────────────────────────────────────────┐
│  RENODERESILIENCE                                    [New] │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Recent Projects          Templates                         │
│  ┌─────────────────┐     ┌─────────────────────────────┐   │
│  │ ▶ sensor_suite  │     │ ● STM32 Sensor Validation   │   │
│  │   RI: 73/100    │     │ ● Motor Controller Safety   │   │
│  │   2 hours ago   │     │ ● CAN Bus Resilience Test   │   │
│  ├─────────────────┤     │ ● Power Management Stress   │   │
│  │ ▶ motor_ctrl    │     │ ● Communication Stack Test  │   │
│  │   RI: 45/100    │     └─────────────────────────────┘   │
│  │   1 day ago     │                                       │
│  ├─────────────────┤     [Open Project]  [Import Campaign] │
│  │ ▶ can_validator │                                       │
│  │   RI: 91/100    │                                       │
│  │   3 days ago    │                                       │
│  └─────────────────┘                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Screen 2: Campaign Designer
```
┌─────────────────────────────────────────────────────────────┐
│  Campaign Designer                              [Run] [Save] │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Name: [Sensor Suite Validation          ]                  │
│  Firmware: [Browse...] sensor.elf (STM32F407, 128KB)       │
│  Platform: [▼ STM32F4 Discovery      ]                      │
│  Duration: [60] seconds per test                            │
│  Parallel: [4 ▲▼] concurrent tests                          │
│                                                             │
│  ┌─ Fault Selection ─────────────────────────────────────┐  │
│  │  [✓] Sensor Faults    [✓] Timing Faults             │  │
│  │  [✓] Comm Faults      [ ] Memory Faults             │  │
│  │  [ ] Power Faults     [ ] GPIO Faults               │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ Selected Faults ─────────────────────────────────────┐  │
│  │  ID    Type      Severity  Duration  Target          │  │
│  │  SF-01 Stuck     HIGH      60s       Temperature     │  │
│  │  SF-02 Noise     MEDIUM    60s       Temperature     │  │
│  │  TF-01 Deadline  CRITICAL  60s       ControlLoop    │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ Expected Behavior ───────────────────────────────────┐  │
│  │  SF-01 → detect_stuck_sensor() within 5000ms        │  │
│  │  SF-02 → std_dev < 2.0 after filtering              │  │
│  │  TF-01 → watchdog_reset within 100ms                │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  Scoring Weights: Detection [40%] Recovery [30%] Safety [30%]│
│  Minimum Grade: [▼ B (70/100)     ]                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Screen 3: Live Test Runner
```
┌─────────────────────────────────────────────────────────────┐
│  Test Runner                                    [Stop] [⏸] │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Progress: [████████████████████░░░░░░░░] 12/27 (44%)      │
│  ETA: 8 minutes remaining                                   │
│                                                             │
│  ┌─ Live Results ────────────────────────────────────────┐  │
│  │  ID    Fault      Status  Detect  Recover  Safety  RI │  │
│  │  SF-01 Stuck      PASS    23ms    45ms     OK     100│  │
│  │  SF-02 Noise      PASS    12ms    89ms     OK      95│  │
│  │  SF-03 Impulse    FAIL    --      --       OK      40│  │
│  │  TF-01 Deadline   FAIL    5ms     --       FAIL    25│  │
│  │  CF-01 PacketLoss PASS    8ms     12ms     OK      98│  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ Real-Time Charts ────────────────────────────────────┐  │
│  │  [Line: RI over time]  [Bar: Fault category scores]  │  │
│  │  [Pie: Pass/Fail/Warning distribution]               │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  Console:                                                   │
│  [INFO]  Starting test SF-03: Impulse noise injection      │
│  [WARN]  Sensor value spiked to 999.0 (expected <100)     │
│  [ERROR] Firmware did not detect outlier within timeout     │
│  [FAIL]  Test SF-03 completed: RI=40, Grade=F              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Screen 4: Report Viewer
```
┌─────────────────────────────────────────────────────────────┐
│  Report Viewer                    [Export PDF] [Export JSON] │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ┌─ Summary ─────────────────────────────────────────────┐  │
│  │  Campaign: Sensor Suite Validation                    │  │
│  │  Overall RI: 69/100  │  Grade: C  │  Status: MARGINAL│  │
│  │  Pass: 15  │  Fail: 8  │  Warning: 4  │  Total: 27    │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ Critical Findings ───────────────────────────────────┐  │
│  │  ⚠ 1. Impulse noise not detected (SF-03)            │  │
│  │     → Recommendation: Add median filter (3-sample)   │  │
│  │  ❌ 2. Deadline miss causes unsafe state (TF-01)     │  │
│  │     → Recommendation: Add task timeout + watchdog     │  │
│  │  ⚠ 3. Bus flooding anomaly threshold too high (CF-03)│  │
│  │     → Recommendation: Lower threshold to 50Hz        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ Detailed Charts ─────────────────────────────────────┐  │
│  │  [Radar: Category scores]  [Heatmap: Fault vs RI]    │  │
│  │  [Timeline: Detection latency per fault]              │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  [View Full Report in Browser]  [Compare with Previous Run] │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Screen 5: Comparison View
```
┌─────────────────────────────────────────────────────────────┐
│  Compare Runs                                               │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ┌─ Baseline ──────────────┐  ┌─ Optimized ──────────────┐ │
│  │  Run: 2026-08-20        │  │  Run: 2026-08-26        │ │
│  │  RI: 45/100 (Grade D)   │  │  RI: 73/100 (Grade B)   │ │
│  │  Pass: 8/27             │  │  Pass: 19/27            │ │
│  └─────────────────────────┘  └─────────────────────────┘  │
│                                                             │
│  Improvement: +28 points (+62%)                             │
│                                                             │
│  ┌─ Side-by-Side Fault Results ──────────────────────────┐  │
│  │  Fault    │  Baseline  │  Optimized  │  Delta        │  │
│  │  SF-01    │  25 (F)    │  100 (A)    │  +75 ✅       │  │
│  │  SF-03    │  30 (F)    │  85 (B)     │  +55 ✅       │  │
│  │  TF-01    │  15 (F)    │  60 (C)     │  +45 ✅       │  │
│  │  CF-01    │  90 (A)    │  95 (A)     │  +5           │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  Key Changes in Optimized Firmware:                         │
│  1. Added median filter for outlier detection               │
│  2. Increased watchdog timeout from 10ms to 50ms            │
│  3. Added task yield points in control loop                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. COMPLETE FILE STRUCTURE

```
renode-resilience/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── app.py                     # QApplication setup
│   ├── main_window.py             # QMainWindow controller
│   │
│   ├── core/                      # Business logic (headless)
│   │   ├── __init__.py
│   │   ├── campaign.py            # Campaign dataclass & manager
│   │   ├── fault_injector.py      # Renode fault injection hooks
│   │   ├── test_runner.py         # Test execution engine
│   │   ├── result_aggregator.py   # Pass/fail/score logic
│   │   ├── resilience_index.py    # RI calculator (0-100)
│   │   ├── diagnosis_engine.py    # Failure classifier + recommendations
│   │   ├── report_generator.py    # HTML/PDF/JSON export
│   │   └── renode_bridge.py       # pyrenode3 wrapper
│   │
│   ├── gui/                       # PyQt6 UI components
│   │   ├── __init__.py
│   │   ├── widgets/
│   │   │   ├── __init__.py
│   │   │   ├── sidebar.py         # Left navigation tree
│   │   │   ├── campaign_editor.py # Campaign design form
│   │   │   ├── test_runner_view.py # Live execution panel
│   │   │   ├── report_viewer.py   # HTML/PDF display
│   │   │   ├── comparison_view.py # Side-by-side compare
│   │   │   ├── console_output.py  # Color-coded log viewer
│   │   │   ├── fault_selector.py  # Checkable fault tree
│   │   │   ├── property_panel.py  # Right-side dock
│   │   │   ├── charts/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ri_gauge.py    # Circular progress gauge
│   │   │   │   ├── fault_heatmap.py # Fault vs score heatmap
│   │   │   │   ├── timeline_chart.py # Detection latency
│   │   │   │   ├── category_radar.py # 6-category radar
│   │   │   │   └── pass_fail_pie.py # Distribution pie
│   │   │   └── dialogs/
│   │   │       ├── __init__.py
│   │   │       ├── new_campaign.py
│   │   │       ├── firmware_upload.py
│   │   │       ├── settings_dialog.py
│   │   │       └── about_dialog.py
│   │   │
│   │   ├── styles/
│   │   │   ├── __init__.py
│   │   │   ├── dark_theme.qss     # Main dark stylesheet
│   │   │   ├── light_theme.qss    # Optional light mode
│   │   │   └── icons/             # SVG icons for all actions
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── qt_helpers.py      # Common Qt utilities
│   │       ├── pandas_model.py    # QTableView + Pandas bridge
│   │       └── async_workers.py   # QThreadPool workers
│   │
│   └── config/
│       ├── __init__.py
│       ├── defaults.py            # Default settings
│       ├── schemas.py             # Pydantic models
│       └── validator.py           # Config validation
│
├── resources/
│   ├── ui/                        # Qt Designer .ui files
│   │   ├── main_window.ui
│   │   ├── campaign_editor.ui
│   │   └── test_runner.ui
│   │
│   ├── icons/                     # App icons (all sizes)
│   │   ├── app_icon.svg
│   │   ├── app_icon_16.png
│   │   ├── app_icon_32.png
│   │   ├── app_icon_48.png
│   │   ├── app_icon_128.png
│   │   └── app_icon_256.png
│   │
│   ├── templates/                 # Report Jinja2 templates
│   │   ├── report_base.html
│   │   ├── report_pdf.css
│   │   └── iso26262_checklist.html
│   │
│   └── platforms/                 # Renode .repl files
│       ├── stm32f4_discovery.repl
│       ├── nrf52840dk.repl
│       └── riscv_hifive1.repl
│
├── examples/                      # Sample firmware + campaigns
│   ├── sensor-firmware/
│   │   ├── src/
│   │   ├── build/
│   │   └── campaign.yaml
│   ├── motor-controller/
│   └── can-validator/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── gui/
│
├── docs/
│   ├── README.md
│   ├── INSTALL.md
│   ├── USER_GUIDE.md
│   ├── API.md
│   └── screenshots/
│
├── scripts/
│   ├── build.py                   # Build automation
│   ├── package.py                 # PyInstaller packaging
│   └── install_renode.py          # Renode dependency installer
│
├── requirements.txt
├── requirements-dev.txt
├── setup.py
├── pyproject.toml
├── .gitignore
├── LICENSE (MIT)
└── README.md
```

---

## 6. PHASE-WISE DEVELOPMENT PLAN (14 Days)

### Phase 1: Project Setup & Renode Integration (Days 1-2)

| Day | Task | Files Created | Deliverable |
|---|---|---|---|
| 1 | Install PyQt6, Qt Creator, Renode | `requirements.txt` | Dev environment ready |
| 1 | Design main window in Qt Designer | `resources/ui/main_window.ui` | `.ui` file |
| 2 | Load `.ui` in Python, setup QApplication | `src/app.py`, `src/main_window.py` | Blank window opens |
| 2 | Integrate Renode via QProcess | `src/core/renode_bridge.py` | Can start/stop Renode |

### Phase 2: Core Engine (Days 3-5)

| Day | Task | Files Created | Deliverable |
|---|---|---|---|
| 3 | Implement fault taxonomy (YAML) | `src/config/schemas.py` | 27 fault types defined |
| 3 | Build fault injector (Renode hooks) | `src/core/fault_injector.py` | Can inject SF-01 |
| 4 | Create campaign manager | `src/core/campaign.py` | Load/save campaigns |
| 4 | Build test runner (sequential) | `src/core/test_runner.py` | Run single test |
| 5 | Add parallel scheduler | `src/core/test_runner.py` | Run 4 tests simultaneously |
| 5 | Implement result aggregator | `src/core/result_aggregator.py` | Pass/fail logic |

### Phase 3: Resilience Scoring & Diagnosis (Days 6-7)

| Day | Task | Files Created | Deliverable |
|---|---|---|---|
| 6 | Build RI calculator | `src/core/resilience_index.py` | 0-100 score |
| 6 | Implement grading (A-F) | `src/core/resilience_index.py` | Grade output |
| 7 | Create diagnosis engine | `src/core/diagnosis_engine.py` | Failure classification |
| 7 | Add recommendation system | `src/core/diagnosis_engine.py` | Fix suggestions |

### Phase 4: GUI Screens (Days 8-10)

| Day | Task | Files Created | Deliverable |
|---|---|---|---|
| 8 | Build sidebar + campaign browser | `src/gui/widgets/sidebar.py` | Navigation works |
| 8 | Create campaign editor form | `src/gui/widgets/campaign_editor.py` | Design campaigns visually |
| 9 | Build test runner view (live) | `src/gui/widgets/test_runner_view.py` | Progress bars, charts |
| 9 | Add console output panel | `src/gui/widgets/console_output.py` | Color-coded logs |
| 10 | Create report viewer | `src/gui/widgets/report_viewer.py` | HTML display |
| 10 | Build comparison view | `src/gui/widgets/comparison_view.py` | Side-by-side runs |

### Phase 5: Charts & Visualization (Days 11-12)

| Day | Task | Files Created | Deliverable |
|---|---|---|---|
| 11 | Implement RI gauge | `src/gui/widgets/charts/ri_gauge.py` | Circular progress |
| 11 | Add fault heatmap | `src/gui/widgets/charts/fault_heatmap.py` | Fault vs score grid |
| 12 | Create timeline chart | `src/gui/widgets/charts/timeline_chart.py` | Detection latency |
| 12 | Add category radar | `src/gui/widgets/charts/category_radar.py` | 6-axis radar |

### Phase 6: Polish & Packaging (Days 13-14)

| Day | Task | Files Created | Deliverable |
|---|---|---|---|
| 13 | Apply dark theme (QSS) | `src/gui/styles/dark_theme.qss` | Professional look |
| 13 | Add icons, tooltips, shortcuts | `resources/icons/` | Polished UX |
| 14 | Package with PyInstaller | `scripts/package.py` | `.exe` (Windows) |
| 14 | Final testing, create installer | `dist/` | Ready to distribute |

---

## 7. KEY IMPLEMENTATION DETAILS

### Renode Bridge (Critical Code)
```python
# src/core/renode_bridge.py
import subprocess
import tempfile
from pathlib import Path

class RenodeBridge:
    def __init__(self):
        self.process = None
        self.log_file = None
        
    def start(self, platform_file: Path, firmware_file: Path):
        """Start Renode with given platform and firmware."""
        # Create temporary Renode script
        script = f"""
            include @{platform_file}
            sysbus LoadELF @{firmware_file}
            start
        """
        self.log_file = tempfile.NamedTemporaryFile(mode='w', suffix='.log')
        
        self.process = subprocess.Popen(
            ['renode', '--disable-xwt', '--port', '1234'],
            stdin=subprocess.PIPE,
            stdout=self.log_file,
            stderr=subprocess.STDOUT
        )
        
    def inject_fault(self, fault_id: str, params: dict):
        """Inject fault via Renode's monitor port."""
        command = self._build_fault_command(fault_id, params)
        self.process.stdin.write(f"{command}\n".encode())
        self.process.stdin.flush()
        
    def read_sensor(self, sensor_path: str) -> float:
        """Read sensor value from Renode."""
        # Use Renode's Python API or monitor commands
        pass
        
    def stop(self):
        """Gracefully shutdown Renode."""
        if self.process:
            self.process.stdin.write(b"quit\n")
            self.process.wait(timeout=10)
```

### Campaign Runner (Async with QThread)
```python
# src/core/test_runner.py
from PyQt6.QtCore import QThread, pyqtSignal
from dataclasses import dataclass

class TestRunner(QThread):
    progress = pyqtSignal(int, int)  # current, total
    result = pyqtSignal(TestResult)
    log = pyqtSignal(str, str)  # level, message
    
    def __init__(self, campaign: Campaign):
        super().__init__()
        self.campaign = campaign
        self.renode = RenodeBridge()
        
    def run(self):
        total = len(self.campaign.faults)
        for i, fault in enumerate(self.campaign.faults):
            self.progress.emit(i + 1, total)
            self.log.emit("INFO", f"Starting {fault.id}")
            
            # Run test
            result = self._run_single_test(fault)
            self.result.emit(result)
            
    def _run_single_test(self, fault: Fault) -> TestResult:
        self.renode.start(self.campaign.platform, self.campaign.firmware)
        self.renode.inject_fault(fault.id, fault.params)
        
        # Monitor for expected behavior
        detected = self._wait_for_detection(fault, timeout=5.0)
        recovered = self._check_recovery(fault)
        safe = self._check_safety()
        
        self.renode.stop()
        
        return TestResult(
            fault_id=fault.id,
            detected=detected,
            recovered=recovered,
            safe=safe,
            resilience_index=self._calculate_ri(detected, recovered, safe)
        )
```

### Main Window Controller
```python
# src/main_window.py
from PyQt6.QtWidgets import QMainWindow, QDockWidget
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RenodeResilience v1.0")
        self.setMinimumSize(1400, 900)
        
        # Central stacked widget
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)
        
        # Add screens
        self.central_stack.addWidget(WelcomeScreen())
        self.central_stack.addWidget(CampaignEditor())
        self.central_stack.addWidget(TestRunnerView())
        self.central_stack.addWidget(ReportViewer())
        self.central_stack.addWidget(ComparisonView())
        
        # Sidebar dock
        self.sidebar = QDockWidget("Navigation", self)
        self.sidebar.setWidget(Sidebar())
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar)
        
        # Properties dock
        self.properties = QDockWidget("Properties", self)
        self.properties.setWidget(PropertyPanel())
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties)
        
        # Console dock (bottom)
        self.console = QDockWidget("Console", self)
        self.console.setWidget(ConsoleOutput())
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.console)
        
        # Status bar
        self.statusBar().showMessage("Ready")
```

---

## 8. PACKAGING & DISTRIBUTION

| Platform | Output | Tool | Size |
|---|---|---|---|
| **Windows** | `RenodeResilience-1.0.0-setup.exe` | PyInstaller + NSIS | ~150MB |
| **macOS** | `RenodeResilience-1.0.0.dmg` | PyInstaller + create-dmg | ~180MB |
| **Linux** | `RenodeResilience-1.0.0.AppImage` | PyInstaller + appimagetool | ~160MB |

**Bundled Dependencies:**
- Python 3.11 runtime
- PyQt6 libraries
- Renode (portable)
- All Python packages (frozen)

---

## 9. DELIVERABLES CHECKLIST

- [ ] **Desktop App** — Installable on Windows/macOS/Linux
- [ ] **5 Built-in Examples** — STM32 sensor, motor, CAN, power, communication
- [ ] **27 Fault Types** — All injectable via GUI
- [ ] **Live Test Runner** — Real-time progress, charts, logs
- [ ] **Report Generator** — HTML, PDF, JSON, JUnit XML
- [ ] **Comparison Tool** — Side-by-side run analysis
- [ ] **Dark Theme** — Professional appearance
- [ ] **Demo Video** — 5-minute screen recording
- [ ] **User Guide** — PDF manual
- [ ] **GitHub Repo** — Open source, MIT license

---

## 10. WHY THIS DESKTOP APP WINS

| Factor | Desktop (PyQt6) | Web (React) |
|---|---|---|
| Renode Integration | Native process, zero latency | Requires server wrapper, fragile |
| Firmware Security | Local only, no upload | Risk of cloud exposure |
| Performance | Direct memory access, 60fps charts | Browser overhead, network lag |
| Offline Use | Full functionality | Requires server |
| Embedded Engineer Trust | ✅ Standard tool pattern | ❌ Unusual for embedded |
| Packaging | Single `.exe`, double-click run | Server deployment complexity |

**Build the desktop app. It's what embedded engineers actually want.**