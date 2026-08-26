"""FaultInjector — maps fault IDs to Renode monitor commands."""

FAULT_CATALOG = {
    "SF-01": {"name": "Stuck-at", "category": "Sensor"},
    "SF-02": {"name": "Gaussian Noise", "category": "Sensor"},
    "SF-03": {"name": "Impulse Noise", "category": "Sensor"},
    "SF-04": {"name": "Drift", "category": "Sensor"},
    "SF-05": {"name": "Bias", "category": "Sensor"},
    "SF-06": {"name": "Missing Samples", "category": "Sensor"},
    "SF-07": {"name": "Sampling Jitter", "category": "Sensor"},
    "TF-01": {"name": "Deadline Miss", "category": "Timing"},
    "TF-02": {"name": "Clock Skew", "category": "Timing"},
    "TF-03": {"name": "Interrupt Storm", "category": "Timing"},
    "TF-04": {"name": "Watchdog Timeout", "category": "Timing"},
    "TF-05": {"name": "Race Condition", "category": "Timing"},
    "CF-01": {"name": "Packet Loss", "category": "Communication"},
    "CF-02": {"name": "Latency Spike", "category": "Communication"},
    "CF-03": {"name": "Bus Flooding", "category": "Communication"},
    "CF-04": {"name": "Frame Corruption", "category": "Communication"},
    "CF-05": {"name": "Bus-Off State", "category": "Communication"},
    "CF-06": {"name": "Arbitration Loss", "category": "Communication"},
    "MF-01": {"name": "Stack Overflow", "category": "Memory"},
    "MF-02": {"name": "Heap Corruption", "category": "Memory"},
    "MF-03": {"name": "Flash Bit-Flip", "category": "Memory"},
    "MF-04": {"name": "ECC Error", "category": "Memory"},
    "PF-01": {"name": "Brownout", "category": "Power"},
    "PF-02": {"name": "Power Glitch", "category": "Power"},
    "PF-03": {"name": "Sleep Failure", "category": "Power"},
    "GF-01": {"name": "Pin Float/Short", "category": "GPIO"},
    "GF-02": {"name": "ADC/PWM/DMA", "category": "GPIO"},
}


def build_fault_command(fault_id: str, params: dict) -> str:
    """Translate fault ID + params to Renode monitor command."""
    p = params or {}
    if fault_id == "SF-01":
        return f'sysbus WriteDoubleWord {p.get("target","sysbus.i2c0.sensor0")} {p.get("value",0)}'
    if fault_id == "SF-02":
        return f'sensor AddNoise gaussian {p.get("std_dev",1.0)}'
    if fault_id == "SF-03":
        return f'sensor InjectSpike {p.get("amplitude",999)} {p.get("rate_hz",10)}'
    if fault_id == "SF-04":
        return f'sensor Drift {p.get("rate",0.1)}'
    if fault_id == "SF-05":
        return f'sensor AddBias {p.get("offset",1.0)}'
    if fault_id == "SF-06":
        return f'sensor Drop {p.get("drop_rate",0.2)}'
    if fault_id == "SF-07":
        return f'timer Jitter {p.get("jitter_ms",5)}'
    if fault_id == "TF-01":
        return f'cpu Hold {p.get("delay_ms",100)}'
    if fault_id == "TF-02":
        return f'rtc Skew {p.get("skew_ppm",100)}'
    if fault_id == "TF-03":
        return f'nvic InjectIRQ {p.get("irq","0")} {p.get("rate_hz",1000)}'
    if fault_id == "TF-04":
        return f'watchdog ForceTimeout {p.get("timeout_ms",10)}'
    if fault_id == "TF-05":
        return f'cpu RaceInject {p.get("threads",2)}'
    if fault_id.startswith("CF-"):
        return f'can Inject {fault_id} {p}'
    if fault_id.startswith("MF-"):
        return f'memory Inject {fault_id} {p}'
    if fault_id.startswith("PF-"):
        return f'power Inject {fault_id} {p}'
    if fault_id == "GF-01":
        return f'gpio SetPin {p.get("pin","0")} {p.get("mode","float")}'
    if fault_id == "GF-02":
        return f'{p.get("periph","adc")} Inject {p.get("value",0)}'
    return f'# Unknown fault {fault_id} {p}'


class FaultInjector:
    def __init__(self, bridge=None):
        self.bridge = bridge
        self._custom = {}

    def register(self, fault_id: str, builder):
        self._custom[fault_id] = builder

    def inject(self, fault_id: str, params: dict) -> bool:
        if fault_id in self._custom:
            cmd = self._custom[fault_id](params)
        else:
            cmd = build_fault_command(fault_id, params)
        if self.bridge:
            return self.bridge.send_command(cmd)
        return True

    def list_faults(self):
        return list(FAULT_CATALOG.keys())
