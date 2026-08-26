"""Campaign Editor form."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QCheckBox, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

class CampaignEditor(QWidget):
    runRequested = pyqtSignal()
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Campaign Designer"))
        self.name_edit = QLineEdit("Sensor Suite Validation")
        lay.addWidget(self.name_edit)
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
