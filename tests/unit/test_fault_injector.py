from src.core.fault_injector import build_fault_command, FAULT_CATALOG

def test_catalog_size():
    assert len(FAULT_CATALOG)==27

def test_build_commands():
    assert "sysbus" in build_fault_command("SF-01", {"value":25,"target":"sysbus.i2c0.sensor0"})
    assert "sensor" in build_fault_command("SF-02", {"std_dev":2.5})
