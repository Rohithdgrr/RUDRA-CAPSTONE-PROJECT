"""Diagnosis engine — rule-based."""
from dataclasses import dataclass


@dataclass
class Diagnosis:
    fault_id: str
    root_cause: str
    category: str
    severity: str
    recommendations: list[str]
    iso_mapping: str | None = None


RULES = {
    "SF-01": ("Stuck-at not detected", "sensor_filter", "Add median filter (3-sample): if abs(value-last)>eps for N samples → flag"),
    "SF-03": ("Impulse noise not detected", "sensor_filter", "Add median filter: median=sorted(window)[1]; discard if abs(x-median)>3*sigma"),
    "TF-01": ("Deadline miss causes unsafe state", "timing", "Add task timeout + watchdog (50ms) + yield points in control loop"),
    "CF-03": ("Bus flooding anomaly threshold too high", "communication", "Lower anomaly threshold to 50Hz (was 200Hz)"),
    "MF-01": ("Stack overflow unsafe", "memory", "Increase stack 512→1024, add canary, -fstack-protector"),
}


def diagnose(test_result) -> Diagnosis:
    fid = test_result.fault_id
    # If PASS, no diagnosis needed
    if test_result.status == "PASS":
        return Diagnosis(fid, "No failure", "none", "INFO", [], None)
    rule = RULES.get(fid)
    if rule:
        cause, cat, rec = rule
        sev = "CRITICAL" if not test_result.safe else "WARNING"
        return Diagnosis(fid, cause, cat, sev, [rec], "ISO26262-6 7.4.3")
    # generic
    return Diagnosis(fid, f"{fid} failed: detected={test_result.detected} recovered={test_result.recovered} safe={test_result.safe}", "generic", "WARNING", ["Review fault handling for " + fid], None)
