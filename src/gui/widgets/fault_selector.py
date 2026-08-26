"""Fault selector checkable tree."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt

class FaultSelector(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)
        cats = {"Sensor Faults":["SF-01","SF-02","SF-03","SF-04","SF-05","SF-06","SF-07"],
                "Timing Faults":["TF-01","TF-02","TF-03","TF-04","TF-05"],
                "Comm Faults":["CF-01","CF-02","CF-03","CF-04","CF-05","CF-06"],
                "Memory Faults":["MF-01","MF-02","MF-03","MF-04"],
                "Power Faults":["PF-01","PF-02","PF-03"],
                "GPIO Faults":["GF-01","GF-02"]}
        for cat, ids in cats.items():
            item = QTreeWidgetItem(self, [cat])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(0, Qt.CheckState.Unchecked)
            for fid in ids:
                child = QTreeWidgetItem(item, [fid])
                child.setFlags(child.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                child.setCheckState(0, Qt.CheckState.Unchecked)
        self.expandAll()
