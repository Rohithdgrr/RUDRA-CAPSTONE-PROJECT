from src.core.fault_injector import build_fault_command, FAULT_CATALOG, FaultInjector
from unittest.mock import MagicMock

def test_catalog_size():
    assert len(FAULT_CATALOG)==27

def test_build_commands_all():
    assert "sysbus" in build_fault_command("SF-01", {"value":25,"target":"sysbus.i2c0.sensor0"})
    assert "sensor" in build_fault_command("SF-02", {"std_dev":2.5})
    assert "InjectSpike" in build_fault_command("SF-03", {"amplitude":999})
    assert "Drift" in build_fault_command("SF-04", {"rate":0.1})
    assert "AddBias" in build_fault_command("SF-05", {"offset":1.0})
    assert "Drop" in build_fault_command("SF-06", {"drop_rate":0.2})
    assert "Jitter" in build_fault_command("SF-07", {"jitter_ms":5})
    assert "cpu Hold" in build_fault_command("TF-01", {"delay_ms":100})
    assert "rtc Skew" in build_fault_command("TF-02", {"skew_ppm":100})
    assert "InjectIRQ" in build_fault_command("TF-03", {"irq":"38"})
    assert "watchdog" in build_fault_command("TF-04", {"timeout_ms":50}).lower()
    assert "RaceInject" in build_fault_command("TF-05", {"threads":2})
    assert "can Inject CF-01" in build_fault_command("CF-01", {"loss_rate":0.3})
    assert "CF-03" in build_fault_command("CF-03", {"rate_hz":5000})
    assert "memory Inject MF-01" in build_fault_command("MF-01", {"overflow_bytes":512})
    assert "memory Inject MF-03" in build_fault_command("MF-03", {"addr":"0x0800"})
    assert "power Inject PF-01" in build_fault_command("PF-01", {"voltage":2.0})
    assert "power Inject PF-02" in build_fault_command("PF-02", {"glitch_us":10})
    assert "gpio SetPin" in build_fault_command("GF-01", {"pin":"PA5"})
    assert "adc Inject" in build_fault_command("GF-02", {"periph":"adc","value":4095})
    assert "Unknown" in build_fault_command("XX-99", {})

def test_injector_custom():
    fi = FaultInjector()
    fi.register("SF-01", lambda p: f"CUSTOM {p}")
    assert fi.inject("SF-01", {"value":1}) is True
    assert fi.list_faults()[0]=="SF-01"

def test_injector_bridge():
    mock = MagicMock()
    mock.send_command.return_value = True
    fi = FaultInjector(bridge=mock)
    fi.inject("SF-02", {"std_dev":1.0})
    assert mock.send_command.called
