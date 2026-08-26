from unittest.mock import MagicMock, patch
from pathlib import Path
from src.core.renode_bridge import RenodeBridge

@patch("subprocess.Popen")
@patch.object(RenodeBridge, "_wait_for_monitor", return_value=True)
def test_start_success(mock_wait, mock_popen):
    mock_proc = MagicMock()
    mock_proc.stdin = MagicMock()
    mock_popen.return_value = mock_proc
    b = RenodeBridge()
    ok = b.start(Path("resources/platforms/stm32f4_discovery.repl"), Path("examples/sensor-firmware/build/sensor.elf"))
    assert ok is True
    mock_popen.assert_called_once()
    assert mock_proc.stdin.write.called

@patch("subprocess.Popen", side_effect=FileNotFoundError)
def test_start_not_found(mock_popen):
    b = RenodeBridge(renode_bin="nonexistent_renode_xyz")
    ok = b.start(Path("a.repl"), Path("b.elf"))
    assert ok is False

def test_inject_without_bridge():
    from src.core.fault_injector import FaultInjector
    fi = FaultInjector(bridge=None)
    assert fi.inject("SF-01", {"value": 1}) is True
    assert len(fi.list_faults()) == 27
