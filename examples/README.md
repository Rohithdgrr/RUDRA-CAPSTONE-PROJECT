# Examples

Three sample firmwares with prebuilt ELF placeholders and C sources. Each has a matching `campaign.yaml`.

- `sensor-firmware/` — STM32F4, I2C temperature sensor, covers SF-01..07, fastest to test (30s).
- `motor-controller/` — Control loop + watchdog, covers TF-01, GF-01.
- `can-validator/` — CAN bus, covers CF-01, CF-03.

Build (requires `arm-none-eabi-gcc`):
```bash
cd examples/sensor-firmware && make
arm-none-eabi-readelf -h build/sensor.elf
```
Run via RenodeResilience:
```bash
renode-resilience campaign --config examples/sensor-firmware/campaign.yaml --parallel 2
```
Or GUI: Load ELF → Platform `STM32F4 Discovery` → Faults SF-01..07 → Run.

Placeholders `build/*.elf` are checked in (text stub) for CI without toolchain.
