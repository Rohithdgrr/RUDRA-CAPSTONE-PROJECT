"""Circular RI gauge placeholder using QLabel + style."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar

class RIGauge(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        self.bar = QProgressBar()
        self.bar.setRange(0,100)
        self.label = QLabel("RI: --")
        lay.addWidget(self.label); lay.addWidget(self.bar)
    def set_value(self, ri:int):
        self.bar.setValue(ri)
        self.label.setText(f"RI: {ri}/100")
