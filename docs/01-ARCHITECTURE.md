# 01 — Architecture

> **Source:** `README.md:65-147`, `desktop-application.md:22-72` expanded

## 1. High-Level Stack

```
User → GUI (PyQt6 QMainWindow 1400×900) → Core Engine → Renode Bridge (QProcess :1234) → Renode Core → Firmware ELF
                          ↓                    ↓                ↓
                      Campaign YAML        Fault Taxonomy   Monitor Port / Python API
                          ↓                    ↓                ↓
                      Scheduler (QThreadPool)  Injector    Peripheral Hooks (I2C/SPI/UART/CAN/GPIO)
                          ↓                    ↓                ↓
                      Aggregator ←────── Sensor/Timer/Comm Values
                          ↓
                      RI Calculator → Diagnosis → Report Generator → HTML/PDF/JSON/JUnit
```

## 2. Layer Breakdown

### Presentation Layer — `src/gui/` (PyQt6)
| Widget | File | Role |
|--------|------|------|
| Main Window | `src/main_window.py` | `QMainWindow` with `WelcomeScreen`, `QStackedWidget` (5 screens), 3 `QDockWidget`, theme switching |
| Welcome Screen | `src/main_window.py:WelcomeScreen` | Hero branding, quick-action cards with icons, recent campaigns |
| Sidebar | `src/gui/widgets/sidebar.py` | Vector icons, section headers, hover/active states, 220px fixed |
| Campaign Editor | `src/gui/widgets/campaign_editor.py` | 27-fault checkbox table with severity colors, form layout, ELF validation |
| Test Runner | `src/gui/widgets/test_runner_view.py` | Summary cards, gradient progress bar, 8-col table with colored status |
| Report Viewer | `src/gui/widgets/report_viewer.py` | Summary banner, HTML report, findings panel with red-bordered cards |
| ComparisonView | `src/gui/widgets/comparison_view.py` | Delta cards, 5-col table with improvement/regression coloring |
| Console | `src/gui/widgets/console_output.py` | `QTextEdit` monospace, timestamps, level icons, 10k line cap |
| Property Panel | `src/gui/widgets/property_panel.py` | Fault params, RI weights, platform info |
| Charts | `src/gui/widgets/charts/*` | RI gauge (donut arc), pass/fail pie (donut), category radar (bars), timeline, heatmap |
| Icons | `src/gui/utils/icons.py` | 20 programmatic vector icons via `QPainter`, no external assets |
| Styles | `src/gui/styles/` | `dark_theme.qss` (200+ rules), `light_theme.qss` (150+ rules) |

Layout: Sidebar 250px | Central StackedWidget | Properties 250px | Bottom Console 200px | StatusBar `Renode ● Running | Tests 12/27 | RI 73/100 | Grade B` — see `desktop-application.md:30-62`.

