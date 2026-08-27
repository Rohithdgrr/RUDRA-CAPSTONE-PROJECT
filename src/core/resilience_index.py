"""Resilience Index calculator — RI = (D*0.4)+(Rec*0.3)+(S*0.3)."""


def calculate_ri(
    detected: bool,
    recovered: bool,
    safe: bool,
    w_d: float = 0.4,
    w_r: float = 0.3,
    w_s: float = 0.3,
    latency_ms: float | None = None,
    timeout_ms: float | None = None,
) -> int:
    """Calculate Resilience Index (0-100).

    Args:
        detected: Whether the fault was detected.
        recovered: Whether the system recovered.
        safe: Whether the system remained in a safe state.
        w_d: Detection weight (default 0.4).
        w_r: Recovery weight (default 0.3).
        w_s: Safety weight (default 0.3).
        latency_ms: Detection latency in ms (optional, for graded detection).
        timeout_ms: Fault timeout in ms (must be > 0 if latency_ms is provided).

    Returns:
        Integer RI score 0-100.
    """
    if detected and latency_ms is not None and timeout_ms and timeout_ms > 0:
        d_score = max(0.0, 100.0 * (1.0 - latency_ms / timeout_ms))
    else:
        d_score = 100.0 if detected else 0.0

    r_score = 100.0 if recovered else 0.0
    s_score = 100.0 if safe else 0.0
    return round(d_score * w_d + r_score * w_r + s_score * w_s)


def grade_for_ri(ri: int, thresholds: dict | None = None) -> str:
    """Map RI score to grade A-F using configurable thresholds."""
    if thresholds is None:
        thresholds = {"grade_a": 90, "grade_b": 70, "grade_c": 50, "grade_d": 30}
    if ri >= thresholds["grade_a"]:
        return "A"
    if ri >= thresholds["grade_b"]:
        return "B"
    if ri >= thresholds["grade_c"]:
        return "C"
    if ri >= thresholds["grade_d"]:
        return "D"
    return "F"
