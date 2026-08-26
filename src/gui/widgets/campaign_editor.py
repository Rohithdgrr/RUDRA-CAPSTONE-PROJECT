"""Campaign Editor form."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QCheckBox, QHBoxLayout, QFileDialog
from PyQt6.QtCore import pyqtSignal
from pathlib import Path

class CampaignEditor(QWidget):
    runRequested = pyqtSignal()
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Campaign Designer"))
        self.name_edit = QLineEdit("Sensor Suite Validation")
        lay.addWidget(self.name_edit)
        # Firmware row with Browse
        fw_row = QHBoxLayout()
        self.firmware_edit = QLineEdit("examples/sensor-firmware/build/sensor.elf")
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse)
        fw_row.addWidget(QLabel("Firmware"))
        fw_row.addWidget(self.firmware_edit)
        fw_row.addWidget(self.browse_btn)
        lay.addLayout(fw_row)
        self.platform = QComboBox()
        self.platform.addItems(["STM32F4 Discovery", "nRF52840 DK", "HiFive1 RISC-V"])
        lay.addWidget(self.platform)
        row = QHBoxLayout()
        self.duration = QSpinBox(); self.duration.setRange(1,3600); self.duration.setValue(60)
        self.parallel = QSpinBox(); self.parallel.setRange(1,8); self.parallel.setValue(4)
        row.addWidget(QLabel("Duration")); row.addWidget(self.duration)
        row.addWidget(QLabel("Parallel")); row.addWidget(self.parallel)
        lay.addLayout(row)
        self.fault_table = QTableWidget(0,3)
        self.fault_table.setHorizontalHeaderLabels(["ID","Type","Severity"])
        for fid, typ in [("SF-01","Stuck"),("SF-02","Noise"),("TF-01","Deadline")]:
            r = self.fault_table.rowCount(); self.fault_table.insertRow(r)
            self.fault_table.setItem(r,0,QTableWidgetItem(fid)); self.fault_table.setItem(r,1,QTableWidgetItem(typ)); self.fault_table.setItem(r,2,QTableWidgetItem("HIGH"))
        lay.addWidget(self.fault_table)
        btns = QHBoxLayout()
        self.run_btn = QPushButton("Run"); self.run_btn.clicked.connect(lambda: self.runRequested.emit())
        self.save_btn = QPushButton("Save")
        btns.addWidget(self.run_btn); btns.addWidget(self.save_btn)
        lay.addLayout(btns)
        lay.addStretch()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Firmware ELF", str(Path.cwd()), "ELF Files (*.elf *.bin);;All Files (*)")
        if path:
            self.firmware_edit.setText(path)
            # Validate ELF magic via config
            try:
                p = Path(path)
                magic = p.read_bytes()[:4]
                if magic == b"\x7fELF":
                    self.firmware_edit.setToolTip(f"Valid ELF — {p.stat().st_size} bytes")
                else:
                    self.firmware_edit.setToolTip("Warning: not ELF magic")
            except Exception:
                pass
