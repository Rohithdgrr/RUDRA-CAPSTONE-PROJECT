"""Settings dialog with Renode path, theme switching, and options."""

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(420)
        self.setMinimumHeight(360)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("Application Settings")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        root.addWidget(title)

        # ── Renode ────────────────────────────────────────────
        grp1 = QGroupBox("Renode")
        form1 = QFormLayout(grp1)
        form1.setSpacing(10)
        self.use_renode = QCheckBox("Use Renode emulation (requires Renode on PATH)")
        self.use_renode.setChecked(False)
        form1.addRow(self.use_renode)
        self.renode_path = QLineEdit("renode")
        self.renode_path.setPlaceholderText("Path to renode executable...")
        form1.addRow("Executable:", self.renode_path)
        self.monitor_port = QLineEdit("1234")
        form1.addRow("Monitor Port:", self.monitor_port)
        root.addWidget(grp1)

        # ── Appearance ────────────────────────────────────────
        grp2 = QGroupBox("Appearance")
        form2 = QFormLayout(grp2)
        form2.setSpacing(10)
        self.theme = QComboBox()
        self.theme.addItems(["Dark", "Light"])
        form2.addRow("Theme:", self.theme)
        self.font_size = QComboBox()
        self.font_size.addItems(["Small (11px)", "Medium (13px)", "Large (15px)"])
        self.font_size.setCurrentIndex(1)
        form2.addRow("Font Size:", self.font_size)
        root.addWidget(grp2)

        # ── Campaign Defaults ─────────────────────────────────
        grp3 = QGroupBox("Campaign Defaults")
        form3 = QFormLayout(grp3)
        form3.setSpacing(10)
        self.auto_save = QCheckBox("Auto-save campaign results")
        self.auto_save.setChecked(True)
        form3.addRow(self.auto_save)
        self.console_output = QCheckBox("Show console output by default")
        self.console_output.setChecked(True)
        form3.addRow(self.console_output)
        root.addWidget(grp3)

        root.addStretch()

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)
