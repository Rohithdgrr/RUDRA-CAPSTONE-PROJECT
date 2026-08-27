# RenodeResilience — Documentation Index

> **Version:** 1.5.0 | **Last Updated:** 2026-08-27 | **Status:** Complete

Master table of contents. Read in order for first-time setup; jump via category for reference.

## Reading Order (First Time)

| Step | Document | Purpose | Est. Time |
|------|----------|---------|-----------|
| 1 | `01-ARCHITECTURE.md` | System layers, component interaction | 15 min |
| 2 | `02-INSTALL.md` | Prerequisites, Renode 1.15+ (tested 1.16.1), Python 3.11+ | 10 min |
| 3 | `03-QUICKSTART.md` | First campaign in 10 minutes (ELF → RI) | 10 min |
| 4 | `06-FAULT_CATALOG.md` | 27 fault types, params, Renode commands | 20 min |
| 5 | `05-CAMPAIGN_SCHEMA.md` | YAML schema, Pydantic validation | 15 min |
| 6 | `08-RESILIENCE_INDEX.md` | RI formula, weights, Grade A-F | 10 min |
| 7 | `04-USER_GUIDE.md` | Full 8-step workflow | 20 min |
| 8 | `14-GUI_SPEC.md` | 5 screens, vector icons, dark/light themes | 15 min |

## By Category

### Core Concepts
- `01-ARCHITECTURE.md` — High-level architecture, module breakdown `src/core/*`, `src/gui/*`
- `08-RESILIENCE_INDEX.md` — `RI = (D×0.4)+(Rec×0.3)+(S×0.3)` 0-100
- `06-FAULT_CATALOG.md` — Taxonomy: 27 canonical IDs (Sensor 7 + Timing 5 + Comm 6 + Memory 4 + Power 3 + GPIO 2)
- `09-DIAGNOSIS_ENGINE.md` — Rule-based classifier + fix recommendations, ISO 26262 / DO-178C mapping

### Campaign & Platform
- `05-CAMPAIGN_SCHEMA.md` — `Campaign.from_yaml()` spec, scoring weights/thresholds with ordering validation
- `07-PLATFORM_GUIDE.md` — STM32F4 Discovery, nRF52840 DK, HiFive1 RISC-V `.repl` files

### User Facing
- `02-INSTALL.md` — Windows/macOS/Linux install, `renode --version`, venv
- `03-QUICKSTART.md` — `renode-resilience run --firmware sensor.elf --fault SF-01`
- `04-USER_GUIDE.md` — Project → Platform → Campaign → Run → Analyze → Report → Compare → Iterate
- `14-GUI_SPEC.md` — Welcome screen, Campaign Designer, Test Runner, Report Viewer, Comparison View with vector icons and theme switching
- `15-STYLE_GUIDE.md` — Dark/Light themes, vector icon system, color palette
- `10-REPORT_SPEC.md` — HTML/PDF/JSON/JUnit XML
- `18-TROUBLESHOOTING.md` — Port 1234, zombie Renode, log bloat, YAML errors

### Integration
- `11-CLI_REFERENCE.md` — `renode-resilience run|campaign|report|compare`
- `12-SDK_GUIDE.md` — `from renode_resilience import Campaign`
- `13-API_REST.md` — FastAPI `POST /api/v1/run`, `WS /api/v1/live/{run_id}`

### Maintainer
- `16-SECURITY.md` — Threat model, path traversal prevention, sandboxing
- `17-TESTING.md` — pytest 27 tests, Robot Framework
- `19-PACKAGING.md` — PyInstaller `.exe`/`.dmg`/`.AppImage`, ~150MB

### Decisions
- `00-PRD.md` — Full product requirements document (860 lines)
- `adr/001-pyqt6-vs-electron.md` — Why Desktop PyQt6 wins (93% local-tool preference)
- `adr/002-renode-bridge-qprocess.md` — QProcess vs pyrenode3
- `adr/003-scoring-weights.md` — Why 40/30/30

## File Map

```
src/
├── core/
│   ├── campaign.py              → 05-CAMPAIGN_SCHEMA
│   ├── renode_bridge.py         → 01-ARCHITECTURE, 07-PLATFORM_GUIDE
│   ├── fault_injector.py        → 06-FAULT_CATALOG
│   ├── resilience_index.py      → 08-RESILIENCE_INDEX
│   ├── result_aggregator.py     → 01-ARCHITECTURE
│   ├── diagnosis_engine.py      → 09-DIAGNOSIS_ENGINE
│   ├── report_generator.py      → 10-REPORT_SPEC
│   └── test_runner.py           → 01-ARCHITECTURE
├── gui/
│   ├── main_window.py           → 14-GUI_SPEC
│   ├── app.py                   → 14-GUI_SPEC
│   ├── utils/icons.py           → 15-STYLE_GUIDE
│   ├── widgets/
│   │   ├── sidebar.py           → 14-GUI_SPEC
│   │   ├── campaign_editor.py   → 14-GUI_SPEC
│   │   ├── test_runner_view.py  → 14-GUI_SPEC
│   │   ├── report_viewer.py     → 14-GUI_SPEC
│   │   ├── comparison_view.py   → 14-GUI_SPEC
│   │   ├── console_output.py    → 14-GUI_SPEC
│   │   ├── property_panel.py    → 14-GUI_SPEC
│   │   └── charts/              → 14-GUI_SPEC
│   └── styles/
│       ├── dark_theme.qss       → 15-STYLE_GUIDE
│       └── light_theme.qss      → 15-STYLE_GUIDE
├── config/
│   ├── schemas.py               → 05-CAMPAIGN_SCHEMA
│   └── defaults.py              → 01-ARCHITECTURE
├── cli.py                       → 11-CLI_REFERENCE
└── api/app.py                   → 13-API_REST
resources/platforms/*.repl       → 07-PLATFORM_GUIDE
```

## Conventions

- All paths relative to repo root.
- Version pin: Renode 1.15+ (tested 1.16.1), PyQt6 6.6+, Python 3.11+.
- 27 unit tests pass (`pytest tests/unit/ -v`).
- GUI: 20 programmatic vector icons, dark/light theme switching via View menu.

## Status Legend

| Icon | Meaning |
|------|---------|
| ✅ | Complete, reviewed |
| 🚧 | Draft, needs review |
| ⏳ | Planned (v1.1+) |
