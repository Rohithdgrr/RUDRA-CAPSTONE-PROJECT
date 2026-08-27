"""MetricCard — stat card with icon, value, label, per light-theme spec."""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class MetricCard(QFrame):
    def __init__(self, label: str, value: str = "--", color: str = "#2563EB", icon: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("metricCard")
        self.setMinimumWidth(140)
        self.setFixedHeight(70)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #6B7280; font-size: 11px; font-weight: 600;")
        lay.addWidget(lbl)
        row = QHBoxLayout()
        row.setSpacing(6)
        if icon:
            ic = QLabel(icon)
            ic.setStyleSheet(f"color: {color}; font-size: 16px;")
            row.addWidget(ic)
        self._val = QLabel(value)
        self._val.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 800;")
        self._val.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(self._val)
        row.addStretch()
        lay.addLayout(row)
        self._color = color

    def setValue(self, value: str | int):
        self._val.setText(str(value))

    def setColor(self, color: str):
        self._color = color
        self._val.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 800;")
