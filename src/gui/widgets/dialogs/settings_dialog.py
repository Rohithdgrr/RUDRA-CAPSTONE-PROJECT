"""Settings dialog."""
from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        lay = QFormLayout(self)
        self.renode_path = QLineEdit("renode")
        lay.addRow("Renode path", self.renode_path)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        lay.addWidget(btns)
