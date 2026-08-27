"""Diagnosis engine — rule-based, covers all 27 canonical faults.

Each rule provides root-cause, category, actionable recommendations (code snippets
+ param tweaks), and ISO 26262 / DO-178C clause mapping.  diagnose() triages by
priority: unsafe > not_detected > not_recovered > late_detection.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Diagnosis:
    fault_id: str
    root_cause: str
    category: str
    severity: str  # INFO | WARNING | CRITICAL
    recommendations: list[str]
    iso_mapping: str | None = None
    # optional enrichment
    failure_mode: str | None = None  # e.g. "not_detected" | "not_recovered" | "unsafe" | "late"
    latency_ms: int | None = None


# ---------------------------------------------------------------------------
# Catalog — 27 faults, each with detection/recovery/safety diagnostics.
# Keep cause strings backward-compatible (existing tests match substrings).
# ---------------------------------------------------------------------------
# Recommendations are intentionally verbose: copy-pasteable fixes for firmware.
_CATALOG: dict[str, dict] = {
    # ── Sensor (SF) ──────────────────────────────────────────────────────────
    "SF-01": {
        "cause": "Stuck-at not detected",
        "category": "sensor_filter",
        "iso": "ISO 26262-4 7.4.3 (FTTI)",
        "recs": [
            "Add median filter (3-sample): if abs(value-last)>eps for N samples → flag stuck",
            "Code: buf[3]={v}; median=sorted(buf)[1]; if abs(v-median)<1e-3 for 20 cycles → raise stuck_at",
            "Tune eps to sensor LSB * 2; log stuck duration to aid FTTI budget",
        ],
    },
    "SF-02": {
        "cause": "Gaussian noise not filtered",
        "category": "sensor_filter",
        "iso": "ISO 26262-4 7.4.3",
        "recs": [
            "Add low-pass / Kalman filter: y = a*y + (1-a)*x, a=0.8 for 10 Hz sensor",
            "Validate: require std_dev_filtered < 2.0 after filter; add chi-square gate",
            "Alternative: increase ADC oversampling 4× and average",
        ],
    },
    "SF-03": {
        "cause": "Impulse noise not detected",
        "category": "sensor_filter",
        "iso": "ISO 26262-4 7.4.3",
        "recs": [
            "Add median filter: median=sorted(window)[1]; discard if abs(x-median)>3*sigma",
            "Add spike counter: if spike_rate > 5/60s → flag sensor_degraded",
            "Consider hardware RC filter on analog front-end",
        ],
    },
    "SF-04": {
        "cause": "Sensor drift not compensated",
        "category": "sensor_calibration",
        "iso": "ISO 26262-4 7.4.3",
        "recs": [
            "Add drift observer: estimate bias via exponential moving average, subtract",
            "Schedule periodic re-calibration every 10 min or on temperature delta >5 °C",
            "Gate: if drift > 0.5%/min → enter safe state, request maintenance",
        ],
    },
    "SF-05": {
        "cause": "Bias offset not corrected",
        "category": "sensor_calibration",
        "iso": "ISO 26262-4 7.4.3",
        "recs": [
            "Add bias correction: v_corr = v - offset, offset learned at startup (zero-point)",
            "Store factory trim in flash; validate at boot with CRC",
            "Add range check: if bias > 10% FS → flag calibration_fault",
        ],
    },
    "SF-06": {
        "cause": "Missing samples not interpolated",
        "category": "sensor_filter",
        "iso": "ISO 26262-4 7.4.3",
        "recs": [
            "Add sample counter + timeout: if no sample for 3*period → hold-last + flag",
            "Interpolate: linear between last two valid samples; limit extrapolation to 2 cycles",
            "Increase I2C timeout and add bus recovery (clock stretch 9×)",
        ],
    },
    "SF-07": {
        "cause": "Sampling jitter not tolerated",
        "category": "timing",
        "iso": "ISO 26262-6 7.4.3",
        "recs": [
            "Use hardware timer capture; add jitter buffer: accept ±5 ms, otherwise resync",
            "Timestamp each sample; reject if dt deviates >10% from nominal",
            "If jitter persistent, switch to DMA double-buffer mode",
        ],
    },
    # ── Timing (TF) ──────────────────────────────────────────────────────────
    "TF-01": {
        "cause": "Deadline miss causes unsafe state",
        "category": "timing",
        "iso": "ISO 26262-6 7.4.4 (watchdog)",
        "recs": [
            "Add task timeout + watchdog (50 ms) + yield points in control loop",
            "Set wdg window 20–60 ms; pet only after control step completes",
            "Decompose control loop; add early-exit if budget >80%",
        ],
    },
    "TF-02": {
        "cause": "Clock skew not compensated",
        "category": "timing",
        "iso": "ISO 26262-6 7.4.4",
        "recs": [
            "Add RTC sync every 60 s against monotonic clock; correct skew_ppm via PLL trim",
            "Timestamp with both RTC and systick; cross-check delta <2 ms",
            "If skew >500 ppm → flag clock_fault, enter degraded mode",
        ],
    },
    "TF-03": {
        "cause": "Interrupt storm not throttled",
        "category": "timing",
        "iso": "ISO 26262-6 7.4.4",
        "recs": [
            "Add IRQ coalescing: limit to 1kHz, drop excess with counter",
            "Raise NVIC priority for critical tasks; mask non-critical during storm",
            "Log storm rate to diagnose EMI source; add debounce on GPIO IRQ",
        ],
    },
    "TF-04": {
        "cause": "Watchdog not serviced correctly",
        "category": "timing",
        "iso": "ISO 26262-6 7.4.4",
        "recs": [
            "Service watchdog only from main loop after health checks pass",
            "Add window watchdog: pet only within 80–100% of timeout",
            "On reset, log cause to backup register for post-mortem",
        ],
    },
    "TF-05": {
        "cause": "Race condition on shared resource",
        "category": "concurrency",
        "iso": "ISO 26262-6 7.4.6",
        "recs": [
            "Protect shared state with mutex/critical section; keep CS <50 µs",
            "Use lock-free queue for ISR→task; add sequence numbers",
            "Enable ThreadSanitizer in host tests; stress with 2× threads",
        ],
    },
    # ── Communication (CF) ───────────────────────────────────────────────────
    "CF-01": {
        "cause": "Packet loss not recovered",
        "category": "communication",
        "iso": "ISO 26262-4 7.4.2",
        "recs": [
            "Add ARQ with 3 retries + timeout 100 ms; sequence numbers",
            "If loss_rate >30% → switch to safe command (hold position)",
            "Log loss bursts; correlate with bus load",
        ],
    },
    "CF-02": {
        "cause": "Latency spike not bounded",
        "category": "communication",
        "iso": "ISO 26262-4 7.4.2",
        "recs": [
            "Add deadline-aware queue: drop stale frames older than 50 ms",
            "Use priority CAN IDs for safety frames; add bus load monitor",
            "If latency >100 ms → flag comm_degraded, limit actuation",
        ],
    },
    "CF-03": {
        "cause": "Bus flooding anomaly threshold too high",
        "category": "communication",
        "iso": "ISO 26262-4 7.4.2",
        "recs": [
            "Lower anomaly threshold to 50 Hz (was 200 Hz)",
            "Add leaky-bucket rate limiter: 100 frames/s per node",
            "On flood, enter bus-quiet and notify supervisor",
        ],
    },
    "CF-04": {
        "cause": "Frame corruption not detected",
        "category": "communication",
        "iso": "ISO 26262-4 7.4.2",
        "recs": [
            "Enable CRC-16 on CAN payload; reject on mismatch",
            "Add end-to-end protection (E2E) with sequence + CRC per ISO 26262",
            "Count BER; if >1e-5 → flag link_fault",
        ],
    },
    "CF-05": {
        "cause": "Bus-off not recovered",
        "category": "communication",
        "iso": "ISO 26262-4 7.4.2",
        "recs": [
            "Implement bus-off recovery: wait 128×11 bits, re-init CAN controller",
            "Add automatic bus-off counter; after 3 events → safe state",
            "Log bus-off duration; correlate with EMI / termination",
        ],
    },
    "CF-06": {
        "cause": "Arbitration loss not handled",
        "category": "communication",
        "iso": "ISO 26262-4 7.4.2",
        "recs": [
            "Retry with backoff 1–5 ms; avoid fixed priority inversion",
            "Re-assign CAN IDs to avoid starvation of safety frames",
            "If arbitration loss >10/s → reduce bus load below 40%",
        ],
    },
    # ── Memory (MF) ──────────────────────────────────────────────────────────
    "MF-01": {
        "cause": "Stack overflow unsafe",
        "category": "memory",
        "iso": "ISO 26262-6 7.4.7 / DO-178C Level A",
        "recs": [
            "Increase stack 512→1024, add canary, -fstack-protector",
            "Enable -Wstack-usage=512; add stack watermark check at 80%",
            "Move large locals to static / heap; avoid recursion",
        ],
    },
    "MF-02": {
        "cause": "Heap corruption not detected",
        "category": "memory",
        "iso": "ISO 26262-6 7.4.7",
        "recs": [
            "Use TLSF or static pool; add red-zones + canaries per block",
            "Enable MPU: heap RX off, guard pages on overflow",
            "On malloc fail → safe state, not silent continue",
        ],
    },
    "MF-03": {
        "cause": "Flash bit-flip not corrected",
        "category": "memory",
        "iso": "ISO 26262-6 7.4.7",
        "recs": [
            "Add ECC + scrubbing: read-verify every 1 s, correct single-bit via Hamming",
            "Store critical params triply with majority vote",
            "Use flash with built-in ECC; enable controller ECC interrupt",
        ],
    },
    "MF-04": {
        "cause": "ECC error not handled",
        "category": "memory",
        "iso": "ISO 26262-6 7.4.7",
        "recs": [
            "Hook ECC fault handler: on double-bit error → safe state + log address",
            "Add periodic memory march test (C) during idle",
            "If ECC rate >1/month → flag hardware degradation",
        ],
    },
    # ── Power (PF) ───────────────────────────────────────────────────────────
    "PF-01": {
        "cause": "Brownout not handled",
        "category": "power",
        "iso": "ISO 26262-4 7.4.1",
        "recs": [
            "Enable BOR at 2.7 V; on BOR → save context to backup SRAM, safe state",
            "Add bulk cap 100 µF + early-warning comparator at 3.0 V (10 ms budget)",
            "Validate supply with brownout injection test at 2.5–3.3 V",
        ],
    },
    "PF-02": {
        "cause": "Power glitch not filtered",
        "category": "power",
        "iso": "ISO 26262-4 7.4.1",
        "recs": [
            "Add glitch filter: require 3 consecutive good samples over 5 ms",
            "Hold output during glitch <10 ms; latch fault if longer",
            "Add RC + ferrite on supply; verify with glitch_us sweep",
        ],
    },
    "PF-03": {
        "cause": "Sleep failure not detected",
        "category": "power",
        "iso": "ISO 26262-4 7.4.1",
        "recs": [
            "Verify sleep entry: check SCB->SCR.SLEEPDEEP and wake flag after 100 ms",
            "Add watchdog for sleep: if not woken in 500 ms → wake via RTC",
            "Measure sleep current; if >10× expected → flag sleep_fault",
        ],
    },
    # ── GPIO / Peripheral (GF) ───────────────────────────────────────────────
    "GF-01": {
        "cause": "Pin float/short not detected",
        "category": "gpio",
        "iso": "ISO 26262-4 7.4.3",
        "recs": [
            "Enable pull-up/down; read back pin after 1 ms: if mismatch → flag",
            "Add external pull + short detection: drive high/low and sense",
            "If float detected → set safe default (e.g., brake engaged)",
        ],
    },
    "GF-02": {
        "cause": "ADC/PWM/DMA fault not handled",
        "category": "gpio",
        "iso": "ISO 26262-4 7.4.3",
        "recs": [
            "Add ADC sanity: if raw ==0 or 4095 for 10 samples → flag saturation",
            "Watch DMA TC flag; on timeout 5 ms → reset DMA stream",
            "For PWM, add feedback capture; if duty deviates >5% → flag",
        ],
    },
}

# Backward-compat alias for old code/tests that import RULES
RULES = {
    k: (v["cause"], v["category"], v["recs"][0])
    for k, v in _CATALOG.items()
    if k in ("SF-01", "SF-03", "TF-01", "CF-03", "MF-01")
}


def _severity_for(tr) -> str:
    if tr.status == "PASS":
        return "INFO"
    if not getattr(tr, "safe", True):
        return "CRITICAL"
    # high-Ri failures that were not detected are worse
    if not getattr(tr, "detected", False):
        return "WARNING"
    return "WARNING"


def _failure_mode_for(tr) -> str:
    if tr.status == "PASS":
        return "none"
    if not getattr(tr, "safe", True):
        return "unsafe"
    if not getattr(tr, "detected", False):
        return "not_detected"
    if not getattr(tr, "recovered", False):
        return "not_recovered"
    # late detection heuristic
    latency = getattr(tr, "latency_ms", None)
    timeout = getattr(tr, "logs", None)  # not reliable; use resilience_index hint
    if latency is not None and latency > 0:
        # if latency near timeout, consider late
        # we don't have timeout here, so use grade as proxy
        if getattr(tr, "grade", "F") in ("D", "F"):
            return "late"
    return "degraded"


def diagnose(test_result) -> Diagnosis:
    """Classify a single TestResult.

    Priority: unsafe > not_detected > not_recovered > late/degraded.
    Returns enriched Diagnosis with per-fault recommendations and ISO mapping.
    """
    fid = getattr(test_result, "fault_id", "?")
    entry = _CATALOG.get(fid)

    # PASS — no failure
    if getattr(test_result, "status", "") == "PASS":
        return Diagnosis(fid, "No failure", "none", "INFO", [], None, failure_mode="none")

    # Unknown fault -> generic
    if entry is None:
        return Diagnosis(
            fid,
            f"{fid} failed: detected={getattr(test_result, 'detected', '?')} "
            f"recovered={getattr(test_result, 'recovered', '?')} "
            f"safe={getattr(test_result, 'safe', '?')}",
            "generic",
            _severity_for(test_result),
            [f"Review fault handling for {fid} — add detection, recovery, and safe-state transitions"],
            None,
            failure_mode=_failure_mode_for(test_result),
            latency_ms=getattr(test_result, "latency_ms", None),
        )

    cause = entry["cause"]
    cat = entry["category"]
    iso = entry["iso"]
    recs = list(entry["recs"])  # copy

    # Enrich with test-specific hints
    mode = _failure_mode_for(test_result)
    latency = getattr(test_result, "latency_ms", None)

    # Tailor cause for recovery/unsafe to be more precise (but keep substring for tests)
    if mode == "unsafe":
        cause = f"{cause} — unsafe state"
        # keep original first rec at index 0 for backward-compat tests, add safety as second
        recs = [recs[0], "Enter safe state immediately: disable actuation, notify supervisor", *recs[1:]] if recs else [
            "Enter safe state immediately: disable actuation, notify supervisor"
        ]
    elif mode == "not_recovered":
        cause = f"{cause} — recovery failed"
        recs = [recs[0], "Add recovery path: retry / fallback / safe-state within 100 ms", *recs[1:]] if recs else [
            "Add recovery path: retry / fallback / safe-state within 100 ms"
        ]
    elif mode == "not_detected" and latency is None:
        # keep cause as-is but add latency hint
        pass
    elif latency is not None and latency > 1000:
        recs.append(f"Late detection ({latency} ms) — reduce detection window or polling period")

    sev = _severity_for(test_result)
    # SF-03/TF-01 legacy expects CRITICAL when unsafe
    if not getattr(test_result, "safe", True):
        sev = "CRITICAL"

    return Diagnosis(
        fault_id=fid,
        root_cause=cause,
        category=cat,
        severity=sev,
        recommendations=recs,
        iso_mapping=iso,
        failure_mode=mode,
        latency_ms=latency,
    )


def get_catalog() -> dict[str, dict]:
    """Return a shallow copy of the catalog for UI / API consumers."""
    return dict(_CATALOG)


def list_fault_ids() -> list[str]:
    return sorted(_CATALOG.keys())
