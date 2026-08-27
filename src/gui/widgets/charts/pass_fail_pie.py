"""Pass/Fail pie chart widget."""

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class PassFailPie(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(160)
        self._passed = 0
        self._failed = 0

    def set_data(self, passed: int, failed: int):
        self._passed = passed
        self._failed = failed
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        size = min(w, h) - 40
        cx = w / 2
        cy = h / 2
        r = size / 2

        try:
            is_light = QSettings("RenodeResilience", "RUDRA").value("theme", "light") == "light"
        except Exception:
            is_light = False
        track = "#E5E7EB" if is_light else "#27273A"
        fg_secondary = "#6B7280" if is_light else "#A1A1AA"
        fg_primary = "#111827" if is_light else "#F4F4F5"
        total = self._passed + self._failed
        if total == 0:
            # Empty ring
            p.setPen(QPen(QColor(track), 20))
            p.drawArc(int(cx - r), int(cy - r), int(size), int(size), 0, 360 * 16)

            p.setPen(QPen(QColor(fg_secondary)))
            font = QFont("Segoe UI", 11)
            p.setFont(font)
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No data")
            p.end()
            return

        pass_angle = int(360 * 16 * self._passed / total)
        fail_angle = 360 * 16 - pass_angle

        # Draw fail arc (red)
        pen_fail = QPen(QColor("#EF4444"), 20)
        pen_fail.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen_fail)
        p.drawArc(int(cx - r), int(cy - r), int(size), int(size), 0, fail_angle)

        # Draw pass arc (green)
        pen_pass = QPen(QColor("#10B981"), 20)
        pen_pass.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen_pass)
        p.drawArc(int(cx - r), int(cy - r), int(size), int(size), fail_angle, pass_angle)

        # Center text
        p.setPen(QPen(QColor(fg_primary)))
        font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        p.setFont(font)
        pct = int(self._passed / total * 100)
        p.drawText(
            int(cx - r),
            int(cy - 14),
            int(size),
            int(size / 2),
            Qt.AlignmentFlag.AlignCenter,
            f"{pct}%",
        )

        p.setPen(QPen(QColor(fg_secondary)))
        font2 = QFont("Segoe UI", 10)
        p.setFont(font2)
        p.drawText(
            int(cx - r),
            int(cy + 10),
            int(size),
            int(size / 2),
            Qt.AlignmentFlag.AlignCenter,
            f"{self._passed}/{total} pass",
        )

        p.end()
