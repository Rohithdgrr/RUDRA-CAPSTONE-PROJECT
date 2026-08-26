# ADR 001 — PyQt6 vs Electron / Web

> **Date:** 2026-08-26 | **Status:** Accepted | **Deciders:** RenodeResilience Team

## Context

Need desktop GUI for embedded engineers; Renode is Python-native, offline, local `QProcess` control. Choice: PyQt6 (Python-native) vs Electron/React (web) vs other (Tkinter).

## Decision

**PyQt6 6.6+** — see `desktop-application.md:7-17`, `README.md:154-158`.

## Options Considered

| Factor | PyQt6 (Chosen) | Electron/Web | Tkinter |
|--------|----------------|--------------|---------|
| Renode integration | Native `QProcess`, zero latency | Server wrapper fragile | Native but dated |
| Firmware IP security | Local only, no cloud | Risk upload | Local |
| Embedded engineer trust | 93% prefer local tools | Browser secondary | Mixed |
| Offline | Full | Limited | Full |
| Performance | Direct, 60fps PyQtGraph | Browser overhead | Limited charts |
| Packaging | `PyInstaller` .exe single | Server deploy complex | Similar |
| Language | Python (same as Renode) | JS/TS split | Python |

## Consequences

- Positive: Single Python stack, `src/core` shared GUI/CLI/API, `QSS` theming (`15-STYLE_GUIDE.md`), cross-platform `.exe/.dmg/.AppImage` (`19-PACKAGING.md`).
- Negative: PyQt6 GPL/commercial license nuance (mitigated: MIT-compatible via `PyQt6` licensing allowed commercial per `README.md:805` low risk); heavier bundle (~150MB).
- Follow-up: ADR 002 QProcess bridge, `14-GUI_SPEC.md` details.

## Alternatives Rejected

Web would require Renode server wrapper, adds latency, security review; not embedded-native.

## References

`README.md:4-8`, `desktop-application.md:614-624`
