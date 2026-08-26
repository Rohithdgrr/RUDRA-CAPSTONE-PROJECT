# ADR 002 — Renode Bridge via QProcess (subprocess.Popen)

> **Date:** 2026-08-26 | **Status:** Accepted

## Context

Renode exposes monitor via `--port 1234` and optional `pyrenode3` Python API `1.15+` (`README.md:165`). Need `src/core/renode_bridge.py` to start/stop, inject faults, read peripherals.

Options: `pyrenode3` bindings vs `QProcess`/`subprocess.Popen` with stdin monitor commands.

## Decision

**`subprocess.Popen` + `QProcess` wrapper** (hybrid). Primary path `Popen(['renode','--disable-xwt','--port','1234'], stdin=PIPE, stdout=log_file)` and `stdin.write(command+"\n")` per `README.md:198-245`. Provide `pyrenode3` as optional fallback for `read_peripheral()` structured reads.

## Rationale

- `pyrenode3` not always installed on user Renode; monitor port universal.
- `QProcess` integrates with Qt event loop for GUI live signals; `Popen` works headless.
- Explicit monitor commands `include @platform`, `sysbus LoadELF @fw`, `sysbus ReadDoubleWord`, `sysbus WriteDoubleWord` map cleanly to `06-FAULT_CATALOG.md` fault builders.
- Simpler `_wait_for_monitor(15s)` polling; `quit` + `wait(10)` + `kill` shutdown deterministic (`01-ARCHITECTURE.md`).

## Consequences

- Must build `_build_fault_command(fault_id, params)` per 27 faults.
- Log to `tempfile.NamedTemporaryFile` for audit; stream to GUI console.
- Fallback `pyrenode3` can be added later without API break (`RenodeBridge.read_peripheral` abstract).

## Alternatives

Pure `pyrenode3` rejected: version pin fragile, not available in portable Renode zip.

## Vendor Proof

- Monitor flags: `renode/README.md:161` `-P INT32 --disable-gui` + `Dockerfile` already uses `1.16.1`.
- `pyrenode3` proof: `pyrenode3/src/pyrenode3/__init__.py:34` `RenodeLoader.from_path/from_installed()` with `PYRENODE_PATH`, `pyrenode3/pyproject.toml:28` `pythonnet>=3.0.1`, tested via `examples/unleashed-fomu.py:1753`.

## References

`src/core/renode_bridge.py`, `desktop-application.md:446-492`, `07-PLATFORM_GUIDE.md`, `renode/platforms/cpus/stm32f4.repl:1-398`, `pyrenode3/README.md:11`
