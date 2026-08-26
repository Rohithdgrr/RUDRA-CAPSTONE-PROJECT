# 04 — User Guide (8-Step Workflow)

> **Source:** `README.md:426-495`, `desktop-application.md:99-253` screens

## Overview Flow

```
START → 1.Create Project → 2.Configure Platform → 3.Design Campaign → 4.Run Tests → 5.Analyze → 6.Report & Export → 7.Compare → 8.Iterate → DONE
```

## Step 1: Project Creation
- Launch `python -m src.main` → WelcomeScreen (`src/gui/widgets/*`, `resources/ui/main_window.ui`).
- **New Project** or Recent (`sensor_suite RI 73`) or Template: `STM32 Sensor`, `Motor Controller`, `CAN Bus`, `Power Management`, `Communication Stack` (`desktop-application.md:107-114`).
- Project stored as folder with `campaign.yaml` + `results/`.

## Step 2: Platform Configuration
- Dropdown: `STM32F4 Discovery`, `nRF52840 DK`, `HiFive1 RISC-V` (`07-PLATFORM_GUIDE.md`).
- **Upload ELF:** Browse → validate arch/entry point (ELF magic check in `campaign.py`). Shows `STM32F407, 128KB` metadata.
- Auto-detect: firmware size, symbols if `arm-none-eabi-readelf` available.
- Settings → Renode path override if not on PATH.

## Step 3: Campaign Design (`CampaignEditor`)
Fields (`desktop-application.md:125-158`):
- Name, Firmware path, Platform, Duration (60s), Parallel (1-8 workers)
- Fault Selection checkboxes by category (Sensor/Timing/Comm/Memory/Power/GPIO) → Selected Faults table `ID | Type | Severity | Duration | Target`
- Expected Behavior per fault: e.g. `SF-01 → detect_stuck_sensor() within 5000ms`, `SF-02 → std_dev <2.0`
- Scoring Weights sliders `Detection 40% Recovery 30% Safety 30%` + Min Grade `B (70)`
- Save → `campaign.yaml` (validated via `05-CAMPAIGN_SCHEMA.md`).

## Step 4: Test Execution (`TestRunnerView`)
- Click **Run Campaign** → `RenodeBridge.start()` via `QProcess`, `include @platform` + `LoadELF` + `start`.
- Scheduler: sequential or parallel `QThreadPool 4` (`src/core/test_runner.py`).
- Live: Progress `[████████░░] 12/27 ETA 8min`, Results table `ID Fault Status Detect Recover Safety RI`, Charts line/bar/pie (PyQtGraph 60fps), Console color-coded (`console_output.py`).
- Controls: **Pause/Stop** → `RenodeBridge.stop(graceful=True)` → `quit` + `wait(10)` + `kill` (`01-ARCHITECTURE.md`).

## Step 5: Analysis (Auto-switch to ReportViewer)
- Cards: Overall RI `69/100 Grade C Marginal` + counts `Pass 15 Fail 8 Warning 4 Total 27`.
- Critical Findings list with icons ⚠/❌ + recommendations (see `09-DIAGNOSIS_ENGINE.md`).
- Charts: Radar 6 categories, Heatmap fault×score, Timeline latency — `src/gui/widgets/charts/*`.

## Step 6: Reporting & Export
- Buttons: `Export PDF` (audit), `Export HTML` (interactive), `Export JSON` (CI/CD), `Export JUnit XML` (Jenkins) — `10-REPORT_SPEC.md`.
- `View Full Report in Browser` (`QWebEngineView`), `Compare with Previous Run`.

## Step 7: Comparison (`ComparisonView`)
- Load two results: Baseline `RI 45 D Pass 8/27` vs Optimized `RI 73 B Pass 19/27` → Improvement `+28 (+62%)`.
- Delta table per fault `Baseline | Optimized | Delta +75 ✅`; Key Changes list (e.g. median filter added) — `desktop-application.md:226-253`.

## Step 8: Iterate & Fix
- Engineer patches firmware per `Fix recommendations with code examples` (`README.md:512`).
- Re-run campaign → compare before/after to verify improvement → repeat until Grade ≥B (objective 7).

## Tips

- Keep campaign YAML under git; `campaigns/private/` gitignored for sensitive paths.
- Console keeps 10k lines; older archived — see `18-TROUBLESHOOTING.md` disk 100MB logs.
- For CI headless, use `11-CLI_REFERENCE.md` instead of GUI; same `campaign.yaml`.
