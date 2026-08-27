"""Category radar — horizontal bar chart showing scores per category."""

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget

CATEGORIES = ["Sensor", "Timing", "Comm", "Memory", "Power", "GPIO"]
CATEGORY_COLORS = {
    "Sensor": "#3B82F6",
    "Timing": "#8B5CF6",
    "Comm": "#F59E0B",
    "Memory": "#EF4444",
    "Power": "#10B981",
    "GPIO": "#F97316",
}


class CategoryRadar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        self._scores = {c: 0 for c in CATEGORIES}

    def set_scores(self, scores: dict):
        self._scores = {c: scores.get(c, 0) for c in CATEGORIES}
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        margin_l, margin_r, margin_t, margin_b = 80, 20, 20, 20
        bar_h = 24
        gap = (h - margin_t - margin_b - len(CATEGORIES) * bar_h) // (len(CATEGORIES) + 1)

        font = QFont("Segoe UI", 10)
        p.setFont(font)

        for i, cat in enumerate(CATEGORIES):
            y = margin_t + gap + i * (bar_h + gap)
            score = self._scores[cat]
            max_bar_w = w - margin_l - margin_r

            # Label — theme aware
            try:
                is_light = QSettings("RenodeResilience", "RUDRA").value("theme", "light") == "light"
            except Exception:
                is_light = False
            label_col = "#6B7280" if is_light else "#A1A1AA"
            p.setPen(QPen(QColor(label_col)))
            p.drawText(
                0,
                y,
                margin_l - 8,
                bar_h,
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                cat,
            )

            # Background bar — light #E5E7EB / dark #1C1C32
            bg = "#E5E7EB" if is_light else "#1C1C32"
            p.setBrush(QColor(bg))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(margin_l, y, max_bar_w, bar_h, 4, 4)

            # Filled bar
            fill_w = int(max_bar_w * score / 100) if score > 0 else 0
            if fill_w > 0:
                color = QColor(CATEGORY_COLORS[cat])
                p.setBrush(color)
                p.drawRoundedRect(margin_l, y, fill_w, bar_h, 4, 4)

            # Score text — adaptive
            txt_col = "#111827" if is_light else "#F4F4F5"
            p.setPen(QPen(QColor(txt_col)))
            text_x = margin_l + fill_w + 8 if fill_w < max_bar_w - 40 else margin_l + fill_w - 30
            p.drawText(text_x, y, 40, bar_h, Qt.AlignmentFlag.AlignVCenter, f"{score}")

        p.end()
