"""Result aggregation & CampaignResult."""
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class TestResult:
    fault_id: str
    status: str  # PASS/FAIL/WARNING
    detected: bool
    recovered: bool
    safe: bool
    latency_ms: Optional[int] = None
    recovery_ms: Optional[int] = None
    resilience_index: int = 0
    grade: str = "F"
    logs: str = ""

    def diagnose(self):
        from src.core.diagnosis_engine import diagnose
        return diagnose(self)


@dataclass
class CampaignResult:
    campaign_name: str
    results: list[TestResult] = field(default_factory=list)
    resilience_index: int = 0
    grade: str = "F"

    @property
    def total_count(self): return len(self.results)
    @property
    def pass_count(self): return sum(1 for r in self.results if r.status == "PASS")
    @property
    def fail_count(self): return sum(1 for r in self.results if r.status == "FAIL")
    @property
    def warning_count(self): return sum(1 for r in self.results if r.status == "WARNING")
    @property
    def failures(self): return [r for r in self.results if r.status != "PASS"]

    def to_dict(self):
        return {
            "campaign": self.campaign_name,
            "resilience_index": self.resilience_index,
            "grade": self.grade,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "warning_count": self.warning_count,
            "total": self.total_count,
            "results": [asdict(r) for r in self.results],
        }

    def to_json(self, path):
        import json, pathlib
        pathlib.Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    def to_html(self, path):
        from src.core.report_generator import generate_html
        generate_html(self, path)

    def to_pdf(self, path):
        from src.core.report_generator import generate_pdf
        generate_pdf(self, path)

    def to_junit(self, path):
        from src.core.report_generator import generate_junit
        generate_junit(self, path)

    def compare(self, other: "CampaignResult"):
        from src.core.campaign import Campaign
        # Dummy campaign needed for compare helper; use empty config
        dummy = Campaign.__new__(Campaign)
        return dummy.compare(self, other)


@dataclass
class ComparisonResult:
    baseline: CampaignResult
    optimized: CampaignResult
    deltas: list[dict]
    delta_ri: int
    improvement_pct: float

    def to_dict(self):
        return {
            "baseline": self.baseline.to_dict(),
            "optimized": self.optimized.to_dict(),
            "deltas": self.deltas,
            "delta_ri": self.delta_ri,
            "improvement_pct": self.improvement_pct,
        }

    def to_html(self, path):
        html = f"<html><body><h1>Comparison</h1><p>Baseline {self.baseline.resilience_index} → Optimized {self.optimized.resilience_index} Δ {self.delta_ri} (+{self.improvement_pct}%)</p><table border=1><tr><th>Fault</th><th>Baseline</th><th>Optimized</th><th>Delta</th></tr>"
        for d in self.deltas:
            html += f"<tr><td>{d['fault_id']}</td><td>{d['baseline']}</td><td>{d['optimized']}</td><td>{d['delta']:+d}</td></tr>"
        html += "</table></body></html>"
        from pathlib import Path
        Path(path).write_text(html, encoding="utf-8")
