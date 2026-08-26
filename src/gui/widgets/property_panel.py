"""Right properties panel."""
from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QDoubleSpinBox, QLabel

class PropertyPanel(QWidget):
    def __init__(self):
        super().__init__()
        lay = QFormLayout(self)
        lay.addRow(QLabel("Fault Params"))
        self.target = QLineEdit("i2c0.sensor0")
        lay.addRow("Target", self.target)
        self.severity = QLineEdit("HIGH")
        lay.addRow("Severity", self.severity)
        self.weights_d = QDoubleSpinBox(); self.weights_d.setRange(0,1); self.weights_d.setValue(0.4)
        lay.addRow("Detection w", self.weights_d)
