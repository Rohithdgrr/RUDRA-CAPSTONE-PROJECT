"""Fault heatmap — table colored by RI."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


class FaultHeatmap(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Fault vs RI Heatmap"))
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Fault", "RI"])
        lay.addWidget(self.table)

    def set_results(self, results):
        self.table.setRowCount(len(results))
        for i, r in enumerate(results):
            self.table.setItem(i, 0, QTableWidgetItem(r.fault_id))
            it = QTableWidgetItem(str(r.resilience_index))
            it.setTextAlignment(int(Qt.AlignmentFlag.AlignCenter))
            # heat color
            if r.resilience_index >= 70:
                it.setBackground(QColor("#4CAF50"))
                it.setForeground(QColor("#fff"))
            elif r.resilience_index >= 50:
                it.setBackground(QColor("#FF9800"))
            else:
                it.setBackground(QColor("#F44336"))
                it.setForeground(QColor("#fff"))
            self.table.setItem(i, 1, it)
