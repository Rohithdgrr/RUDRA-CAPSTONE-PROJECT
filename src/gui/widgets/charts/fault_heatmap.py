"""Fault heatmap placeholder."""
from PyQt6.QtWidgets import QWidget, QLabel

class FaultHeatmap(QWidget):
    def __init__(self):
        super().__init__()
        from PyQt6.QtWidgets import QVBoxLayout
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Fault Heatmap (placeholder)"))
