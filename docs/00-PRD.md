# RenodeResilience — Product Requirements Document (PRD)

> **Version:** 1.0.0 | **Status:** Complete | **Last Updated:** 2026-08-26

This is the full PRD for the RenodeResilience capstone project. For quick reference, see the [README](../README.md) and [Documentation Index](00-INDEX.md).

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
Embedded firmware failures in the field cost manufacturers billions in recalls, liability, and reputation damage.

| Problem | Impact |
|---|---|
| Hardware-in-the-Loop (HIL) testing is expensive | Physical fault injection rigs cost $50K-$200K per setup |
| Unit tests don't catch hardware-fault scenarios | Mocked sensors/timers don't behave like real failing hardware |
| No quantitative resilience metric exists | Teams say "it feels robust" but can't measure it |
| Debugging field failures is reactive | Bugs are found by customers, not before shipment |
| Safety standards lack automated verification | ISO 26262/DO-178C compliance is manual and error-prone |
| Renode has no structured testing layer | The emulator exists, but no framework automates fault campaigns on top of it |

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
| 3 | Compute Resilience Index (0-100) | RI = (D*0.4) + (Rec*0.3) + (S*0.3) |
| 4 | Generate diagnosis reports | HTML, PDF, JSON, JUnit XML outputs |
| 5 | Provide desktop GUI | PyQt6 app with dark theme, live charts |
| 6 | Support parallel execution | 4+ concurrent tests |
| 7 | Achieve Grade B (70+) on sample firmware | Demonstrate value end-to-end |

---

## 4. System Architecture

### 4.1 High-Level Architecture

```
User -> GUI (PyQt6) -> Core Engine -> Renode Bridge -> Renode Process -> Firmware
                |         |              |
           Campaign   Fault YAML    Monitor Port (1234)
           Config     Taxonomy      Python API / REPL
                |         |              |
           Scheduler  Injector     Peripheral Hooks
                |         |              |
           Results <- Aggregator <- Sensor/Timer/Comm Values
                |
           RI Calculator -> Diagnosis -> Report Generator -> HTML/PDF/JSON
```

---

## 5. Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **GUI Framework** | PyQt6 | 6.6+ | Native desktop widgets, cross-platform |
| **Styling** | QSS (Qt StyleSheets) | — | Dark theme, custom appearance |
| **Real-Time Charts** | PyQtGraph | 0.13+ | 60fps live plots, gauges, heatmaps |
| **Core Language** | Python | 3.11+ | Business logic, framework |
| **Renode Bridge** | pyrenode3 / QProcess | 1.15+ | Renode integration |
| **Data Processing** | Pandas + NumPy | 2.0+ | Result aggregation, statistics |
| **Config Validation** | Pydantic + YAML | 2.0+ | Schema validation, campaign configs |
| **Reports** | Jinja2 + WeasyPrint | — | HTML/PDF generation |
| **ML Diagnosis** | scikit-learn | 1.3+ | Failure classification |
| **REST API** | FastAPI | 0.100+ | Headless API access |
| **WebSocket** | FastAPI WebSocket | — | Live test progress streaming |
| **CLI** | Typer | 0.9+ | Command-line interface |
| **Packaging** | PyInstaller | 6.0+ | .exe / .dmg / .AppImage |
| **CI/CD** | GitHub Actions | — | Automated testing, releases |

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
| **Resilience Index** | `src/core/resilience_index.py` | Compute RI = (D*0.4) + (Rec*0.3) + (S*0.3), assign Grade A-F |
| **Diagnosis Engine** | `src/core/diagnosis_engine.py` | Rule-based failure classification + fix recommendations |
| **Report Generator** | `src/core/report_generator.py` | Export HTML (interactive), PDF (audit), JSON (CI/CD), JUnit XML |

### 6.2 Fault Injection Taxonomy (27 Types)

| Category | Count | Types |
|---|---|---|
| **Sensor Faults** | 7 | Stuck-at, Gaussian Noise, Impulse Noise, Drift, Bias, Missing Samples, Outliers |
| **Timing Faults** | 5 | Deadline Miss, Clock Skew, Interrupt Storm, Watchdog Timeout, Race Condition |
| **Communication Faults** | 6 | Packet Loss, Latency Spike, Bus Flooding, Frame Corruption, Bus-Off State, Arbitration Loss |
| **Memory Faults** | 4 | Stack Overflow, Heap Corruption, Flash Bit-Flip, ECC Error |
| **Power Faults** | 3 | Brownout, Power Glitch, Sleep Failure |
| **GPIO/Peripheral Faults** | 2 | Pin Float, ADC Saturation |

