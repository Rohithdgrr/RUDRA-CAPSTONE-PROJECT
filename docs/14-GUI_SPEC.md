# 14 — GUI Specification (PyQt6)

> **Framework:** PyQt6 6.6+, Qt Creator 6.6+, PyQtGraph 0.13+ | `desktop-application.md:99-253` mockups

## 1. Window Structure

`src/main_window.py:MainWindow(QMainWindow)` — `1400×900 min`, title `RenodeResilience v1.0`.

```
┌─────────────────────────────────────────────────────────────────┐
│ QMainWindow                                                     │
│ ┌────────┬──────────────────────────────────┬────────────────┐ │
│ │Sidebar │   QStackedWidget (Central)        │ Properties     │ │
│ │250px   │  Welcome → Designer → Runner →  │ 250px (QDock)  │ │
│ │QTree   │  Report → Compare               │ Fault Params   │ │
│ │        │                                  │ Expected Behav │ │
│ └────────┴──────────────────────────────────┴────────────────┘ │
│ ┌───────────────────────────────────────────────────────────────┐ │
│ │ Console QDock Bottom 200px QTextEdit monospace color-coded  │ │
│ └───────────────────────────────────────────────────────────────┘ │
│ StatusBar: Renode ● Running | Tests 12/27 | RI 73/100 | Grade B │
└─────────────────────────────────────────────────────────────────┘
```

Docks: `QDockWidget` Left `Sidebar`, Right `Properties`, Bottom `Console` — dockable/closable.

## 2. Screen Inventory

### Screen 1: Welcome / Project Browser (`WelcomeScreen`)
- Recent Projects: cards `▶ sensor_suite RI 73 2h ago`, `motor_ctrl RI45`, `can_validator RI91`.
- Templates panel: `STM32 Sensor, Motor Controller, CAN Bus, Power Management, Communication Stack` with radio.
- Actions: `[New] [Open Project] [Import Campaign]`.
- File: `src/gui/widgets/sidebar.py` + `resources/ui/main_window.ui`.

### Screen 2: Campaign Designer (`CampaignEditor`)
- Fields: Name `QLineEdit`, Firmware `Browse` + label `sensor.elf (STM32F407,128KB)`, Platform `QComboBox`, Duration `QSpinBox 1-3600`, Parallel `QSpinBox 1-8`.
- Fault Selection: Checkboxes by category (Sensor/Timing/Comm/Memory/Power/GPIO) → Selected Faults `QTableView` columns `ID Type Severity Duration Target`.
- Expected Behavior: `QTableView` rows `SF-01 → detect_stuck_sensor() within 5000ms`.
- Scoring: Sliders `Detection 40 Recovery 30 Safety 30` + Min Grade `QComboBox B(70)`.
- Actions: `[Run] [Save]` → validates Pydantic, writes `campaign.yaml`.
- Files: `src/gui/widgets/campaign_editor.py`, `fault_selector.py`, `property_panel.py`.

### Screen 3: Live Test Runner (`TestRunnerView`)
- Progress: `QProgressBar 12/27 (44%)` + ETA `8 min`.
- Live Results: `QTableView + PandasModel` columns `ID Fault Status Detect Recover Safety RI` with live update via `TestRunner.result` signal.
- Charts (PyQtGraph 60fps): Line `RI over time`, Bar `category scores`, Pie `Pass/Fail/Warning`.
- Console: `QTextEdit` appended via `TestRunner.log` signal: `[INFO] Campaign started | [PASS] SF-01 23ms | [FAIL] TF-01 | [WARN] CF-03`.
- Controls: `[Stop] [Pause ⏸]` → `RenodeBridge.stop()`.
- Files: `src/gui/widgets/test_runner_view.py`, `console_output.py`, `charts/*`.

### Screen 4: Report Viewer (`ReportViewer`)
- Tabs: `HTML` (`QWebEngineView`), `PDF` (Qt PDF), `JSON` (`QTableView`).
- Summary card: `Campaign RI 69 Grade C Marginal Pass 15 Fail 8 Warning 4`.
- Critical Findings: `QListView` ⚠/❌ with expandable recommendation (`diagnosis_engine`).
- Detailed Charts: Radar 6 categories, Heatmap, Timeline latency.
- Actions: `[Export PDF] [Export JSON] [View in Browser] [Compare]`.
- Files: `src/gui/widgets/report_viewer.py`, `charts/*`, `resources/templates/*`.

### Screen 5: ComparisonView
- Two cards `Baseline RI45 D Pass8/27` vs `Optimized RI73 B Pass19/27` + Improvement `+28 (+62%)`.
- Delta table `Fault | Baseline | Optimized | Delta +75 ✅`.
- Key Changes list bullet 1-3.
- File: `src/gui/widgets/comparison_view.py`.

### Screen 6: Settings (`SettingsDialog`)
- Renode path, Theme `dark/light`, Default weights, Export paths, API token — Pydantic-backed `src/config/schemas.py`.

## 3. Styling

- Dark-first QSS `src/gui/styles/dark_theme.qss` + `light_theme.qss` (see `15-STYLE_GUIDE.md`).
- Icons `resources/icons/app_icon_*.png`, SVG scalable.
- Color coding: PASS `#4CAF50`, FAIL `#F44336`, WARNING `#FF9800`, INFO `#2196F3`, Grades A `#2ECC71` B `#3498DB` C `#F1C40F` D `#E67E22` F `#E74C3C`.

## 4. Interaction

- Drag-and-drop campaign designer (faults reorder).
- Shortcuts: `Ctrl+N` New, `Ctrl+O` Open, `Ctrl+S` Save, `Ctrl+R` Run, `Ctrl+E` Export.
- Tooltips per fault ID (from `06-FAULT_CATALOG.md`).

## 5. Performance

- Lazy widget init (screens created on first access), PyQtGraph GPU, Pandas `QTableView`, log rotation 10k lines — matches `README.md:416-421`.

## 6. Packaging

PyInstaller → `.exe/.dmg/.AppImage` per `19-PACKAGING.md`; Qt Designer `.ui` compiled via `pyuic6`.
