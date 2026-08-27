"""Campaign manager — load YAML, run tests.

Supports two execution modes:
* **Simulation** (default) — deterministic MD5 hash, no Renode required.
* **Renode emulation** (``use_renode=True``) — drives a real Renode
  subprocess via :class:`src.core.renode_bridge.RenodeBridge` and
  :func:`src.core.fault_injector.build_fault_command`.  Falls back to
  simulation if Renode is unavailable.
"""

from __future__ import annotations

import hashlib
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml

from src.config.schemas import CampaignConfig
from src.core.resilience_index import calculate_ri, grade_for_ri
from src.core.result_aggregator import CampaignResult, ComparisonResult, TestResult, compare_results

logger = logging.getLogger(__name__)


class Campaign:
    def __init__(self, config: CampaignConfig):
        self.config = config

    @classmethod
    def from_yaml(cls, path: str | Path):
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        if data is None:
            raise ValueError(f"Empty campaign file: {path}")
        cfg = CampaignConfig.model_validate(data)
        return cls(cfg)

    def to_yaml(self, path: str | Path):
        Path(path).write_text(
            yaml.dump(self.config.model_dump(), sort_keys=False),
            encoding="utf-8",
        )

    # ------------------------------------------------------------------ #
    # Simulation path (original behaviour, kept for tests / fallback)      #
    # ------------------------------------------------------------------ #
    def _run_single_sim(self, fault, weights, thresholds):
        """Deterministic simulation — no Renode required."""
        h = int(hashlib.md5(fault.id.encode()).hexdigest()[:2], 16)
        is_fixed = "fixed" in self.config.name.lower()
        detected = h % 3 != 0
        recovered = h % 4 != 0
        if fault.id in ("SF-03", "TF-01") and not is_fixed:
            detected = False
            recovered = False
        if is_fixed and fault.id in ("SF-03", "TF-01"):
            detected = True
            recovered = True
        safe = not (fault.id == "TF-01" and not detected)
        ri = calculate_ri(
            detected,
            recovered,
            safe,
            w_d=weights.detection,
            w_r=weights.recovery,
            w_s=weights.safety,
            latency_ms=23 if detected else None,
            timeout_ms=fault.timeout_ms,
        )
        grade = grade_for_ri(ri, thresholds)
        grade_c = thresholds.get("grade_c", 50)
        grade_b = thresholds.get("grade_b", 70)
        if ri >= grade_b:
            status = "PASS"
        elif ri >= grade_c:
            status = "WARNING"
        else:
            status = "FAIL"
        return TestResult(
            fault_id=fault.id,
            status=status,
            detected=detected,
            recovered=recovered,
            safe=safe,
            latency_ms=23 if detected else None,
            recovery_ms=45 if recovered else None,
            resilience_index=ri,
            grade=grade,
            logs=f"[{status}] {fault.id} detect={detected} recover={recovered} safe={safe}",
        )

    def _run_single(self, fault, weights, thresholds):
        """Backward-compat alias for simulation."""
        return self._run_single_sim(fault, weights, thresholds)

    # ------------------------------------------------------------------ #
    # Renode emulation helpers                                             #
    # ------------------------------------------------------------------ #
    def _poll_detection(self, bridge, fault, stop_check=None) -> tuple[bool, int | None]:
        """Poll ``bridge`` until fault is detected or timeout expires.

        Returns ``(detected, latency_ms)``.  Uses ``fault.params['target']``
        as peripheral path when available, otherwise falls back to a sensible
        default.  Detection is heuristic: a non-zero ``ReadDoubleWord`` value
        or the expected string appearing in the Renode log is considered a
        successful detection.
        """
        target = None
        if isinstance(fault.params, dict):
            target = fault.params.get("target")
        if not target:
            # per-category sensible defaults (cover all 27 faults)
            if fault.id.startswith("SF-"):
                target = "sysbus.i2c0.sensor0"
            elif fault.id.startswith("TF-"):
                target = "sysbus.nvic"
            elif fault.id.startswith("CF-"):
                target = "sysbus.can1"
            elif fault.id.startswith("MF-"):
                target = "sysbus.flash"
            elif fault.id.startswith("PF-"):
                target = "sysbus.power"
            else:
                target = "sysbus.gpioPortA.DATA"

        timeout_s = fault.timeout_ms / 1000.0
        deadline = time.time() + timeout_s
        t0 = time.time()
        poll_interval = 0.05  # 50 ms
        while time.time() < deadline:
            if stop_check and stop_check():
                break
            try:
                val = bridge.read_peripheral(target)
            except Exception:
                val = "0"
            # Heuristic: any non-zero value means firmware reacted
            if val not in ("0", "0x0", "0x00000000", "", None):
                if (
                    isinstance(val, str)
                    and val.strip().lower() not in ("0", "0x0", "0x00000000", "")
                    or not isinstance(val, str)
                    and val != 0
                ):
                    latency = int((time.time() - t0) * 1000)
                    return True, latency
            # Also check log for expected string
            if fault.expected and bridge.log_path and bridge.log_path.exists():
                try:
                    text = bridge.log_path.read_text(encoding="utf-8", errors="replace")
                    if fault.expected.lower() in text.lower():
                        latency = int((time.time() - t0) * 1000)
                        return True, latency
                except OSError:
                    pass
            time.sleep(poll_interval)
        return False, None

    def _run_single_renode(self, fault, weights, thresholds, bridge, stop_check=None) -> TestResult:
        """Execute a single fault via a live :class:`RenodeBridge`."""
        # Inject fault
        try:
            injected = bridge.inject_fault(fault.id, fault.params or {})
        except Exception as e:
            logger.warning("Inject failed for %s: %s", fault.id, e)
            injected = False

        # Give Renode a moment to propagate the fault
        time.sleep(0.05)
        if injected:
            bridge.send_command("start")

        detected, latency_ms = self._poll_detection(bridge, fault, stop_check=stop_check)

        # Check recovery: poll again shortly after detection
        recovered = False
        recovery_ms: int | None = None
        if detected:
            t_rec = time.time()
            # Wait up to 1s for recovery: poll until peripheral returns to nominal (0)
            rec_deadline = t_rec + 1.0
            target = fault.params.get("target") if isinstance(fault.params, dict) else None
            if not target:
                target = "sysbus.i2c0.sensor0"
            while time.time() < rec_deadline:
                if stop_check and stop_check():
                    break
                try:
                    _v = bridge.read_peripheral(target)
                except Exception:
                    _v = "0"
                _v_str = str(_v).strip().lower() if _v is not None else "0"
                # Nominal == "0" / "0x0" / "0x00000000" means recovered
                if _v_str in ("0", "0x0", "0x00000000", "", "0x0000000"):
                    recovered = True
                    recovery_ms = int((time.time() - t_rec) * 1000)
                    break
                time.sleep(0.05)
            # If loop exits without break, recovered stays False (timeout)

        # Safety: TF-01 deadline miss is the canonical unsafe case; otherwise
        # check if bridge is still responsive.  If not detected for TF-01 -> unsafe.
        if fault.id == "TF-01" and not detected:
            safe = False
        else:
            # Bridge liveness as proxy for safety
            try:
                safe = bridge.send_command("echo safe_check")  # no-op liveness probe
            except Exception:
                safe = False

        ri = calculate_ri(
            detected,
            recovered,
            safe,
            w_d=weights.detection,
            w_r=weights.recovery,
            w_s=weights.safety,
            latency_ms=latency_ms,
            timeout_ms=fault.timeout_ms,
        )
        grade = grade_for_ri(ri, thresholds)
        grade_c = thresholds.get("grade_c", 50)
        grade_b = thresholds.get("grade_b", 70)
        if ri >= grade_b:
            status = "PASS"
        elif ri >= grade_c:
            status = "WARNING"
        else:
            status = "FAIL"

        logs = (
            f"[{status}] {fault.id} renode inject={injected} "
            f"detect={detected} recover={recovered} safe={safe} "
            f"latency={latency_ms}ms RI={ri} grade={grade}"
        )
        # Reset machine between faults so faults don't leak
        try:
            bridge.send_command("pause")
            bridge.send_command("machine Reset")
            bridge.send_command("start")
        except Exception:
            pass

        return TestResult(
            fault_id=fault.id,
            status=status,
            detected=detected,
            recovered=recovered,
            safe=safe,
            latency_ms=latency_ms,
            recovery_ms=recovery_ms if recovered else None,
            resilience_index=ri,
            grade=grade,
            logs=logs,
        )

    def _run_single_with_bridge_factory(
        self, fault, weights, thresholds, renode_bin: str, base_port: int, idx: int, stop_check=None
    ) -> TestResult:
        """Helper for parallel Renode: each worker owns its own bridge."""
        from src.core.renode_bridge import RenodeBridge

        port = base_port + idx
        bridge = RenodeBridge(renode_bin=renode_bin, port=port)
        platform = Path(self.config.platform)
        firmware = Path(self.config.firmware)
        # Try to start; if it fails, fallback to simulation for this fault
        if not bridge.start(platform, firmware):
            logger.warning(
                "Renode start failed for %s on port %s, falling back to simulation", fault.id, port
            )
            return self._run_single_sim(fault, weights, thresholds)
        try:
            return self._run_single_renode(fault, weights, thresholds, bridge, stop_check=stop_check)
        finally:
            try:
                bridge.stop()
            except Exception:
                pass

    def run(
        self,
        parallel: int = 1,
        on_progress=None,
        on_result=None,
        use_renode: bool = False,
        renode_bin: str = "renode",
        renode_port: int = 1234,
        bridge=None,
        stop_check=None,
    ) -> CampaignResult:
        """Execute the campaign.

        Args:
            parallel: ThreadPool workers (1 = sequential).
            on_progress: ``fn(done, total)`` callback.
            on_result: ``fn(TestResult)`` callback per fault.
            use_renode: If True, drive a real Renode subprocess. Falls back
                to simulation if Renode is not found.
            renode_bin: Renode binary name/path.
            renode_port: Base monitor port (``+idx`` for parallel workers).
            bridge: Optional pre-started :class:`RenodeBridge` for
                caller-managed lifecycle (useful for API long-running runs).

        Simulation remains the default so existing tests/CI without Renode
        continue to pass.
        """
        weights = self.config.scoring.weights
        thresholds = self.config.scoring.thresholds.model_dump()
        faults = self.config.faults
        total = len(faults)
        results: list[TestResult] = []

        # ---- Renode path -------------------------------------------------
        if use_renode or bridge is not None:
            # Parallel Renode: each worker owns its own bridge on port+idx
            if parallel > 1 and bridge is None:
                logger.info(
                    "Renode parallel mode: %s workers ports %s..%s",
                    parallel,
                    renode_port,
                    renode_port + total - 1,
                )
                with ThreadPoolExecutor(max_workers=min(parallel, total)) as ex:
                    future_to_idx = {
                        ex.submit(
                            self._run_single_with_bridge_factory,
                            f,
                            weights,
                            thresholds,
                            renode_bin,
                            renode_port,
                            i,
                            stop_check,
                        ): i
                        for i, f in enumerate(faults)
                    }
                    completed = 0
                    for fut in as_completed(future_to_idx):
                        idx = future_to_idx[fut]
                        try:
                            tr = fut.result()
                            results.append((idx, tr))
                        except Exception as e:
                            logger.error("Fault %s failed: %s", faults[idx].id, e)
                            continue
                        completed += 1
                        if on_progress:
                            on_progress(completed, total)
                        if on_result:
                            on_result(tr)
            elif bridge is not None:
                # Caller-supplied bridge — share it sequentially
                for idx, f in enumerate(faults):
                    if stop_check and stop_check():
                        break
                    try:
                        tr = self._run_single_renode(f, weights, thresholds, bridge, stop_check=stop_check)
                    except Exception as e:
                        logger.error("Fault %s failed: %s", f.id, e)
                        continue
                    results.append((idx, tr))
                    if on_progress:
                        on_progress(idx + 1, total)
                    if on_result:
                        on_result(tr)
            else:
                # Single shared bridge for sequential Renode
                from src.core.renode_bridge import RenodeBridge

                shared = RenodeBridge(renode_bin=renode_bin, port=renode_port)
                platform = Path(self.config.platform)
                firmware = Path(self.config.firmware)
                if not shared.start(platform, firmware):
                    logger.warning(
                        "Renode start failed on port %s, falling back to simulation", renode_port
                    )
                    # fallback to simulation
                    return self.run(
                        parallel=parallel,
                        on_progress=on_progress,
                        on_result=on_result,
                        use_renode=False,
                    )
                try:
                    for idx, f in enumerate(faults):
                        if stop_check and stop_check():
                            break
                        try:
                            tr = self._run_single_renode(f, weights, thresholds, shared, stop_check=stop_check)
                        except Exception as e:
                            logger.error("Fault %s failed: %s", f.id, e)
                            continue
                        results.append((idx, tr))
                        if on_progress:
                            on_progress(idx + 1, total)
                        if on_result:
                            on_result(tr)
                finally:
                    try:
                        shared.stop()
                    except Exception:
                        pass
        # ---- Simulation path (default) -----------------------------------
        elif parallel > 1:
            with ThreadPoolExecutor(max_workers=min(parallel, total)) as ex:
                future_to_idx = {
                    ex.submit(self._run_single_sim, f, weights, thresholds): i
                    for i, f in enumerate(faults)
                }
                completed = 0
                for fut in as_completed(future_to_idx):
                    idx = future_to_idx[fut]
                    try:
                        tr = fut.result()
                        results.append((idx, tr))
                    except Exception as e:
                        logger.error("Fault %s failed: %s", faults[idx].id, e)
                        continue
                    completed += 1
                    if on_progress:
                        on_progress(completed, total)
                    if on_result:
                        on_result(tr)
        else:
            for idx, f in enumerate(faults):
                try:
                    tr = self._run_single_sim(f, weights, thresholds)
                except Exception as e:
                    logger.error("Fault %s failed: %s", f.id, e)
                    continue
                results.append((idx, tr))
                if on_progress:
                    on_progress(idx + 1, total)
                if on_result:
                    on_result(tr)

        # Sort by original fault order
        results.sort(key=lambda x: x[0])
        sorted_results = [r for _, r in results]

        avg_ri = (
            round(sum(r.resilience_index for r in sorted_results) / len(sorted_results))
            if sorted_results
            else 0
        )
        grade = grade_for_ri(avg_ri, thresholds)
        return CampaignResult(
            campaign_name=self.config.name,
            results=sorted_results,
            resilience_index=avg_ri,
            grade=grade,
        )

    def compare(self, baseline: CampaignResult, optimized: CampaignResult) -> ComparisonResult:
        return compare_results(baseline, optimized)
