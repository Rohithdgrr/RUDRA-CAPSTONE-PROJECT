# Changelog

> Format: Keep a Changelog | Versioning: SemVer

## [1.0.0] — 2026-08-26 (Planned)

### Added
- Core engine: `RenodeBridge`, `FaultInjector` 27 faults (6 categories), `Campaign`, `TestRunner` parallel 4, `ResultAggregator`, `ResilienceIndex RI=(D*0.4)+(Rec*0.3)+(S*0.3)` Grade A-F, `DiagnosisEngine` rule-based, `ReportGenerator` HTML/PDF/JSON/JUnit — per `README.md:185-195`.
- GUI: PyQt6 `QMainWindow 1400×900` with Sidebar/StackedWidget/Properties/Console/StatusBar + 5 screens Welcome/CampaignEditor/TestRunner/ReportViewer/ComparisonView + PyQtGraph charts @60fps — `docs/14-GUI_SPEC.md`.
- Platforms: STM32F4 Discovery, nRF52840 DK, HiFive1 RISC-V `.repl` — `docs/07-PLATFORM_GUIDE.md`.
- API: FastAPI `POST /run /campaign`, `GET /status /report /faults /platforms`, `WS /live` — `docs/13-API_REST.md`.
- CLI: `renode-resilience run|campaign|report|compare` Typer — `docs/11-CLI_REFERENCE.md`.
- SDK: `Campaign.from_yaml().run()` — `docs/12-SDK_GUIDE.md`.
- Docs: PRD `README.md` + `desktop-application.md` + `docs/00-INDEX`…`19-PACKAGING` + `adr/001-003`.
- Packaging: PyInstaller `.exe/.dmg/.AppImage` ~150MB — `docs/19-PACKAGING.md`.

### Known Limitations
- 3 boards only; other `.repl` custom (`README.md:716`).
- Rule-based diagnosis only; ML v1.1.

## [1.1.0] — Planned (1-2 months, `README.md:758-763`)

- Platforms ESP32, RP2040, SAMD21; faults EMI/temp drift/clock domain; ML diagnosis `scikit-learn`; plugin system; VS Code extension.

## [2.0.0] — Planned (3-6 months, `README.md:765-771`)

- Distributed testing, cloud dashboard optional, fuzzing AFL/libFuzzer, RTOS-aware (FreeRTOS/Zephyr), hardware trace correlation.

## [3.0.0] — Planned (6-12 months, `README.md:773-776`)

- AI-generated fixes LLM, formal verification SPIN/UPPAAL bridge, TÜV ISO 26262 tool qualification, Enterprise LDAP/audit/multi-user.

## Unreleased

- No changes yet; track in PRs.
