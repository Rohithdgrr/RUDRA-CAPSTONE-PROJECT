# 18 — Troubleshooting

> **Logs:** `RenodeBridge.log_file` temp `.log`, console 10k lines archived, `results/*.log`

## 1. Renode Startup

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Renode not found` | Not on PATH | Set in GUI Settings → Renode Path or `export PATH=$PATH:/opt/renode` |
| `Timeout waiting for monitor 15s` (`renode_bridge.py:_wait_for_monitor`) | Port 1234 busy, Renode crash | `netstat -ano | findstr 1234` (Win) / `lsof -i:1234` → kill PID; `renode --disable-xwt --port 1234` manual |
| `LoadELF failed: wrong architecture` | ELF for wrong MCU | Rebuild: `arm-none-eabi-gcc -mcpu=cortex-m4` for STM32F4 |
| Zombie Renode after force-kill | No graceful `quit` | `taskkill /F /IM renode.exe` (Win) / `pkill -9 renode`; then `RenodeBridge.stop(graceful=False)` auto-kill |

## 2. Campaign / YAML

| Error | Cause | Fix |
|-------|-------|-----|
| `ValidationError: firmware not found` | Relative path | Use repo-relative `examples/.../sensor.elf` or absolute |
| `weights sum !=1.0` | Bad `scoring` | `0.4+0.3+0.3=1.0` per `05-CAMPAIGN_SCHEMA.md` |
| `Unknown fault ID` | Typo `SF-99` | Check `06-FAULT_CATALOG.md` 27 IDs |
| `timeout_ms out of range` | 5ms | Must 100-60000 |
| `duplicate fault id` | SF-01 twice | Unique per campaign |

Validate offline: `python -m src.config.validator campaign.yaml`.

## 3. Test Runner

- **Hang infinite loop:** Set `duration` reasonable (60s), watchdog `TF-04`; runner auto-kill `duration*1.5`.
- **Disk 100MB logs:** Rotate `logs/`; console caps 10k lines (`README.md:404`).
- **Parallel 4 slow:** Renode 10-100x slower (`README.md:718`); reduce parallel or use lightweight ELF.
- **Progress stuck 0/27:** Check `renode_bridge.py` stdin flush; see `RenodeBridge.log_file`.

## 4. GUI

- **Blank window:** See `02-INSTALL.md` verify PyQt6 6.6+; `python -m src.main --verbose`.
- **QSS not applied:** Path `src/gui/styles/dark_theme.qss` must exist; fallback light theme.
- **Charts 0 fps:** PyQtGraph needs OpenGL; update GPU drivers.

## 5. Reports

- **WeasyPrint missing:** `pip install WeasyPrint` + pango/cairo (Linux `apt install libcairo2`).
- **PDF empty:** Jinja2 template error; check `resources/templates/report_base.html` bytecode cache.
- **JUnit not recognized by Jenkins:** Use `results.to_junit()` strict schema `10-REPORT_SPEC.md`.

## 6. CLI/API

- `renode-resilience: command not found` → `pip install -e .` or `venv` activate.
- API `503 Renode not running` → start Renode or run via GUI which auto-starts.
- WS disconnect → `run_id` expired (results TTL 7 days in `src/config/defaults.py`).

## 7. Diagnostics

```bash
# Renode manual test
renode --disable-xwt --port 1234
(monitor) include @resources/platforms/stm32f4_discovery.repl
(monitor) sysbus LoadELF @examples/sensor-firmware/build/sensor.elf
(monitor) start
(monitor) sysbus ReadDoubleWord 0x08000000

# Python harness
python -c "from src.core.renode_bridge import RenodeBridge; from pathlib import Path; b=RenodeBridge(); print(b.start(Path('resources/platforms/stm32f4_discovery.repl'), Path('examples/sensor-firmware/build/sensor.elf')))"
```

## 8. Getting Help

- Check `logs/audit.log` + `RenodeBridge.log_file` (temp path printed on start).
- For Robot logs: `$ARTIFACTS_PATH/robot_output.xml` + `src/results.py` markdown via `renode-test-action/src/run_renode_test.sh:40` → `$GITHUB_STEP_SUMMARY`.
- Open issue with `campaign.yaml`, `results/*.json` snippet, `renode --version` (or `renode --version` from `renode-docker/Dockerfile:8` `1.16.1`), `PYRENODE_PATH` if using `pyrenode3`.
- Upstream Renode help: `renode/README.md:227` https://renode.readthedocs.io, issues `github.com/renode/renode`.
