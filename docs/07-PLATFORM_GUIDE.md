# 07 — Platform Guide

> **Resources:** `resources/platforms/*.repl` (copies from `renode/platforms/boards/` + `renode/platforms/cpus/`) | Renode 1.15+ (tested 1.16.1, `renode/README.md:36`), `renode-docker/Dockerfile:8`

## 1. Supported Platforms (v1.0)

| ID | Board | MCU | Arch | REPL File | Status |
|----|-------|-----|------|-----------|--------|
| `stm32f4` | STM32F4 Discovery | STM32F407VG | ARM Cortex-M4 | `stm32f4_discovery.repl` (`renode/platforms/boards/stm32f4_discovery.repl:1` + `renode/platforms/cpus/stm32f4.repl:1`) | ✅ Prebuilt, `renode/tests/peripherals/STM32F4_Discovery.robot` |
| `nrf52840` | nRF52840 DK | nRF52840 | ARM Cortex-M4 + BT | `nrf52840dk_nrf52840.repl` (`renode/platforms/boards/nrf52840dk_nrf52840.repl`) | ✅ Prebuilt, `tests/peripherals/NRF52840.robot` |
| `riscv_hifive1` | HiFive1 Rev B | FE310 | RISC-V RV32IMAC | `sifive-fe310.repl` (`renode/platforms/cpus/sifive-fe310.repl`) | ✅ Prebuilt, `tests/platforms/SiFive-FE310.robot` |
| `esp32` | ESP32 DevKit | Xtensa LX6 | — | — | ⏳ v1.1 |
| `rp2040` | Raspberry Pi Pico | RP2040 | ARM Cortex-M0+ | — | ⏳ v1.1 |

Query via `GET /api/v1/platforms` or sidebar `Platforms` tree.

## 2. REPL File Basics

Renode platform description (`.repl`):
```
using sysbus
mach create "stm32f4"
machine LoadPlatformDescription @platforms/cpus/stm32f4.repl
sysbus LoadELF @firmware
connector Connect sysbus.uart1 uart1
```

Stored in `resources/platforms/` (copied from `renode/platforms/boards/` + `cpus/` + `platforms/cpus/*.repl`); editable for custom boards. See `desktop-application.md:340-344`. Original SVD `https://dl.antmicro.com/projects/renode/svd/STM32F40x.svd.gz` via `renode/platforms/cpus/stm32f4.repl:394`.

## 3. Per-Platform Details

### STM32F4 Discovery
- Peripherals testable: I2C sensors, SPI flash, UART, CAN, GPIO, ADC, PWM, DMA, RTC, WDT, NVIC (`README.md:828-852`).
- Fault hooks: all 27; most mature.
- Firmware arch check: `arm-none-eabi-readelf -h sensor.elf | grep Machine → ARM`.

### nRF52840 DK
- Adds BLE radio placeholder (not fault-injected in v1.0; treat as UART).
- Power faults PF-01..03 relevant (sleep controller).
- I2C `i2c0.sensor0` maps to temp sensor mock.

### HiFive1 RISC-V
- PLIC instead of NVIC for `TF-03 Interrupt Storm`.
- Flash `MF-03 Bit-Flip` uses `memory FlipBit` on `sysbus.flash`.

## 4. Adding Custom Platform

1. Copy `resources/platforms/stm32f4_discovery.repl` → `myboard.repl`.
2. Edit CPU/peripheral lines per Renode docs.
3. Add to `src/config/defaults.py` platforms list.
4. Test: `renode --disable-xwt` then `include @myboard.repl` → `sysbus LoadELF @fw` → `start` → `sysbus ReadDoubleWord 0x08000000`.
5. Document fault coverage gaps (e.g., custom ADC path `sysbus.adc0`).

## 5. Renode Bridge Integration

`src/core/renode_bridge.py:RenodeBridge.start(platform_file, firmware_file)` builds script:
```
include @<platform_file>
sysbus LoadELF @<firmware_file>
start
```
Spawns `subprocess.Popen(['renode','--disable-xwt','--port','1234'])`, waits `_wait_for_monitor(15s)`.

## 6. Peripheral Paths Reference

| Bus | Read Example | Faults |
|-----|--------------|--------|
| I2C sensor | `sysbus.i2c0.sensor0 Value` | SF-01..07 |
| UART | `sysbus.uart0 Status` | CF-01..06 |
| CAN | `sysbus.can0 BusState` | CF-01..06 |
| GPIO | `sysbus.gpioa Pin7` | GF-01 |
| ADC | `sysbus.adc0 Channel3` | GF-02 |
| Watchdog | `sysbus.wdog Enabled` | TF-04 |

Full list per board in each `.repl` comments.

## 7. Firmware Requirements

- ELF or BIN compiled for correct arch; entry point present.
- Symbols optional but help `diagnosis_engine` map `fault → code path`.
- Resource limits: emulator 10-100x slower; keep firmware <512KB for throughput target 100/hr (`README.md:718`).

## 8. Troubleshooting

- `Unknown platform` → check `schemas.py` enum vs `renode/platforms/boards/*.repl` list (142 boards).
- `LoadELF failed: wrong architecture` → rebuild for correct MCU (`arm-none-eabi-readelf -h` Machine `ARM` vs `RISC-V`).
- Port 1234 busy → see `18-TROUBLESHOOTING.md`.
- `renode --version` mismatch: prefer portable `1.16.1` (`renode-docker/Dockerfile:8`) or `renode/README.md:36` nightly; install via `brew install renode/tap/renode` (macOS) or `renode-latest.linux-portable.tar.gz` (Linux).