### API Layer — `src/api/` (FastAPI) — Headless Mode
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/run` | POST | Single fault test |
| `/api/v1/campaign` | POST | Full campaign YAML/JSON |
| `/api/v1/status/{run_id}` | GET | `{status, progress, total}` |
| `/api/v1/result/{run_id}` | GET | Result JSON |
| `/api/v1/report/{run_id}?format=html|pdf|json` | GET | File download |
| `/api/v1/compare` | POST | `{baseline, optimized}` → `ComparisonReport` |
| `/api/v1/faults` | GET | 27 fault definitions |
| `/api/v1/platforms` | GET | `["stm32f4","nrf52840","riscv_hifive1"]` |
| `WS /api/v1/live/{run_id}` | WS | `test.started/progress/result/completed` events |

### Core Engine — `src/core/` (Python 3.11+)
| Module | File | Responsibility |
|--------|------|----------------|
| Renode Bridge | `src/core/renode_bridge.py` | `start(platform,fw)→bool`, `inject_fault(id,params)→bool`, `read_peripheral(path)→value`, `stop()` via `subprocess.Popen --disable-xwt --port 1234`, path traversal prevention, resource cleanup |
| Fault Injector | `src/core/fault_injector.py` | 27 IDs → Renode monitor commands, formatted params (not dict repr) |
| Campaign Manager | `src/core/campaign.py` | `Campaign.from_yaml()`, Pydantic validation, parallel execution with exception handling, configurable WARNING thresholds |
| Test Runner | `src/core/test_runner.py` | `QThread` with stop support, signals `progress/result/log/finished_campaign` |
| Result Aggregator | `src/core/result_aggregator.py` | `TestResult`, `CampaignResult`, `ComparisonResult`, standalone `compare_results()` |
| Resilience Index | `src/core/resilience_index.py` | `RI=(D×0.4)+(Rec×0.3)+(S×0.3)`, division-by-zero guard, Grade A-F |
| Diagnosis Engine | `src/core/diagnosis_engine.py` | 5 rule-based classifiers + recommendations + ISO 26262 mapping |
| Report Generator | `src/core/report_generator.py` | HTML (inline CSS), PDF (WeasyPrint), JUnit XML |

See `desktop-application.md:444-537` for critical code sketches.

### Renode Adapter — `resources/platforms/` (vendored `renode/platforms/`)
`stm32f4_discovery.repl` (`renode/platforms/boards/stm32f4_discovery.repl:1` → `using platforms/cpus/stm32f4.repl`), `nrf52840dk_nrf52840.repl`, `sifive-fe310.repl` (HiFive1) — verified `renode/platforms/cpus/stm32f4.repl:43` `cpu cortex-m4 nvic 0xE000E000`, `sram 0x20000000 256KB`, `flash 0x08000000 2MB`, peripherals `i2c1 0x40005400 can1 0x40006400 gpioPortA-K` (`07-PLATFORM_GUIDE.md:32`).

### Renode Core (External, `renode/` 1425 objects, MIT)
CPU Emulator, Memory Model (Flash/RAM), Peripheral Models — not built, just bridged. Flags `-P port -e COMMAND --console --disable-gui --hide-log` (`renode/README.md:161`). Docker `antmicro/renode:latest` (`renode/README.md:199`) + `renode-docker/Dockerfile:8` `1.16.1`.

### Firmware Under Test
User ELF/BIN + optional source maps + pytest/Robot harness.

## 3. Component Interaction Flow

| Phase | Flow |
|-------|------|
| Config | GUI `CampaignEditor` → `campaign.yaml` → `CampaignManager.validate()` (Pydantic) |
| Launch | `RenodeBridge.start()` → `subprocess.Popen(['renode','--disable-xwt','--port','1234'])` → `_wait_for_monitor(15s)` → `include @platform` + `sysbus LoadELF @fw` + `start` |
| Inject | `FaultInjector._build_fault_command(fault_id, params)` → `process.stdin.write(command+"\n")` |
| Observe | `read_peripheral("sysbus.i2c0.sensor0")` → poll expected behavior `detect_stuck_sensor()` within `timeout_ms` |
| Score | `ResultAggregator` → `ResilienceIndexCalculator` → `DiagnosisEngine.diagnose()` → `ReportGenerator.to_html/pdf/json/junit()` |
| Stream | `TestRunner(QThread)` emits `progress/log/result` → GUI live table + PyQtGraph (60fps) + WebSocket `WS /live` |

## 4. Threading & Perf

- `QThreadPool` (not multiprocessing): I/O-bound Renode, GIL acceptable; 4 concurrent workers target 100 faults/hr (`README.md:406`).
- Lazy widget init, Pandas chunking `pd.read_json(chunksize=1000)`, Jinja2 `bytecode_cache`, log rotation 10k lines (`README.md:416-421`).
- Memory <2GB, report <5s, campaign load <1s (`README.md:406-415`).

## 5. File Structure Reference

Full tree in `desktop-application.md:257-378`. Key:
```
src/main.py, app.py, main_window.py
src/core/{campaign,fault_injector,test_runner,result_aggregator,resilience_index,diagnosis_engine,report_generator,renode_bridge}.py
src/gui/widgets/{sidebar,campaign_editor,test_runner_view,report_viewer,comparison_view,console_output,fault_selector,property_panel}.py
src/config/{defaults,schemas,validator}.py
resources/{ui/*.ui, icons/*, templates/*.html, platforms/*.repl}
examples/{sensor-firmware,motor-controller,can-validator}/
tests/{unit,integration,gui}/
```

## 6. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Renode API changes (`README.md:805`) | Pin `1.15+` (tested `1.16.1` via `renode-docker/Dockerfile:8` + `renode/README.md:36`), abstraction layer `RenodeBridge` |
| Platform coverage limited 3 boards | Custom `.repl` docs in `07-PLATFORM_GUIDE.md` |
| Emulation 10-100x slower | Parallel 4 + chunked processing |
