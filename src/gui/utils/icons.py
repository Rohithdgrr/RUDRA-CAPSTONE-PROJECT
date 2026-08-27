"""Programmatic vector icons — no external assets needed."""

import math

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap


def _make_icon(draw_fn, size=20, color="#A1A1AA") -> QIcon:
    """Create an icon by drawing on a QPixmap."""
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(
        QPen(
            QColor(color),
            1.6,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
    )
    p.setBrush(Qt.BrushStyle.NoBrush)
    draw_fn(p, QRectF(1, 1, size - 2, size - 2), color)
    p.end()
    return QIcon(pm)


def _draw_home(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    cx = r.x() + w / 2
    # Roof (triangle)
    roof = QPainterPath()
    roof.moveTo(cx, r.y())
    roof.lineTo(r.x(), r.y() + h * 0.45)
    roof.lineTo(r.x() + w, r.y() + h * 0.45)
    roof.closeSubpath()
    p.setBrush(QColor(c))
    p.drawPath(roof)
    # Door
    p.drawRect(QRectF(cx - w * 0.12, r.y() + h * 0.55, w * 0.24, h * 0.45))


def _draw_campaign(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    for i in range(3):
        y = r.y() + i * h / 3 + 1
        p.setBrush(QColor(c))
        p.drawRoundedRect(QRectF(r.x(), y, w * 0.65, h / 3 - 2), 2, 2)
        p.drawEllipse(QRectF(r.x() + w * 0.72, y + 1, w * 0.22, h / 3 - 4))


def _draw_report(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    # Bar chart
    col_w = w / 6
    heights = [0.9, 0.6, 0.75, 0.45, 0.85, 0.55]
    for i, pct in enumerate(heights):
        x = r.x() + i * (col_w + 1)
        bar_h = h * pct
        p.setBrush(QColor(c))
        p.drawRoundedRect(QRectF(x, r.y() + h - bar_h, col_w - 1, bar_h), 1, 1)


def _draw_compare(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    # Left arrow
    mid = r.y() + h / 2
    p.setBrush(QColor(c))
    # Left arrow body
    p.drawRect(QRectF(r.x() + 2, mid - 2, w * 0.38, 4))
    # Left arrow head
    head = QPainterPath()
    head.moveTo(r.x(), mid)
    head.lineTo(r.x() + w * 0.18, mid - 5)
    head.lineTo(r.x() + w * 0.18, mid + 5)
    head.closeSubpath()
    p.drawPath(head)
    # Right arrow body
    p.drawRect(QRectF(r.x() + w * 0.6, mid - 2, w * 0.38, 4))
    # Right arrow head
    head2 = QPainterPath()
    head2.moveTo(r.x() + w, mid)
    head2.lineTo(r.x() + w * 0.82, mid - 5)
    head2.lineTo(r.x() + w * 0.82, mid + 5)
    head2.closeSubpath()
    p.drawPath(head2)


def _draw_new(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    cx, cy = r.x() + w / 2, r.y() + h / 2
    lw = max(w * 0.12, 1.5)
    p.setPen(QPen(QColor(c), lw))
    p.drawLine(int(cx), int(r.y() + 3), int(cx), int(r.y() + h - 3))
    p.drawLine(int(r.x() + 3), int(cy), int(r.x() + w - 3), int(cy))


def _draw_open(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    # Folder shape
    p.setBrush(QColor(c))
    p.setPen(Qt.PenStyle.NoPen)
    # Tab
    p.drawRoundedRect(QRectF(r.x(), r.y(), w * 0.35, h * 0.22), 2, 2)
    # Body
    p.drawRoundedRect(QRectF(r.x(), r.y() + h * 0.15, w, h * 0.85), 2, 2)


def _draw_save(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    p.setBrush(QColor(c))
    p.setPen(Qt.PenStyle.NoPen)
    # Top clip
    p.drawRoundedRect(QRectF(r.x() + w * 0.25, r.y(), w * 0.5, h * 0.3), 2, 2)
    # Body
    p.drawRoundedRect(QRectF(r.x(), r.y() + h * 0.2, w, h * 0.8), 2, 2)
    # Clip slot
    inner = QColor("#0F0F1A") if "#3B82F6" in c else QColor("#FFFFFF")
    p.setBrush(inner)
    p.drawRect(QRectF(r.x() + w * 0.2, r.y() + h * 0.55, w * 0.6, h * 0.08))
    # Arrow down
    p.setBrush(QColor(c))
    p.drawRect(QRectF(r.x() + w * 0.35, r.y() + h * 0.4, w * 0.3, h * 0.15))


def _draw_recent(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    cx, cy = r.x() + w / 2, r.y() + h / 2
    rad = min(w, h) / 2 - 1
    # Clock circle
    p.drawEllipse(QRectF(cx - rad, cy - rad, rad * 2, rad * 2))
    # Clock hands
    p.drawLine(int(cx), int(cy), int(cx), int(cy - rad * 0.55))
    p.drawLine(int(cx), int(cy), int(cx + rad * 0.4), int(cy + rad * 0.1))


def _draw_template(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    p.setBrush(QColor(c))
    p.setPen(Qt.PenStyle.NoPen)
    # Grid of 4 squares
    gap = 2
    sw = (w - gap) / 2
    sh = (h - gap) / 2
    p.drawRoundedRect(QRectF(r.x(), r.y(), sw, sh), 2, 2)
    p.drawRoundedRect(QRectF(r.x() + sw + gap, r.y(), sw, sh), 2, 2)
    p.drawRoundedRect(QRectF(r.x(), r.y() + sh + gap, sw, sh), 2, 2)
    p.drawRoundedRect(QRectF(r.x() + sw + gap, r.y() + sh + gap, sw, sh), 2, 2)


def _draw_firmware(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    # Chip body
    p.setBrush(QColor(c))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(r.x() + w * 0.1, r.y() + h * 0.1, w * 0.8, h * 0.8), 3, 3)
    # Pins top
    for i in range(3):
        x = r.x() + w * 0.25 + i * w * 0.25
        p.drawRect(QRectF(x, r.y(), w * 0.08, h * 0.15))
    # Pins bottom
    for i in range(3):
        x = r.x() + w * 0.25 + i * w * 0.25
        p.drawRect(QRectF(x, r.y() + h * 0.85, w * 0.08, h * 0.15))


def _draw_load(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    cx = r.x() + w / 2
    # Arrow down
    p.setBrush(QColor(c))
    p.setPen(Qt.PenStyle.NoPen)
    head = QPainterPath()
    head.moveTo(cx, r.y() + h * 0.1)
    head.lineTo(r.x() + w * 0.25, r.y() + h * 0.45)
    head.lineTo(r.x() + w * 0.35, r.y() + h * 0.45)
    head.lineTo(r.x() + w * 0.35, r.y() + h * 0.9)
    head.lineTo(r.x() + w * 0.65, r.y() + h * 0.9)
    head.lineTo(r.x() + w * 0.65, r.y() + h * 0.45)
    head.lineTo(r.x() + w * 0.75, r.y() + h * 0.45)
    head.closeSubpath()
    p.drawPath(head)


def _draw_select(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    cx, cy = r.x() + w / 2, r.y() + h / 2
    rad = min(w, h) / 2 - 1
    p.drawEllipse(QRectF(cx - rad, cy - rad, rad * 2, rad * 2))
    # Checkmark
    p.setPen(QPen(QColor(c), 2))
    p.drawLine(int(cx - rad * 0.4), int(cy + 1), int(cx - rad * 0.05), int(cy + rad * 0.35))
    p.drawLine(
        int(cx - rad * 0.05), int(cy + rad * 0.35), int(cx + rad * 0.45), int(cy - rad * 0.3)
    )


def _draw_build(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    p.setPen(QPen(QColor(c), 2))
    # Hammer handle
    p.drawLine(
        int(r.x() + w * 0.15), int(r.y() + h * 0.85), int(r.x() + w * 0.55), int(r.y() + h * 0.35)
    )
    # Hammer head
    p.setBrush(QColor(c))
    p.drawRoundedRect(QRectF(r.x() + w * 0.45, r.y() + h * 0.1, w * 0.45, h * 0.3), 3, 3)


def _draw_verify(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    cx, cy = r.x() + w / 2, r.y() + h / 2
    rad = min(w, h) / 2 - 1
    p.setBrush(QColor(c))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QRectF(cx - rad, cy - rad, rad * 2, rad * 2))
    inner = QColor("#0F0F1A") if "#3B82F6" in c else QColor("#FFFFFF")
    p.setBrush(inner)
    p.drawEllipse(QRectF(cx - rad * 0.7, cy - rad * 0.7, rad * 1.4, rad * 1.4))
    p.setBrush(QColor(c))
    # Checkmark
    path = QPainterPath()
    path.moveTo(cx - rad * 0.35, cy + 1)
    path.lineTo(cx - 0.5, cy + rad * 0.3)
    path.lineTo(cx + rad * 0.35, cy - rad * 0.3)
    p.setPen(QPen(QColor(c), 2))
    p.drawPath(path)


def _draw_platform(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    # Monitor/screen
    p.setBrush(QColor(c))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(r.x() + 1, r.y(), w - 2, h * 0.7), 3, 3)
    inner = QColor("#0F0F1A")
    p.setBrush(inner)
    p.drawRoundedRect(QRectF(r.x() + 3, r.y() + 2, w - 6, h * 0.55), 2, 2)
    # Stand
    p.setBrush(QColor(c))
    p.drawRect(QRectF(r.x() + w * 0.35, r.y() + h * 0.72, w * 0.3, h * 0.1))
    p.drawRect(QRectF(r.x() + w * 0.25, r.y() + h * 0.85, w * 0.5, h * 0.08))


def _draw_settings(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    cx, cy = r.x() + w / 2, r.y() + h / 2
    rad_out = min(w, h) / 2 - 1
    rad_in = rad_out * 0.55
    # Gear teeth (8)
    teeth = 8
    for i in range(teeth):
        angle = (2 * math.pi / teeth) * i
        x1 = cx + rad_out * 0.75 * math.cos(angle)
        y1 = cy + rad_out * 0.75 * math.sin(angle)
        p.setBrush(QColor(c))
        p.setPen(Qt.PenStyle.NoPen)
        sz = rad_out * 0.35
        p.drawRect(QRectF(x1 - sz / 2, y1 - sz / 2, sz, sz))
    p.setBrush(QColor(c))
    p.drawEllipse(QRectF(cx - rad_out * 0.65, cy - rad_out * 0.65, rad_out * 1.3, rad_out * 1.3))
    inner = QColor("#0F0F1A") if "#3B82F6" in c else QColor("#FFFFFF")
    p.setBrush(inner)
    p.drawEllipse(QRectF(cx - rad_in, cy - rad_in, rad_in * 2, rad_in * 2))


def _draw_play(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    p.setBrush(QColor(c))
    p.setPen(Qt.PenStyle.NoPen)
    path = QPainterPath()
    path.moveTo(r.x() + w * 0.15, r.y() + h * 0.05)
    path.lineTo(r.x() + w * 0.85, r.y() + h * 0.5)
    path.lineTo(r.x() + w * 0.15, r.y() + h * 0.95)
    path.closeSubpath()
    p.drawPath(path)


def _draw_pdf(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    # Document
    p.setBrush(QColor(c))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(r.x() + 1, r.y(), w - 2, h), 2, 2)
    inner = QColor("#0F0F1A") if "#3B82F6" in c else QColor("#FFFFFF")
    p.setBrush(inner)
    p.drawRect(QRectF(r.x() + 3, r.y() + 3, w - 6, h - 6))
    p.setPen(QPen(QColor(c), 1.5))
    for i in range(3):
        y = r.y() + h * 0.25 + i * h * 0.2
        p.drawLine(int(r.x() + 6), int(y), int(r.x() + w - 6), int(y))


def _draw_json(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    p.setPen(QPen(QColor(c), 2))
    # Curly braces
    p.drawText(QRectF(r), Qt.AlignmentFlag.AlignCenter, "{ }")


def _draw_stop(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    p.setBrush(QColor(c))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(r.x() + 2, r.y() + 2, w - 4, h - 4), 3, 3)


def _draw_pause(p: QPainter, r: QRectF, c: str):
    w, h = r.width(), r.height()
    p.setBrush(QColor(c))
    p.setPen(Qt.PenStyle.NoPen)
    bw = w * 0.25
    p.drawRect(QRectF(r.x() + w * 0.28, r.y() + 2, bw, h - 4))
    p.drawRect(QRectF(r.x() + w * 0.62, r.y() + 2, bw, h - 4))


# ── Public API ───────────────────────────────────────────────


class AppIcons:
    """All application icons as QIcon objects."""

    @staticmethod
    def home(color="#A1A1AA"):
        return _make_icon(_draw_home, 20, color)

    @staticmethod
    def campaign(color="#A1A1AA"):
        return _make_icon(_draw_campaign, 20, color)

    @staticmethod
    def report(color="#A1A1AA"):
        return _make_icon(_draw_report, 20, color)

    @staticmethod
    def compare(color="#A1A1AA"):
        return _make_icon(_draw_compare, 20, color)

    @staticmethod
    def new(color="#A1A1AA"):
        return _make_icon(_draw_new, 20, color)

    @staticmethod
    def open(color="#A1A1AA"):
        return _make_icon(_draw_open, 20, color)

    @staticmethod
    def save(color="#A1A1AA"):
        return _make_icon(_draw_save, 20, color)

    @staticmethod
    def recent(color="#A1A1AA"):
        return _make_icon(_draw_recent, 20, color)

    @staticmethod
    def template(color="#A1A1AA"):
        return _make_icon(_draw_template, 20, color)

    @staticmethod
    def firmware(color="#A1A1AA"):
        return _make_icon(_draw_firmware, 20, color)

    @staticmethod
    def load(color="#A1A1AA"):
        return _make_icon(_draw_load, 20, color)

    @staticmethod
    def select(color="#A1A1AA"):
        return _make_icon(_draw_select, 20, color)

    @staticmethod
    def build(color="#A1A1AA"):
        return _make_icon(_draw_build, 20, color)

    @staticmethod
    def verify(color="#A1A1AA"):
        return _make_icon(_draw_verify, 20, color)

    @staticmethod
    def platform(color="#A1A1AA"):
        return _make_icon(_draw_platform, 20, color)

    @staticmethod
    def settings(color="#A1A1AA"):
        return _make_icon(_draw_settings, 20, color)

    @staticmethod
    def play(color="#A1A1AA"):
        return _make_icon(_draw_play, 20, color)

    @staticmethod
    def stop(color="#A1A1AA"):
        return _make_icon(_draw_stop, 20, color)

    @staticmethod
    def pause(color="#A1A1AA"):
        return _make_icon(_draw_pause, 20, color)

    @staticmethod
    def pdf(color="#A1A1AA"):
        return _make_icon(_draw_pdf, 20, color)

    @staticmethod
    def json(color="#A1A1AA"):
        return _make_icon(_draw_json, 20, color)
