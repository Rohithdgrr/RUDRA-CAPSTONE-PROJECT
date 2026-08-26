from src.core.result_aggregator import TestResult
from src.core.diagnosis_engine import diagnose

def test_diagnose_pass():
    tr = TestResult(fault_id="SF-01", status="PASS", detected=True, recovered=True, safe=True, resilience_index=100)
    d = diagnose(tr)
    assert d.root_cause == "No failure"
    assert d.severity == "INFO"

def test_diagnose_sf03():
    tr = TestResult(fault_id="SF-03", status="FAIL", detected=False, recovered=False, safe=True, resilience_index=0)
    d = diagnose(tr)
    assert "Impulse" in d.root_cause
    assert "median" in d.recommendations[0].lower()

def test_diagnose_tf01_critical():
    tr = TestResult(fault_id="TF-01", status="FAIL", detected=False, recovered=False, safe=False, resilience_index=0)
    d = diagnose(tr)
    assert d.severity == "CRITICAL"
    assert "watchdog" in d.recommendations[0].lower()
