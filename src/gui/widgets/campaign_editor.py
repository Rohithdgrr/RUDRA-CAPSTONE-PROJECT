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
    QSplitter,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.gui.utils.icons import AppIcons
from src.gui.widgets.fault_table import FaultTable


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

        # ── Splitter: Settings (left) + Fault Table (right) ──
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Left panel — settings
        left_panel = QWidget()
        left_lay = QVBoxLayout(left_panel)
        left_lay.setContentsMargins(0, 0, 8, 0)
        left_lay.setSpacing(12)

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
        left_lay.addWidget(grp)
        left_lay.addStretch()
        splitter.addWidget(left_panel)

        # Right panel — FaultTable
        right_panel = QWidget()
        right_lay = QVBoxLayout(right_panel)
        right_lay.setContentsMargins(8, 0, 0, 0)
        right_lay.setSpacing(8)

        fault_header_row = QHBoxLayout()
        fault_title = QLabel("Fault Selection")
        fault_title.setObjectName("sectionLabel")
        fault_header_row.addWidget(fault_title)
        fault_header_row.addStretch()
        select_all_btn = QPushButton("Select All")
        select_all_btn.setObjectName("ghostBtn")
        select_all_btn.setFixedWidth(90)
        select_all_btn.clicked.connect(self._select_all)
        fault_header_row.addWidget(select_all_btn)
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("ghostBtn")
        clear_btn.setFixedWidth(70)
        clear_btn.clicked.connect(self._clear_all)
        fault_header_row.addWidget(clear_btn)
        right_lay.addLayout(fault_header_row)

        self.fault_table = FaultTable()
        right_lay.addWidget(self.fault_table)
        splitter.addWidget(right_panel)

        splitter.setSizes([320, 680])
        root.addWidget(splitter, 1)

        # ── Action Buttons ────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.run_btn = QPushButton(AppIcons.play("#FFFFFF"), "  Run Campaign")
        self.run_btn.setFixedHeight(42)
        self.run_btn.setMinimumWidth(180)
        self.run_btn.clicked.connect(lambda: self.runRequested.emit())
        btn_row.addWidget(self.run_btn)

        self.save_btn = QPushButton(AppIcons.save("#FFFFFF"), "  Save Draft")
        self.save_btn.setObjectName("ghostBtn")
        self.save_btn.setFixedHeight(42)
        btn_row.addWidget(self.save_btn)

        btn_row.addStretch()
        root.addLayout(btn_row)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Firmware ELF", str(Path.cwd()), "ELF Files (*.elf *.bin);;All Files (*)"
        )
        if path:
            self.firmware_edit.setText(path)
            try:
                p = Path(path)
                with p.open("rb") as f:
                    magic = f.read(4)
                if magic == b"\x7fELF":
                    self.firmware_edit.setStyleSheet("border-color: #059669;")
                    self.firmware_edit.setToolTip(f"Valid ELF — {p.stat().st_size:,} bytes")
                else:
                    self.firmware_edit.setStyleSheet("border-color: #D97706;")
                    self.firmware_edit.setToolTip("Warning: not ELF magic")
            except Exception:
                pass

    def _select_all(self):
        self.fault_table.select_all(True)

    def _clear_all(self):
        self.fault_table.select_all(False)

    def get_selected_faults(self) -> list[str]:
        return self.fault_table.get_selected()
