"""Resilience Index calculator — RI = (D*0.4)+(Rec*0.3)+(S*0.3)."""


def calculate_ri(detected: bool, recovered: bool, safe: bool, w_d=0.4, w_r=0.3, w_s=0.3, latency_ms=None, timeout_ms=None) -> int:
    if latency_ms is not None and timeout_ms:
        # graded detection
        if detected:
            # partial credit by latency
            d_score = max(0, 100 * (1 - latency_ms / timeout_ms))
        else:
            d_score = 0
    else:
        d_score = 100 if detected else 0
    r_score = 100 if recovered else 0
    s_score = 100 if safe else 0
    return round(d_score * w_d + r_score * w_r + s_score * w_s)


def grade_for_ri(ri: int, thresholds=None) -> str:
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