---

## 7. API Design

### 7.1 REST Endpoints (FastAPI)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/run` | Run single fault test |
| `POST` | `/api/v1/campaign` | Run full campaign |
| `GET` | `/api/v1/status/{run_id}` | Check test status |
| `GET` | `/api/v1/result/{run_id}` | Get test results |
| `GET` | `/api/v1/report/{run_id}` | Generate report (html/pdf/json) |
| `POST` | `/api/v1/compare` | Compare two runs |
| `GET` | `/api/v1/faults` | List all 27 fault types |
| `GET` | `/api/v1/platforms` | List supported platforms |
| `WS` | `/api/v1/live/{run_id}` | WebSocket live progress |
| `POST` | `/api/v1/upload/firmware` | Upload and validate ELF |

---

## 8. UI/UX Design

### 8.1 Design Philosophy
- Dark theme first — reduces eye strain during long test campaigns
- Embedded engineer-native — sidebar navigation, dockable panels, monospace console
- Real-time feedback — live charts, progress bars, color-coded logs
- Information density — show everything important without clutter

### 8.2 Screen Inventory

| Screen | Widget | Key Elements |
|---|---|---|
| **Welcome** | `WelcomeScreen` | Hero, 4 quick-action cards, recent campaigns |
| **Campaign Designer** | `CampaignEditor` | Name, firmware upload, platform, 27-fault checkboxes, severity table |
| **Live Test Runner** | `TestRunnerView` | Summary cards, progress bar, 8-col results table, charts |
| **Report Viewer** | `ReportViewer` | Summary banner, HTML report, critical findings |
| **Comparison View** | `ComparisonView` | Delta cards, 5-col table, improvement/regression colors |

---

## 9. Security

### 9.1 Threat Model & Mitigations

| Threat | Risk | Mitigation |
|---|---|---|
| Firmware IP Theft | High | All execution is local; no cloud upload ever |
| Malicious Firmware | Medium | Sandboxed Renode process; resource limits; timeout guards |
| Path Traversal | High | `_sanitize_path()` validates no `..` in file paths |
| Report Sensitivity | Low | Optional AES-256 encryption for report files |

---

## 10. Performance

| Metric | Target | Strategy |
|---|---|---|
| Test Throughput | 100 fault injections/hour | Parallel execution (4+ workers) |
| Report Generation | <5 seconds | Jinja2 template caching |
| Dashboard Load | <2 seconds | Lazy loading, result pagination |
| Memory Footprint | <2GB RAM | Streaming logs, chunked Pandas |
| Startup Time | <10 seconds | Pre-compiled Renode, cached configs |

---

## 11. Workflow

```
START -> 1. Create Project -> 2. Configure Platform -> 3. Design Campaign
                                                            |
DONE <- 6. Report & Export <- 5. Analyze Results <- 4. Run Tests (Live)
     ^
     |    7. Compare Runs <- 8. Iterate & Fix
```

---

## 12. Deliverables Checklist

| # | Deliverable | Status |
|---|---|---|
| 1 | GitHub Repository | Done |
| 2 | Desktop Application (PyQt6) | Done |
| 3 | CLI (Typer) | Done |
| 4 | REST API (FastAPI) | Done |
| 5 | 27 Fault Types | Done |
| 6 | RI Calculator (0-100) | Done |
| 7 | Diagnosis Engine | Done |
| 8 | HTML/PDF/JSON Reports | Done |
| 9 | 3 Platform Definitions | Done |
| 10 | 27 Unit Tests | Done |
| 11 | CI/CD Pipeline | Done |
| 12 | Docker Image | Done |
| 13 | Documentation (22 docs) | Done |
| 14 | Demo Video | Guide ready |

---

## 13. Future Scope

### v1.1 (Near-term)
- Additional platforms: ESP32, RP2040, SAMD21
- ML-based diagnosis classifier
- Plugin system for third-party fault injectors

### v2.0 (Mid-term)
- Distributed testing across multiple machines
- Cloud dashboard (optional)
- RTOS-aware faults (FreeRTOS/Zephyr)

### v3.0 (Long-term)
- AI-generated fixes via LLM
- Formal verification bridge (SPIN/UPPAAL)
- TUV approval for ISO 26262 tool qualification

---

**Document Version:** 1.0.0
**Last Updated:** 2026-08-26
**Author:** RenodeResilience Team
