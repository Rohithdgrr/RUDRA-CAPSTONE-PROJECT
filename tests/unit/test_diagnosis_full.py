from src.core.diagnosis_engine import diagnose, get_catalog, list_fault_ids
from src.core.result_aggregator import TestResult
from src.core.fault_injector import FAULT_CATALOG


def test_catalog_size_is_27():
    assert len(get_catalog()) == 27
    assert len(list_fault_ids()) == 27
    assert set(get_catalog().keys()) == set(FAULT_CATALOG.keys())


def test_all_faults_have_diagnosis():
    for fid in FAULT_CATALOG:
        tr = TestResult(fault_id=fid, status="FAIL", detected=False, recovered=False, safe=True, resilience_index=0)
        d = diagnose(tr)
        assert d.fault_id == fid
        assert d.root_cause != ""
        assert d.category != "none"
        assert d.severity in ("WARNING", "CRITICAL", "INFO")
        assert len(d.recommendations) >= 1
        assert d.iso_mapping is not None
        assert "ISO" in d.iso_mapping or "DO-178C" in d.iso_mapping


def test_pass_has_no_failure():
    tr = TestResult(fault_id="SF-01", status="PASS", detected=True, recovered=True, safe=True, resilience_index=100)
    d = diagnose(tr)
    assert d.root_cause == "No failure"
    assert d.severity == "INFO"
    assert d.failure_mode == "none"


def test_unsafe_critical_and_recovery_modes():
    # unsafe -> CRITICAL
    tr = TestResult(fault_id="TF-01", status="FAIL", detected=False, recovered=False, safe=False, resilience_index=0)
    d = diagnose(tr)
    assert d.severity == "CRITICAL"
    assert d.failure_mode == "unsafe"
    assert "unsafe" in d.root_cause.lower()

    # not_detected
    tr2 = TestResult(fault_id="SF-01", status="FAIL", detected=False, recovered=False, safe=True, resilience_index=10)
    d2 = diagnose(tr2)
    assert d2.failure_mode == "not_detected"

    # not_recovered
    tr3 = TestResult(fault_id="SF-01", status="FAIL", detected=True, recovered=False, safe=True, resilience_index=40)
    d3 = diagnose(tr3)
    assert d3.failure_mode == "not_recovered"
    assert "recovery failed" in d3.root_cause.lower()


def test_unknown_fault_generic():
    tr = TestResult(fault_id="XX-99", status="FAIL", detected=False, recovered=False, safe=True, resilience_index=0)
    d = diagnose(tr)
    assert d.category == "generic"
    assert "XX-99" in d.root_cause


def test_late_detection_hint():
    tr = TestResult(fault_id="SF-01", status="FAIL", detected=True, recovered=True, safe=True, resilience_index=30, latency_ms=2500, grade="D")
    d = diagnose(tr)
    # late hint appends extra rec if latency >1000
    assert any("Late detection" in r for r in d.recommendations)


def test_categories_map():
    cats = {v["category"] for v in get_catalog().values()}
    # at least 7 distinct categories across 27 faults
    assert len(cats) >= 7
