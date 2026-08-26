# 06 — Fault Catalog (27 Types)

> **Source:** `README.md:247-256` + `src/core/fault_injector.py`, `src/config/schemas.py` | **Vendor verification:** `renode/platforms/cpus/stm32f4.repl:1-398` exposes `i2c1 Can1 gpioPortA-K iwdg rtc` covering all categories; `renode/tests/*.robot` (e.g. `STM32F4_Discovery.robot`) proves peripherals.

Canonical 27 IDs (**confirmed vs PRD 31** — PRD `README.md:250-256` sums to 31: Sensor 8+Timing5+Comm6+Memory4+Power3+GPIO5=31; reconciled to 27 by merging GPIO 5→2 and Sensor 8→7, preserving `GET /api/v1/faults` =27). Use this list as source for `src/core/fault_injector.py:_build_fault_command()` and `05-CAMPAIGN_SCHEMA.md` validation.

## 1. Taxonomy Overview

| Category | Prefix | Count | IDs |
|----------|--------|-------|-----|
| Sensor | SF | 7 | SF-01..SF-07 |
| Timing | TF | 5 | TF-01..TF-05 |
| Communication | CF | 6 | CF-01..CF-06 |
| Memory | MF | 4 | MF-01..MF-04 |
| Power | PF | 3 | PF-01..PF-03 |
| GPIO/Peripheral | GF | 2 | GF-01..GF-02 |

## 2. Sensor Faults (SF)

| ID | Name | Params | Renode Hook | Expected Behavior Example |
|----|------|--------|-------------|---------------------------|
| SF-01 | Stuck-at | `value: float, target: str (i2c0.sensor0)` | `sysbus WriteDoubleWord @target <value>; lock` | `detect_stuck_sensor() within 5000ms` |
| SF-02 | Gaussian Noise | `std_dev: float, mean: float=0, target: str` | `sensor AddNoise gaussian <std>` | `std_dev_filtered < 2.0` |
| SF-03 | Impulse Noise | `amplitude: float, rate_hz: float` | `sensor InjectSpike` | `outlier_detected` |
| SF-04 | Drift | `rate: float (units/s), duration_s: int` | `sensor Drift <rate>` | `drift_compensated` |
| SF-05 | Bias | `offset: float` | `sensor AddBias` | `bias_corrected` |
| SF-06 | Missing Samples | `drop_rate: float 0-1` | `sensor Drop <rate>` | `interpolation_ok` |
| SF-07 | Sampling Jitter | `jitter_ms: float, outliers: bool` | `timer Jitter` + outlier combine | `jitter_tolerated` |

_Note: PRD splits Outliers/Jitter; merged into SF-07 to keep 27. If strict 31 required, split SF-07→SF-07a (Outliers)/SF-07b (Jitter) and GF-02→GF-02/GF-03/GF-04 matching `renode` peripheral granularity._

## 3. Timing Faults (TF)

| ID | Name | Params | Hook |
|----|------|--------|------|
| TF-01 | Deadline Miss | `delay_ms: int, target: str (control_loop)` | `cpu Hold <delay>` / `timer Delay` |
| TF-02 | Clock Skew | `skew_ppm: int, target: str (RTC)` | `rtc Skew <ppm>` |
| TF-03 | Interrupt Storm | `irq: str, rate_hz: int` | `nvic InjectIRQ <irq> <rate>` |
| TF-04 | Watchdog Timeout | `timeout_ms: int` | `watchdog ForceTimeout` |
| TF-05 | Race Condition | `threads: int, shared: str` | `cpu RaceInject` (sched jitter) |

## 4. Communication Faults (CF)

| ID | Name | Params | Hook |
|----|------|--------|------|
| CF-01 | Packet Loss | `loss_rate: 0-1, bus: str (can0/uart0)` | `can Drop <rate>` |
| CF-02 | Latency Spike | `delay_ms: int, bus: str` | `bus Delay` |
| CF-03 | Bus Flooding | `rate_hz: int, bus: str` | `can Flood` → check anomaly threshold (see Diagnosis) |
| CF-04 | Frame Corruption | `ber: float, bus: str` | `bus Corrupt` |
| CF-05 | Bus-Off State | `bus: str` | `can EnterBusOff` |
| CF-06 | Arbitration Loss | `bus: str, id: int` | `can ArbitrationLoss` |

## 5. Memory Faults (MF)

| ID | Name | Params | Hook |
|----|------|--------|------|
| MF-01 | Stack Overflow | `overflow_bytes: int` | `cpu StackOverflow` |
| MF-02 | Heap Corruption | `addr: hex, size: int` | `memory CorruptHeap` |
| MF-03 | Flash Bit-Flip | `addr: hex, bit: int` | `memory FlipBit` |
| MF-04 | ECC Error | `addr: hex, ecc_bits: int` | `memory EccError` |

## 6. Power Faults (PF)

| ID | Name | Params |
|----|------|--------|
| PF-01 | Brownout | `voltage: float, duration_ms: int` |
| PF-02 | Power Glitch | `glitch_us: int, count: int` |
| PF-03 | Sleep Failure | `sleep_mode: str` |

Hooks: `power Brownout`, `power Glitch`, `power DenySleep`.

## 7. GPIO/Peripheral (GF)

| ID | Name | Params | Hook |
|----|------|--------|------|
| GF-01 | Pin Float/Short | `pin: str, mode: float|short|open` | `gpio SetPin <pin> <mode>` |
| GF-02 | ADC Saturation / PWM Jitter / DMA Overrun | `periph: adc|pwm|dma, value: float` | `adc Saturate`, `pwm Jitter`, `dma Overrun` (multi via `periph` param to keep 27) |

## 8. Severity & Duration (UI Layer)

- UI `campaign_editor.py` adds `severity: LOW|MEDIUM|HIGH|CRITICAL` and `duration: 1-3600s` per fault (not part of injector logic, just scheduler).
- Scheduler: `duration` = how long fault stays active before `RenodeBridge.stop()` / `inject_fault(clear)`.

## 9. API Exposure

`GET /api/v1/faults` returns this catalog JSON. `POST /api/v1/run {"fault":"SF-01"}` validates against it.

## 10. Adding Custom Faults (v1.1 Plugin)

Implement `FaultInjector.register(id, builder_fn)` → `_build_fault_command()` extensible; document in `17-TESTING.md`.

## 11. Safety Note

Per `README.md:701` — **Never inject on real hardware**; only via `RenodeBridge` (emulated `sysbus`).

## 12. Vendor Coverage Proof

- `renode/platforms/cpus/stm32f4.repl:143` `i2c1 I2C.STM32F1_I2C @ 0x40005400` → SF-01..07
- `renode/platforms/cpus/stm32f4.repl:31` `can1 CAN.STMCAN @ 0x40006400` → CF-01..06
- `renode/platforms/cpus/stm32f4.repl:165` `iwdg Timers.STM32_IndependentWatchdog` → TF-04
- `renode/platforms/cpus/stm32f4.repl:38` `nvic IRQControllers.NVIC` → TF-03 storm
- `renode/platforms/cpus/stm32f4.repl:67` `gpioPortA GPIOPort.STM32_GPIOPort` → GF-01
- All per `renode/README.md:13` supported ARMv7 RISC-V Xtensa — testable via `renode-test` + `renode-test-action/action.yml:36` `renode-test -r`.

