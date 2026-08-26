# Methodology Paper Outline — IEEE 8-10 Pages

> **Title:** RenodeResilience: A Quantitative Fault-Injection Framework for Embedded Firmware on Renode
> **Authors:** RenodeResilience Team — 2026-08-26

## Abstract (200 words)
Automated fault-injection + 0-100 Resilience Index RI=(D×0.4)+(Rec×0.3)+(S×0.3) + rule-based diagnosis + PyQt6 GUI vs HIL $50K.

## 1. Introduction
- $500M recall problem (`README.md:22`), gap: no structured testing layer on Renode.

## 2. Related Work
- QEMU vs Vector vs Renode, Table `README.md:745`.

## 3. Fault Taxonomy
- 27 types 6 categories `docs/06-FAULT_CATALOG.md:9`, Renode hooks `sysbus WriteDoubleWord`, `renode/platforms/cpus/stm32f4.repl:31` proof.

## 4. Architecture
- Figure `docs/01-ARCHITECTURE.md:7` — GUI/QProcess/renode_bridge/QThreadPool, `adr/002` hybrid.

## 5. Resilience Index
- Formula `docs/08-RESILIENCE_INDEX.md:3`, weights `adr/003` 40/30/30, grades A-F, example SF-01 100 vs TF-01 0.

## 6. Diagnosis Engine
- Rules `docs/09-DIAGNOSIS_ENGINE.md:18` SF-03→median filter, ISO26262 mapping.

## 7. Implementation
- PyQt6 6.6, FastAPI, Typer, PyInstaller — `src/core/{renode_bridge,fault_injector,campaign}.py`, `src/gui/*`.

## 8. Evaluation
- 3 firmwares `examples/*/src/main.c`, campaigns `campaigns/sensor_suite.yaml`, RI 43→73 after fix (+70%), throughput 100/hr parallel 4, report <2s.

## 9. Future
- v1.1 ML scikit-learn, ESP32, plugin system (`CHANGELOG.md:21`).

## 10. Conclusion

## References
- Renode https://renode.io, pyrenode3, Antmicro, ISO 26262, DO-178C.

## Appendix
- REPL excerpts `renode/platforms/cpus/stm32f4.repl:43`, API Swagger `GET /api/v1/faults`.

> Generate PDF: `pandoc docs/METHODOLOGY_PAPER.md -o docs/methodology.pdf --template=ieee` or WeasyPrint.
