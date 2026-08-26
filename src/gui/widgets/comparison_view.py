"""Side-by-side comparison."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem

class ComparisonView(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        self.label = QLabel("No comparison loaded")
        lay.addWidget(self.label)
        self.table = QTableWidget(0,4)
        self.table.setHorizontalHeaderLabels(["Fault","Baseline","Optimized","Delta"])
        lay.addWidget(self.table)
