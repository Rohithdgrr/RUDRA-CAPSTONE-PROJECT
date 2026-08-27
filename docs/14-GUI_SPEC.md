# 14 — GUI Specification (PyQt6)

> **Framework:** PyQt6 6.6+ | **Version:** 1.5 | **Screens:** 5 | **Icons:** 20 vector

## 1. Window Structure

`src/main_window.py:MainWindow(QMainWindow)` — `1400×900 min`, title `RenodeResilience v1.5`.

```
┌──────────────────────────────────────────────────────────────────┐
│ QMainWindow                                                      │
│ ┌──────┬───────────────────────────────────┬──────────────────┐ │
│ │Side- │   QStackedWidget (Central)         │ Properties       │ │
│ │bar   │  0: Welcome (WelcomeScreen)        │ 280px (QDock)    │ │
│ │220px │  1: CampaignEditor                 │ Fault Params     │ │
│ │Icons │  2: TestRunnerView                 │ RI Weights       │ │
│ │      │  3: Report+Charts                  │ Platform Info    │ │
│ │      │  4: ComparisonView                 │                  │ │
│ │      │                                    │                  │ │
│ ├──────┴───────────────────────────────────┴──────────────────┤ │
│ │ Console QDock Bottom 120px QTextEdit color-coded timestamps │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ StatusBar: Ready | Renode: idle                                   │
└──────────────────────────────────────────────────────────────────┘
```

Docks: `QDockWidget` Left `Sidebar` 220px, Right `Properties` 280px, Bottom `Console` 120px.

## 2. Screen Inventory

### Screen 0: Welcome (`WelcomeScreen`)
- **Hero:** "RUDRA" brand (blue, 36pt Black), tagline, description.
- **Quick Actions:** 4 cards with vector icons — New Campaign (+), Run Demo (▶), Open Report (📊), Compare Runs (↔).
- **Recent Campaigns:** 3 cards with campaign icons, fault count, RI/Grade, date.
- **Footer:** Version, capabilities.

### Screen 1: Campaign Designer (`CampaignEditor`)
- **General Settings:** `QGroupBox` with `QFormLayout` — Campaign name, Firmware Browse (ELF validation), Platform `QComboBox`, Duration `QSpinBox`, Parallel `QSpinBox`.
- **Fault Selection:** `QGroupBox` with 27-row `QTableWidget` — columns: checkbox, Fault ID, Type, Severity (colored). Select All / Clear buttons.
- **Actions:** `Run Campaign` (play icon) + `Save` (save icon) buttons.
- **Files:** `src/gui/widgets/campaign_editor.py`

### Screen 2: Test Runner (`TestRunnerView`)
- **Summary Cards:** 4 `QFrame` cards — Total (blue), Passed (green), Failed (red), RI (purple).
- **Progress:** `QProgressBar` with gradient chunk (blue→purple) + ETA label.
- **Table:** `QTableWidget` 8 columns — #, Fault ID, Status (colored bg), Detection, Recovery, Safety, RI (colored), Duration.
- **Controls:** Pause (⏸ icon) + Stop (■ icon, red) buttons.
- **Files:** `src/gui/widgets/test_runner_view.py`

### Screen 3: Report Viewer (`ReportViewer`)
- **Charts Row:** `QFrame` with 3 charts — RI Gauge (donut arc), Pass/Fail Pie (donut), Category Radar (horizontal bars).
- **Export Buttons:** PDF (📄), HTML ({ }), JSON ({ }), JUnit (📊) with icons.
- **Summary Banner:** RI/100, Grade (colored), Campaign Name, Pass/Fail stats.
- **HTML Report:** `QTextBrowser` with metrics cards.
- **Findings Panel:** `QTextBrowser` with red-bordered fault cards + recommendations.
- **Files:** `src/gui/widgets/report_viewer.py`, `charts/*`

### Screen 4: Comparison View (`ComparisonView`)
- **Summary Cards:** 4 cards — Baseline RI (blue), Optimized RI (purple), Delta (green/red), Improvement % (yellow).
- **Table:** `QTableWidget` 5 columns — Fault ID, Baseline RI, Optimized RI, Delta (colored ±), Status (IMPROVED/REGRESSED/SAME).
- **Files:** `src/gui/widgets/comparison_view.py`

### Settings Dialog (`SettingsDialog`)
- **Renode:** Executable path, Monitor Port.
- **Appearance:** Theme (Dark/Light) combo, Font Size combo.
- **Campaign Defaults:** Auto-save checkbox, Console output checkbox.
- **Files:** `src/gui/widgets/dialogs/settings_dialog.py`

## 3. Icons (Vector)

20 programmatic vector icons via `src/gui/utils/icons.py` — `QPainter` on `QPixmap`, no external assets:

| Icon | Used For |
|------|----------|
| `home` | Dashboard nav |
| `campaign` | Campaigns, recent items |
| `report` | Reports, JUnit export |
| `compare` | Compare nav |
| `new` | New Campaign (+) |
| `open` | Open Campaign (folder) |
| `save` | Save (floppy) |
| `recent` | Recent (clock) |
| `template` | Templates (grid) |
| `firmware` | Firmware (chip) |
| `load` | Load ELF (download) |
| `select` | Select Target (checkmark) |
| `build` | Build (hammer) |
| `verify` | Verify (badge) |
| `platform` | Platforms (monitor) |
| `settings` | Settings (gear) |
| `play` | Run (triangle) |
| `stop` | Stop (square) |
| `pause` | Pause (bars) |
| `pdf` | Export PDF (document) |

## 4. Themes

### Dark Theme (`dark_theme.qss`)
- Background: `#0F0F1A`, Surface: `#16162A`, Border: `#27273A`
- Text: `#D4D4D8`, Muted: `#71717A`, Brand: `#3B82F6`
- 200+ QSS rules covering all widgets

### Light Theme (`light_theme.qss`)
- Background: `#F8FAFC`, Surface: `#FFFFFF`, Border: `#E5E7EB`
- Text: `#1F2937`, Muted: `#9CA3AF`, Brand: `#3B82F6`
- 150+ QSS rules

### Switching
- **View → Theme → Dark/Light** menu toggle
- `MainWindow._set_theme()` loads QSS file and applies via `app.setStyleSheet()`
- `settings_dialog.py` also has theme selector

## 5. Charts

| Chart | File | Implementation |
|-------|------|----------------|
| RI Gauge | `charts/ri_gauge.py` | Custom `paintEvent` donut arc with grade color |
| Pass/Fail Pie | `charts/pass_fail_pie.py` | Custom `paintEvent` donut (red/green) |
| Category Radar | `charts/category_radar.py` | Custom `paintEvent` horizontal bars (6 categories) |
| Timeline | `charts/timeline_chart.py` | PyQtGraph line plot (optional) |
| Heatmap | `charts/fault_heatmap.py` | Colored `QTableWidget` |

## 6. Console

`src/gui/widgets/console_output.py` — `QTextEdit` read-only, `QFont("Cascadia Code", 11)`, color-coded timestamps, level icons (ℹ✓✗⚠⚙☢), 10k line cap with auto-trim.

## 7. Performance

- Lazy widget init (screens created at startup, switched via `QStackedWidget`)
- Log rotation 10k lines via cursor trimming
- Vector icons cached as `QPixmap` per icon function call

## 8. Packaging

PyInstaller → `.exe/.dmg/.AppImage` per `19-PACKAGING.md`.
