"""Right properties panel with fault parameters and weight controls."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)


class PropertyPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(280)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # ── Fault Parameters ──────────────────────────────────
        section = QLabel("FAULT PARAMETERS")
        section.setObjectName("sectionLabel")
        root.addWidget(section)

        grp = QFrame()
        grp.setObjectName("summaryCard")
        form = QFormLayout(grp)
        form.setSpacing(10)
        form.setContentsMargins(12, 12, 12, 12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.target = QLineEdit("i2c0.sensor0")
        self.target.setPlaceholderText("Target component...")
        form.addRow("Target:", self.target)

        self.severity = QComboBox()
        self.severity.addItems(["CRITICAL", "HIGH", "MEDIUM", "LOW"])
        self.severity.setCurrentText("HIGH")
        form.addRow("Severity:", self.severity)

        self.timeout = QDoubleSpinBox()
        self.timeout.setRange(100, 60000)
        self.timeout.setValue(5000)
        self.timeout.setSuffix("ms")
        self.timeout.setDecimals(0)
        form.addRow("Timeout:", self.timeout)

        root.addWidget(grp)

        # ── RI Weights ────────────────────────────────────────
        section2 = QLabel("RI WEIGHTS")
        section2.setObjectName("sectionLabel")
        root.addWidget(section2)

        grp2 = QFrame()
        grp2.setObjectName("summaryCard")
        form2 = QFormLayout(grp2)
        form2.setSpacing(10)
        form2.setContentsMargins(12, 12, 12, 12)
        form2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.weights_d = QDoubleSpinBox()
        self.weights_d.setRange(0, 1)
        self.weights_d.setSingleStep(0.05)
        self.weights_d.setValue(0.4)
        form2.addRow("Detection:", self.weights_d)

        self.weights_r = QDoubleSpinBox()
        self.weights_r.setRange(0, 1)
        self.weights_r.setSingleStep(0.05)
        self.weights_r.setValue(0.3)
        form2.addRow("Recovery:", self.weights_r)

        self.weights_s = QDoubleSpinBox()
        self.weights_s.setRange(0, 1)
        self.weights_s.setSingleStep(0.05)
        self.weights_s.setValue(0.3)
        form2.addRow("Safety:", self.weights_s)

        root.addWidget(grp2)

        # ── Platform Info ─────────────────────────────────────
        section3 = QLabel("PLATFORM INFO")
        section3.setObjectName("sectionLabel")
        root.addWidget(section3)

        grp3 = QFrame()
        grp3.setObjectName("summaryCard")
        info_lay = QVBoxLayout(grp3)
        info_lay.setContentsMargins(12, 12, 12, 12)
        info_lay.setSpacing(6)

        for label, value in [
            ("Platform", "STM32F4 Discovery"),
            ("Architecture", "ARM Cortex-M4"),
            ("Clock", "168 MHz"),
            ("RAM", "192 KB"),
            ("Flash", "1 MB"),
        ]:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #71717A; font-size: 11px;")
            row.addWidget(lbl)
            row.addStretch()
            val = QLabel(value)
            val.setStyleSheet("color: #D4D4D8; font-size: 11px; font-weight: 600;")
            row.addWidget(val)
            info_lay.addLayout(row)

        root.addWidget(grp3)
        root.addStretch()
