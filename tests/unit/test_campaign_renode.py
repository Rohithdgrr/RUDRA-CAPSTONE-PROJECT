"""Unit tests for Campaign Renode wiring — mocked, no real Renode needed."""
from unittest.mock import MagicMock, patch, PropertyMock
from pathlib import Path
import pytest
from src.core.campaign import Campaign
from src.config.schemas import CampaignConfig


def _make_cfg(name="Test", faults=None):
    if faults is None:
        faults = [{"id": "SF-01", "params": {"target": "sysbus.test"}, "expected": "detect", "timeout_ms": 500}]
    return CampaignConfig.model_validate({
        "name": name,
        "firmware": "a.elf",
        "platform": "stm32f4",
        "duration": 60,
        "parallel": 1,
        "faults": faults,
    })


def test_run_fallback_when_renode_missing():
    """use_renode=True with nonexistent binary should fallback to sim and still pass."""
    cfg = _make_cfg(faults=[
        {"id": "SF-01", "params": {}, "expected": "", "timeout_ms": 500},
        {"id": "SF-02", "params": {}, "expected": "", "timeout_ms": 500},
    ])
    camp = Campaign(cfg)
    res = camp.run(use_renode=True, renode_bin="nonexistent_renode_xyz_123")
    assert res.total_count == 2
    assert 0 <= res.resilience_index <= 100


def test_run_parallel_fallback():
    cfg = _make_cfg(faults=[
        {"id": "SF-01", "params": {}, "expected": "", "timeout_ms": 500},
        {"id": "TF-01", "params": {}, "expected": "", "timeout_ms": 500},
    ])
    camp = Campaign(cfg)
    res = camp.run(parallel=2, use_renode=True, renode_bin="nonexistent_renode_xyz_123")
    assert res.total_count == 2


def test_run_with_mocked_shared_bridge():
    """Inject mocked bridge via `bridge=` param (caller-managed) — covers _run_single_renode."""
    cfg = _make_cfg()
    camp = Campaign(cfg)
    mock_bridge = MagicMock()
    mock_bridge.inject_fault.return_value = True
    mock_bridge.read_peripheral.return_value = "0x1234"  # non-zero => detected
    mock_bridge.send_command.return_value = True
    mock_bridge.log_path = None
    # Use caller-supplied bridge path (sharing one bridge sequentially)
    res = camp.run(bridge=mock_bridge)
    assert res.total_count == 1
    assert res.results[0].detected is True
    assert res.results[0].resilience_index > 0
    assert mock_bridge.inject_fault.called
    assert mock_bridge.send_command.called


def test_poll_detection_with_log_match():
    """_poll_detection should return detected if expected string appears in log."""
    cfg = _make_cfg()
    camp = Campaign(cfg)
    # Create a temp log file containing expected string
    import tempfile
    tf = tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False, encoding="utf-8")
    tf.write("some log\nwatchdog_reset\n")
    tf.close()
    try:
        mock_bridge = MagicMock()
        mock_bridge.read_peripheral.return_value = "0"
        mock_bridge.log_path = Path(tf.name)
        mock_bridge.send_command.return_value = True
        camp.config.faults[0].expected = "watchdog_reset"
        detected, latency = camp._poll_detection(mock_bridge, camp.config.faults[0])
        # Should detect via log quickly (timeout 500ms, poll 50ms)
        assert detected is True
    finally:
        Path(tf.name).unlink(missing_ok=True)


def test_run_single_with_bridge_factory_mocked(tmp_path):
    """_run_single_with_bridge_factory should fallback to sim if start fails, else use renode path."""
    cfg = _make_cfg()
    camp = Campaign(cfg)
    fault = camp.config.faults[0]
    weights = camp.config.scoring.weights
    thresholds = camp.config.scoring.thresholds.model_dump()

    # Patch RenodeBridge.start to simulate success with mocked bridge
    with patch("src.core.renode_bridge.RenodeBridge") as MockBridge:
        inst = MagicMock()
        inst.start.return_value = True
        inst.inject_fault.return_value = True
        inst.read_peripheral.return_value = "0x1"
        inst.send_command.return_value = True
        inst.log_path = None
        inst.stop.return_value = True
        MockBridge.return_value = inst

        tr = camp._run_single_with_bridge_factory(fault, weights, thresholds, "renode", 1234, 0)
        assert tr.fault_id == "SF-01"
        assert tr.detected is True

    # Now test fallback when start fails
    with patch("src.core.renode_bridge.RenodeBridge") as MockBridge:
        inst = MagicMock()
        inst.start.return_value = False
        MockBridge.return_value = inst
        tr2 = camp._run_single_with_bridge_factory(fault, weights, thresholds, "renode", 1234, 0)
        # fallback to sim — still returns a result
        assert tr2.fault_id == "SF-01"


def test_campaign_run_with_mocked_parallel_renode():
    """Parallel renode with mocked per-worker bridges."""
    cfg = _make_cfg(faults=[
        {"id": "SF-01", "params": {}, "expected": "", "timeout_ms": 300},
        {"id": "CF-01", "params": {}, "expected": "", "timeout_ms": 300},
    ])
    camp = Campaign(cfg)
    with patch.object(Campaign, "_run_single_with_bridge_factory") as mock_factory:
        from src.core.result_aggregator import TestResult

        def _mk(f, w, t, bin, port, idx, *a, **k):
            return TestResult(
                fault_id=f.id, status="PASS", detected=True, recovered=True, safe=True,
                latency_ms=10, recovery_ms=5, resilience_index=95, grade="A", logs="mock"
            )

        mock_factory.side_effect = _mk
        res = camp.run(parallel=2, use_renode=True, renode_bin="renode", renode_port=5000)
        assert res.total_count == 2
        assert mock_factory.call_count == 2
