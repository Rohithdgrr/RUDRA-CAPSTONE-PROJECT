"""RI gauge with color grading and value cap."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget

GRADE_COLOR = {
    "A": "#10B981",
    "B": "#3B82F6",
    "C": "#F59E0B",
    "D": "#F97316",
    "F": "#EF4444",
}


def grade_for_ri(ri: int) -> str:
    if ri >= 90:
        return "A"
    if ri >= 70:
        return "B"
    if ri >= 50:
        return "C"
    if ri >= 30:
        return "D"
    return "F"


class RIGauge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(160, 160)
        self._value = 0
        self._grade = "--"

    def set_value(self, ri: int):
        self._value = max(0, min(100, int(ri)))
        self._grade = grade_for_ri(self._value)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        size = min(w, h) - 16
        cx, cy = w / 2, h / 2
        r = size / 2
        pen_w = 10

        # Background circle
        p.setPen(QPen(QColor("#27273A"), pen_w))
        p.drawArc(int(cx - r), int(cy - r), int(size), int(size), 0, 360 * 16)

        # Value arc
        color = QColor(GRADE_COLOR.get(self._grade, "#A1A1AA"))
        pen = QPen(color, pen_w)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        span = int(-360 * 16 * min(self._value, 100) / 100)
        p.drawArc(int(cx - r), int(cy - r), int(size), int(size), 90 * 16, span)

        # RI value
        p.setPen(QPen(color))
        p.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        p.drawText(
            int(cx - r),
            int(cy - 20),
            int(size),
            int(size / 2),
            Qt.AlignmentFlag.AlignCenter,
            str(self._value),
        )

        # "/100"
        p.setPen(QPen(QColor("#71717A")))
        p.setFont(QFont("Segoe UI", 10))
        p.drawText(
            int(cx - r), int(cy + 8), int(size), int(size / 2), Qt.AlignmentFlag.AlignCenter, "/100"
        )

        # Grade
        p.setPen(QPen(color))
        p.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        p.drawText(
            int(cx - r),
            int(cy + 24),
            int(size),
            int(size / 2),
            Qt.AlignmentFlag.AlignCenter,
            f"Grade {self._grade}",
        )

        p.end()
