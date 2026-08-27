"""ToastNotification — auto-dismiss top-right popup per spec."""
from PyQt6.QtWidgets import QFrame, QLabel, QHBoxLayout, QWidget, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint
from PyQt6.QtGui import QFont

class Toast(QFrame):
    def __init__(self, message: str, level: str = "info", parent: QWidget | None = None, duration: int = 3000):
        super().__init__(parent)
        self.setObjectName("toast")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        level_colors = {"info":"#2563EB","success":"#059669","warning":"#D97706","error":"#DC2626"}
        col = level_colors.get(level, "#2563EB")
        self.setStyleSheet(f"QFrame#toast {{ background: #111827; color: #FFFFFF; border-radius: 6px; padding: 10px 14px; border: 1px solid {col}; }} QLabel {{ color: #FFFFFF; font-size: 13px; }}")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12,8,12,8)
        lab = QLabel(message)
        lab.setWordWrap(True)
        lay.addWidget(lab)
        # Opacity fade
        self._effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._effect)
        self._anim = QPropertyAnimation(self._effect, b"opacity")
        self._anim.setDuration(300)
        # Auto-dismiss
        QTimer.singleShot(duration, self._fade_out)
        # Position top-right of parent/Toplevel
        self._position()
        self.show()
        self.raise_()

    def _position(self):
        parent = self.parentWidget() or self.parent()
        if parent:
            geo = parent.geometry()
            self.adjustSize()
            x = geo.x() + geo.width() - self.width() - 20
            y = geo.y() + 20
            self.move(x, y)
        else:
            self.move(20,20)

    def _fade_out(self):
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.finished.connect(self.close)
        self._anim.start()

def show_toast(parent, msg: str, level="info", duration=3000):
    return Toast(msg, level, parent, duration)
