# RenodeResilience — Documentation Index

> **Version:** 1.0.0 | **Last Updated:** 2026-08-26 | **Status:** Draft

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
| 8 | `14-GUI_SPEC.md` | 5 screens, layouts, QSS | 15 min |

## By Category

### Core Concepts
- `01-ARCHITECTURE.md` — High-level architecture, module breakdown `src/core/*`, `src/gui/*`
- `08-RESILIENCE_INDEX.md` — `RI = (D×0.4)+(Rec×0.3)+(S×0.3)` 0-100
- `06-FAULT_CATALOG.md` — Taxonomy: 27 canonical IDs (PRD table lists 31; normalized: Sensor 7 + Timing 5 + Comm 6 + Memory 4 + Power 3 + GPIO 2) — see renode-test proofs
- `09-DIAGNOSIS_ENGINE.md` — Rule-based classifier + fix recommendations, ISO 26262 / DO-178C mapping

### Campaign & Platform
- `05-CAMPAIGN_SCHEMA.md` — `Campaign.from_yaml()` spec, scoring weights/thresholds
- `07-PLATFORM_GUIDE.md` — STM32F4 Discovery, nRF52840 DK, HiFive1 RISC-V `.repl` files

### User Facing
- `02-INSTALL.md` — Windows/macOS/Linux install, `renode --version`, venv
- `03-QUICKSTART.md` — `renode-resilience run --firmware sensor.elf --fault SF-01`
- `04-USER_GUIDE.md` — Project → Platform → Campaign → Run → Analyze → Report → Compare → Iterate
- `14-GUI_SPEC.md` — Welcome, Campaign Designer, Test Runner, Report Viewer, ComparisonView
- `15-STYLE_GUIDE.md` — Dark theme QSS, color codes PASS `#4CAF50` FAIL `#F44336`
- `10-REPORT_SPEC.md` — HTML/PDF/JSON/JUnit XML via Jinja2 + WeasyPrint
- `18-TROUBLESHOOTING.md` — Port 1234, zombie Renode, log bloat, YAML errors

### Integration
- `11-CLI_REFERENCE.md` — `renode-resilience run|campaign|report|compare`
- `12-SDK_GUIDE.md` — `from renode_resilience import Campaign`
- `13-API_REST.md` — FastAPI `POST /api/v1/run`, `WS /api/v1/live/{run_id}`

### Maintainer
- `16-SECURITY.md` — Threat model, sandboxing, AES-256 reports
- `17-TESTING.md` — pytest, Robot Framework, 90% coverage
- `19-PACKAGING.md` — PyInstaller `.exe`/`.dmg`/`.AppImage`, ~150MB

### Decisions
- `adr/001-pyqt6-vs-electron.md` — Why Desktop PyQt6 wins (93% local-tool preference)
- `adr/002-renode-bridge-qprocess.md` — QProcess vs pyrenode3
- `adr/003-scoring-weights.md` — Why 40/30/30

## File Map Alignment

```
renode-resilience/
├── src/core/renode_bridge.py      → 01-ARCHITECTURE, 07-PLATFORM_GUIDE
├── src/core/fault_injector.py     → 06-FAULT_CATALOG
├── src/core/campaign.py           → 05-CAMPAIGN_SCHEMA
├── src/core/resilience_index.py   → 08-RESILIENCE_INDEX
├── src/core/diagnosis_engine.py   → 09-DIAGNOSIS_ENGINE
├── src/core/report_generator.py   → 10-REPORT_SPEC
├── src/gui/widgets/*              → 14-GUI_SPEC
├── src/gui/styles/dark_theme.qss  → 15-STYLE_GUIDE
└── resources/platforms/*.repl     → 07-PLATFORM_GUIDE
```

## Conventions

- All paths relative to repo root `/`.
- Code snippets reference `file_path:line_number` where applicable.
- Version pin: Renode 1.15+ (tested 1.16.1 via `renode-docker/Dockerfile:8` + `renode/README.md:36`), PyQt6 6.6+, Python 3.11+. Vendor dirs `renode/`, `pyrenode3/`, `renode-docker/`, `renode-test-action/` vendored for substrate reference.

## Status Legend

| Icon | Meaning |
|------|---------|
| ✅ | Complete, reviewed |
| 🚧 | Draft, needs review |
| ⏳ | Planned (v1.1+) |
