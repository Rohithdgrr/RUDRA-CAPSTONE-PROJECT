from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
class TimelineChart(QWidget):
    def __init__(self):
        super().__init__()
        lay=QVBoxLayout(self); lay.addWidget(QLabel("Timeline Chart (latency, placeholder)"))
