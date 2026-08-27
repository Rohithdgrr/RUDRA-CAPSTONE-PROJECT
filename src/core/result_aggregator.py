"""Result aggregation & CampaignResult."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class TestResult:
    fault_id: str
    status: str  # PASS/FAIL/WARNING
    detected: bool
    recovered: bool
    safe: bool
    latency_ms: int | None = None
    recovery_ms: int | None = None
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
    def total_count(self) -> int:
        return len(self.results)

    @property
    def pass_count(self) -> int:
        return sum(1 for r in self.results if r.status == "PASS")

    @property
    def fail_count(self) -> int:
        return sum(1 for r in self.results if r.status == "FAIL")

    @property
    def warning_count(self) -> int:
        return sum(1 for r in self.results if r.status == "WARNING")

    @property
    def failures(self) -> list[TestResult]:
        return [r for r in self.results if r.status != "PASS"]

    def to_dict(self) -> dict:
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
        import json

        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    def to_html(self, path):
        from src.core.report_generator import generate_html

        generate_html(self, path)

    def to_pdf(self, path):
        from src.core.report_generator import generate_pdf

        generate_pdf(self, path)

    def to_junit(self, path):
        from src.core.report_generator import generate_junit

        generate_junit(self, path)

    def compare(self, other: CampaignResult) -> ComparisonResult:
        return compare_results(self, other)


def compare_results(baseline: CampaignResult, optimized: CampaignResult) -> ComparisonResult:
    """Compare two campaign results without requiring a Campaign instance."""
    b_map = {r.fault_id: r.resilience_index for r in baseline.results}
    o_map = {r.fault_id: r.resilience_index for r in optimized.results}
    all_ids = sorted(set(b_map) | set(o_map))
    deltas = []
    for fid in all_ids:
        b = b_map.get(fid, 0)
        o = o_map.get(fid, 0)
        deltas.append({"fault_id": fid, "baseline": b, "optimized": o, "delta": o - b})
    delta_ri = optimized.resilience_index - baseline.resilience_index
    improvement_pct = round((delta_ri / max(1, baseline.resilience_index)) * 100, 1)
    return ComparisonResult(
        baseline=baseline,
        optimized=optimized,
        deltas=deltas,
        delta_ri=delta_ri,
        improvement_pct=improvement_pct,
    )


@dataclass
class ComparisonResult:
    baseline: CampaignResult
    optimized: CampaignResult
    deltas: list[dict]
    delta_ri: int
    improvement_pct: float

    def to_dict(self) -> dict:
        return {
            "baseline": self.baseline.to_dict(),
            "optimized": self.optimized.to_dict(),
            "deltas": self.deltas,
            "delta_ri": self.delta_ri,
            "improvement_pct": self.improvement_pct,
        }

    def to_html(self, path):
        html = (
            f"<html><body><h1>Comparison</h1>"
            f"<p>Baseline {self.baseline.resilience_index} &rarr; "
            f"Optimized {self.optimized.resilience_index} "
            f"&Delta; {self.delta_ri} (+{self.improvement_pct}%)</p>"
            f"<table border=1><tr><th>Fault</th><th>Baseline</th>"
            f"<th>Optimized</th><th>Delta</th></tr>"
        )
        for d in self.deltas:
            html += (
                f"<tr><td>{d['fault_id']}</td><td>{d['baseline']}</td>"
                f"<td>{d['optimized']}</td><td>{int(d['delta']):+d}</td></tr>"
            )
        html += "</table></body></html>"
        Path(path).write_text(html, encoding="utf-8")
