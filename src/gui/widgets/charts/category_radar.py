from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
class CategoryRadar(QWidget):
    def __init__(self):
        super().__init__()
        lay=QVBoxLayout(self); lay.addWidget(QLabel("Category Radar (6-axis, placeholder)"))
