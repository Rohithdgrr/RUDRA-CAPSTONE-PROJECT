"""Sidebar navigation."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import pyqtSignal

class Sidebar(QTreeWidget):
    navigate = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)
        self.setStyleSheet("background:#2A2A3C; color:#E0E0E0;")
        self._build()
        self.itemClicked.connect(self._on_click)
    def _build(self):
        campaigns = QTreeWidgetItem(self, ["Campaigns"])
        for name in ["New", "Open", "Save", "Recent", "Templates"]:
            QTreeWidgetItem(campaigns, [name])
        fw = QTreeWidgetItem(self, ["Firmware"])
        for n in ["Load", "Select", "Build", "Verify"]:
            QTreeWidgetItem(fw, [n])
        plat = QTreeWidgetItem(self, ["Platforms"])
        for p in ["STM32", "nRF52", "RISC-V"]:
            QTreeWidgetItem(plat, [p])
        QTreeWidgetItem(self, ["Settings"])
        self.expandAll()
    def _on_click(self, item, col):
        self.navigate.emit(item.text(0))
