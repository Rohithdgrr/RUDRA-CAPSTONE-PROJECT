from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt

class CategoryRadar(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Category Scores (Sensor/Timing/Comm/Memory/Power/GPIO)"))
        self.table = QTableWidget(1, 6)
        self.table.setHorizontalHeaderLabels(["Sensor","Timing","Comm","Memory","Power","GPIO"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        for c in range(6):
            self.table.setItem(0, c, QTableWidgetItem("--"))
        lay.addWidget(self.table)

    def set_scores(self, scores: dict):
        cats = ["Sensor","Timing","Comm","Memory","Power","GPIO"]
        for i, cat in enumerate(cats):
            v = scores.get(cat, 0)
            it = self.table.item(0, i)
            if it:
                it.setText(str(v))
                it.setTextAlignment(int(Qt.AlignmentFlag.AlignCenter))
                # color by value
                col = "#4CAF50" if v >=70 else "#FF9800" if v>=50 else "#F44336"
                it.setBackground = None  # keep default; text color via foreground

