"""RI gauge with color grading."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt

GRADE_COLOR = {"A":"#2ECC71","B":"#3498DB","C":"#F1C40F","D":"#E67E22","F":"#E74C3C"}

def grade_for_ri(ri):
    if ri>=90: return "A"
    if ri>=70: return "B"
    if ri>=50: return "C"
    if ri>=30: return "D"
    return "F"

class RIGauge(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label = QLabel("RI: --")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size:28px;font-weight:700;color:#E0E0E0")
        self.bar = QProgressBar()
        self.bar.setRange(0,100)
        self.bar.setTextVisible(True)
        self.bar.setFormat("%v/100")
        lay.addWidget(self.label); lay.addWidget(self.bar)
    def set_value(self, ri:int):
        self.bar.setValue(ri)
        g = grade_for_ri(ri)
        c = GRADE_COLOR[g]
        self.label.setText(f"RI: {ri}/100 — Grade {g}")
        self.label.setStyleSheet(f"font-size:28px;font-weight:700;color:{c}")
        self.bar.setStyleSheet(f"QProgressBar::chunk{{background:{c}}}" )
