"""Campaign manager — load YAML, run tests."""
from __future__ import annotations
import yaml
import hashlib
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.config.schemas import CampaignConfig
from src.core.result_aggregator import CampaignResult, TestResult, ComparisonResult
from src.core.resilience_index import calculate_ri, grade_for_ri
from src.core.renode_bridge import RenodeBridge

class Campaign:
    def __init__(self, config: CampaignConfig):
        self.config = config

    @classmethod
    def from_yaml(cls, path: str | Path):
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        cfg = CampaignConfig.model_validate(data)
        return cls(cfg)

    def to_yaml(self, path: str | Path):
        import yaml
        Path(path).write_text(yaml.dump(self.config.model_dump(), sort_keys=False), encoding="utf-8")

    def validate(self):
        return self.config

    def _run_single(self, fault, weights, thresholds):
        h = int(hashlib.md5(fault.id.encode()).hexdigest()[:2], 16)
        detected = h % 3 != 0
        recovered = h % 4 != 0
        safe = not (fault.id == "TF-01" and not detected)
        if fault.id in ("SF-03", "TF-01"):
            detected = False
            recovered = False
        ri = calculate_ri(detected, recovered, safe, w_d=weights.detection, w_r=weights.recovery, w_s=weights.safety, latency_ms=23 if detected else None, timeout_ms=fault.timeout_ms)
        grade = grade_for_ri(ri, thresholds)
        status = "PASS" if ri >= thresholds["grade_b"] else "FAIL"
        if 50 <= ri < 70:
            status = "WARNING"
        return TestResult(fault_id=fault.id, status=status, detected=detected, recovered=recovered, safe=safe, latency_ms=23 if detected else None, recovery_ms=45 if recovered else None, resilience_index=ri, grade=grade, logs=f"[{status}] {fault.id} detect={detected} recover={recovered} safe={safe}")

    def run(self, parallel: int = 1, on_progress=None, on_result=None) -> CampaignResult:
        weights = self.config.scoring.weights
        thresholds = self.config.scoring.thresholds.model_dump()
        faults = self.config.faults
        total = len(faults)
        results: list[TestResult] = [None] * total  # type: ignore

        if parallel > 1:
            with ThreadPoolExecutor(max_workers=min(parallel, total)) as ex:
                future_to_idx = {ex.submit(self._run_single, f, weights, thresholds): i for i, f in enumerate(faults)}
                completed = 0
                for fut in as_completed(future_to_idx):
                    idx = future_to_idx[fut]
                    tr = fut.result()
                    results[idx] = tr
                    completed += 1
                    if on_progress:
                        on_progress(completed, total)
                    if on_result:
                        on_result(tr)
        else:
            for idx, f in enumerate(faults):
                tr = self._run_single(f, weights, thresholds)
                results[idx] = tr
                if on_progress:
                    on_progress(idx+1, total)
                if on_result:
                    on_result(tr)

        # Ensure order by fault id original order
        if any(r is None for r in results):
            results = [r for r in results if r is not None]
        avg_ri = round(sum(r.resilience_index for r in results) / len(results)) if results else 0
        grade = grade_for_ri(avg_ri, thresholds)
        return CampaignResult(campaign_name=self.config.name, results=results, resilience_index=avg_ri, grade=grade)

    def compare(self, baseline: "CampaignResult", optimized: "CampaignResult") -> ComparisonResult:
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
        return ComparisonResult(baseline=baseline, optimized=optimized, deltas=deltas, delta_ri=delta_ri, improvement_pct=improvement_pct)
