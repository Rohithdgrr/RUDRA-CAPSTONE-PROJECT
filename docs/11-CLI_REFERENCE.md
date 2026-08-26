# 11 — CLI Reference (Typer)

> **Binary:** `renode-resilience` | `scripts/build.py` | Source `README.md:603-631`

## Install

After `02-INSTALL.md`: `renode-resilience --help` should show commands. If not: `pip install -e .` or `python -m src.main --help`.

## Commands

### `renode-resilience run` — Single Fault

```bash
renode-resilience run \
  --firmware examples/sensor-firmware/build/sensor.elf \
  --platform resources/platforms/stm32f4_discovery.repl \
  --fault SF-01 \
  --duration 60 \
  --target i2c0.sensor0 \
  --output results/single.json
```
| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--firmware` | yes | — | ELF path |
| `--platform` | yes | — | REPL path or id `stm32f4` |
| `--fault` | yes | — | Fault ID from `06-FAULT_CATALOG.md` |
| `--duration` | no | 60 | Seconds |
| `--target` | per-fault | — | Peripheral path |
| `--output` | no | stdout | Result JSON path |

Exit code 0 PASS, 1 FAIL, 2 ERROR (timeout).

### `renode-resilience campaign` — Full Campaign

```bash
renode-resilience campaign \
  --config campaigns/sensor_suite.yaml \
  --parallel 4 \
  --output results/
```
| Flag | Default | Description |
|------|---------|-------------|
| `--config` | required | Campaign YAML (`05-CAMPAIGN_SCHEMA.md`) |
| `--parallel` | 1 | Workers 1-8 (`src/core/test_runner.py` QThreadPool) |
| `--output` | `results/` | Dir for `campaign_<date>.json` + logs |

Streams progress to stderr; WebSocket mirroring if API running.

### `renode-resilience report`

```bash
renode-resilience report \
  --results results/campaign_2026-08-26.json \
  --format pdf \
  --output report.pdf
# formats: html|pdf|json|junit
```

### `renode-resilience compare`

```bash
renode-resilience compare \
  --baseline results/baseline.json \
  --optimized results/optimized.json \
  --output comparison.html
```

Outputs delta table `Fault | Baseline | Optimized | Delta` + improvement %.

### `renode-resilience list`

```bash
renode-resilience faults      # lists 27 IDs
renode-resilience platforms   # stm32f4, nrf52840, riscv_hifive1
```

## Global Flags

`--help`, `--version`, `--verbose` (-v), `--quiet`.

## Exit Codes

`0` success, `1` test failure (RI<F threshold), `2` validation error, `3` Renode not found.

## Examples

```bash
# Sensor suite 27 faults parallel
renode-resilience campaign --config campaigns/sensor_suite.yaml --parallel 4 --output results/

# Then HTML
renode-resilience report --results results/sensor_suite.json --format html --output docs/report.html

# CI: fail if Grade <B
renode-resilience campaign --config campaigns/sensor_suite.yaml --output results/ && \
  python -c "import json; assert json.load(open('results/latest.json'))['resilience_index']>=70"
```

## Config

Reads `src/config/defaults.py` and `~/.config/renode-resilience/config.yaml` (Renode path, theme).

## Troubleshooting

- `command not found` → venv activate, reinstall `pip install -e .`.
- `Renode not found` → set `--renode-path` or Settings dialog.
- See `18-TROUBLESHOOTING.md`.
