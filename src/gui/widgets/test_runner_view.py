"""Live test runner view."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSlot

class TestRunnerView(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        top = QHBoxLayout()
        self.progress = QProgressBar()
        self.eta = QLabel("ETA: --")
        top.addWidget(self.progress); top.addWidget(self.eta)
        lay.addLayout(top)
        self.table = QTableWidget(0,7)
        self.table.setHorizontalHeaderLabels(["ID","Fault","Status","Detect","Recover","Safety","RI"])
        lay.addWidget(self.table)
        btns = QHBoxLayout()
        self.stop_btn = QPushButton("Stop"); self.pause_btn = QPushButton("Pause")
        btns.addWidget(self.stop_btn); btns.addWidget(self.pause_btn)
        lay.addLayout(btns)

    def set_progress(self, cur, total):
        self.progress.setMaximum(total); self.progress.setValue(cur)
        self.eta.setText(f"{cur}/{total}")

    @pyqtSlot(object)
    def add_result(self, tr):
        r = self.table.rowCount(); self.table.insertRow(r)
        vals = [tr.fault_id, tr.fault_id, tr.status, str(tr.latency_ms), str(tr.recovery_ms), str(tr.safe), str(tr.resilience_index)]
        for c, v in enumerate(vals):
            self.table.setItem(r,c,QTableWidgetItem(v))
        # color row
        if tr.status=="PASS":
            color="#4CAF50"
        elif tr.status=="FAIL":
            color="#F44336"
        else:
            color="#FF9800"
        for c in range(7):
            it=self.table.item(r,c)
            if it: it.setBackground = None
