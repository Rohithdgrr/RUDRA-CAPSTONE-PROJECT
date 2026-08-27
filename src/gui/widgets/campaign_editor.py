"""Campaign Editor — polished form with icons and fault table."""

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.gui.utils.icons import AppIcons


class CampaignEditor(QWidget):
    runRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # ── Header ────────────────────────────────────────────
        title_row = QHBoxLayout()
        title = QLabel("Campaign Designer")
        title.setObjectName("titleLabel")
        title_row.addWidget(title)
        title_row.addStretch()
        root.addLayout(title_row)

        subtitle = QLabel(
            "Configure and launch fault injection campaigns against your embedded firmware"
        )
        subtitle.setObjectName("subtitleLabel")
        root.addWidget(subtitle)

        root.addSpacing(4)

        # ── General Settings Group ────────────────────────────
        grp = QGroupBox("General Settings")
        form = QFormLayout()
        form.setSpacing(12)
        form.setContentsMargins(16, 20, 16, 16)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_edit = QLineEdit("Sensor Suite Validation")
        self.name_edit.setPlaceholderText("Campaign name...")
        form.addRow("Campaign:", self.name_edit)

        fw_row = QHBoxLayout()
        self.firmware_edit = QLineEdit("examples/sensor-firmware/build/sensor.elf")
        self.firmware_edit.setPlaceholderText("Path to firmware ELF/BIN...")
        self.browse_btn = QPushButton(AppIcons.open("#FFFFFF"), " Browse")
        self.browse_btn.setFixedWidth(100)
        self.browse_btn.clicked.connect(self._browse)
        fw_row.addWidget(self.firmware_edit)
        fw_row.addWidget(self.browse_btn)
        form.addRow("Firmware:", fw_row)

        self.platform = QComboBox()
        self.platform.addItems(["STM32F4 Discovery", "nRF52840 DK", "HiFive1 RISC-V"])
        form.addRow("Platform:", self.platform)

        settings_row = QHBoxLayout()
        self.duration = QSpinBox()
        self.duration.setRange(1, 3600)
        self.duration.setValue(60)
        self.duration.setSuffix("s")
        self.duration.setFixedWidth(100)
        settings_row.addWidget(self.duration)
        settings_row.addSpacing(16)
        self.parallel = QSpinBox()
        self.parallel.setRange(1, 8)
        self.parallel.setValue(4)
        self.parallel.setFixedWidth(80)
        settings_row.addWidget(self.parallel)
        settings_row.addStretch()
        form.addRow("Duration:", settings_row)

        grp.setLayout(form)
        root.addWidget(grp)

        # ── Fault Selection Table ─────────────────────────────
        fault_grp = QGroupBox("Fault Selection (27 canonical fault types)")
        fault_lay = QVBoxLayout()
        fault_lay.setContentsMargins(16, 20, 16, 16)
        fault_lay.setSpacing(8)

        fault_header = QHBoxLayout()
        select_all_btn = QPushButton(AppIcons.select("#D4D4D8"), " Select All")
        select_all_btn.setObjectName("exportBtn")
        select_all_btn.setFixedWidth(110)
        select_all_btn.clicked.connect(self._select_all)
        fault_header.addWidget(select_all_btn)

        clear_btn = QPushButton(AppIcons.stop("#D4D4D8"), " Clear")
        clear_btn.setObjectName("exportBtn")
        clear_btn.setFixedWidth(90)
        clear_btn.clicked.connect(self._clear_all)
        fault_header.addWidget(clear_btn)

        fault_header.addStretch()
        fault_lay.addLayout(fault_header)

        self.fault_table = QTableWidget(0, 4)
        self.fault_table.setHorizontalHeaderLabels(["Select", "Fault ID", "Type", "Severity"])
        self.fault_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.fault_table.setColumnWidth(0, 40)
        self.fault_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.fault_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.fault_table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.fault_table.verticalHeader().setVisible(False)
        self.fault_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.fault_table.setAlternatingRowColors(True)
        self.fault_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        fault_lay.addWidget(self.fault_table)

        # Aligned with FAULT_CATALOG (src/core/fault_injector.py) — single source of truth
        faults = [
            ("SF-01", "Stuck-at", "HIGH"),
            ("SF-02", "Gaussian Noise", "MEDIUM"),
            ("SF-03", "Impulse Noise", "HIGH"),
            ("SF-04", "Drift", "MEDIUM"),
            ("SF-05", "Bias", "MEDIUM"),
            ("SF-06", "Missing Samples", "LOW"),
            ("SF-07", "Sampling Jitter", "MEDIUM"),
            ("TF-01", "Deadline Miss", "HIGH"),
            ("TF-02", "Clock Skew", "HIGH"),
            ("TF-03", "Interrupt Storm", "CRITICAL"),
            ("TF-04", "Watchdog Timeout", "MEDIUM"),
            ("TF-05", "Race Condition", "HIGH"),
            ("CF-01", "Packet Loss", "HIGH"),
            ("CF-02", "Latency Spike", "HIGH"),
            ("CF-03", "Bus Flooding", "MEDIUM"),
            ("CF-04", "Frame Corruption", "HIGH"),
            ("CF-05", "Bus-Off State", "MEDIUM"),
            ("CF-06", "Arbitration Loss", "CRITICAL"),
            ("MF-01", "Stack Overflow", "CRITICAL"),
            ("MF-02", "Heap Corruption", "CRITICAL"),
            ("MF-03", "Flash Bit-Flip", "HIGH"),
            ("MF-04", "ECC Error", "HIGH"),
            ("PF-01", "Brownout", "HIGH"),
            ("PF-02", "Power Glitch", "MEDIUM"),
            ("PF-03", "Sleep Failure", "HIGH"),
            ("GF-01", "Pin Float/Short", "MEDIUM"),
            ("GF-02", "ADC/PWM/DMA", "HIGH"),
        ]
        self.fault_table.setRowCount(len(faults))
        for i, (fid, ftype, sev) in enumerate(faults):
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk.setCheckState(
                Qt.CheckState.Checked if sev in ("HIGH", "CRITICAL") else Qt.CheckState.Unchecked
            )
            chk.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.fault_table.setItem(i, 0, chk)
            self.fault_table.setItem(i, 1, QTableWidgetItem(fid))
            self.fault_table.setItem(i, 2, QTableWidgetItem(ftype))
            sev_item = QTableWidgetItem(sev)
            sev_colors = {
                "CRITICAL": "#EF4444",
                "HIGH": "#F97316",
                "MEDIUM": "#F59E0B",
                "LOW": "#6B7280",
            }
            sev_item.setForeground(self._color(sev_colors.get(sev, "#6B7280")))
            sev_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.fault_table.setItem(i, 3, sev_item)

        fault_grp.setLayout(fault_lay)
        root.addWidget(fault_grp)

        # ── Action Buttons ────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.run_btn = QPushButton(AppIcons.play("#FFFFFF"), "  Run Campaign")
        self.run_btn.setFixedHeight(42)
        self.run_btn.setMinimumWidth(180)
        self.run_btn.clicked.connect(lambda: self.runRequested.emit())
        btn_row.addWidget(self.run_btn)

        self.save_btn = QPushButton(AppIcons.save("#FFFFFF"), "  Save")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.setFixedHeight(42)
        btn_row.addWidget(self.save_btn)

        btn_row.addStretch()
        root.addLayout(btn_row)
        root.addStretch()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Firmware ELF", str(Path.cwd()), "ELF Files (*.elf *.bin);;All Files (*)"
        )
        if path:
            self.firmware_edit.setText(path)
            try:
                p = Path(path)
                # Efficiently read only first 4 bytes to check ELF magic (avoid loading 100 MB)
                with p.open("rb") as f:
                    magic = f.read(4)
                if magic == b"\x7fELF":
                    self.firmware_edit.setStyleSheet("border-color: #10B981;")
                    self.firmware_edit.setToolTip(f"Valid ELF — {p.stat().st_size:,} bytes")
                else:
                    self.firmware_edit.setStyleSheet("border-color: #F59E0B;")
                    self.firmware_edit.setToolTip("Warning: not ELF magic")
            except Exception:
                pass

    def _select_all(self):
        for i in range(self.fault_table.rowCount()):
            it = self.fault_table.item(i, 0)
            if it:
                it.setCheckState(Qt.CheckState.Checked)

    def _clear_all(self):
        for i in range(self.fault_table.rowCount()):
            it = self.fault_table.item(i, 0)
            if it:
                it.setCheckState(Qt.CheckState.Unchecked)

    @staticmethod
    def _color(hex_str: str):
        from PyQt6.QtGui import QColor

        return QColor(hex_str)

    def get_selected_faults(self) -> list[str]:
        ids = []
        for i in range(self.fault_table.rowCount()):
            it = self.fault_table.item(i, 0)
            if it and it.checkState() == Qt.CheckState.Checked:
                ids.append(self.fault_table.item(i, 1).text())
        return ids
