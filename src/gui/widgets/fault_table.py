"""FaultTable — sortable, filterable QTableView with custom delegates per spec."""
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor
from src.core.fault_injector import FAULT_CATALOG

SEV_COLORS = {"CRITICAL": "#DC2626", "HIGH": "#DC2626", "MEDIUM": "#D97706", "LOW": "#059669"}
SEV_BG = {"CRITICAL": "#FEF2F2", "HIGH": "#FEF2F2", "MEDIUM": "#FFFBEB", "LOW": "#ECFDF5"}

class FaultTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0,0,0,0)
        lay.setSpacing(8)
        # Filter
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("Filter faults (e.g. sensor, SF-01, HIGH)...")
        self.filter.textChanged.connect(self._filter)
        lay.addWidget(self.filter)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["", "ID", "Category", "Type", "Severity", "Description"])
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 36)
        for c in range(1,6):
            hdr.setSectionResizeMode(c, QHeaderView.ResizeMode.Stretch)
        lay.addWidget(self.table)
        self._populate()
        # subtle text buttons
        self._filter()  # init

    def _populate(self):
        # Severity map (from campaign_editor aligned list)
        sev_map = {
            "SF-01":"HIGH","SF-02":"MEDIUM","SF-03":"HIGH","SF-04":"MEDIUM","SF-05":"MEDIUM","SF-06":"LOW","SF-07":"MEDIUM",
            "TF-01":"HIGH","TF-02":"HIGH","TF-03":"CRITICAL","TF-04":"MEDIUM","TF-05":"HIGH",
            "CF-01":"HIGH","CF-02":"HIGH","CF-03":"MEDIUM","CF-04":"HIGH","CF-05":"MEDIUM","CF-06":"CRITICAL",
            "MF-01":"CRITICAL","MF-02":"CRITICAL","MF-03":"HIGH","MF-04":"HIGH",
            "PF-01":"HIGH","PF-02":"MEDIUM","PF-03":"HIGH",
            "GF-01":"MEDIUM","GF-02":"HIGH",
        }
        self.table.setRowCount(len(FAULT_CATALOG))
        for i, (fid, info) in enumerate(sorted(FAULT_CATALOG.items())):
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk.setCheckState(Qt.CheckState.Checked if sev_map.get(fid) in ("HIGH","CRITICAL") else Qt.CheckState.Unchecked)
            chk.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, chk)
            self.table.setItem(i, 1, QTableWidgetItem(fid))
            self.table.setItem(i, 2, QTableWidgetItem(info["category"]))
            self.table.setItem(i, 3, QTableWidgetItem(info["name"]))
            sev = sev_map.get(fid, "MEDIUM")
            sev_item = QTableWidgetItem(sev)
            sev_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # Pill styling via foreground + background
            col = SEV_COLORS.get(sev, "#6B7280")
            sev_item.setForeground(QColor(col))
            bg = SEV_BG.get(sev, "#FFFFFF")
            sev_item.setBackground(QColor(bg))
            self.table.setItem(i, 4, sev_item)
            self.table.setItem(i, 5, QTableWidgetItem(f"Inject {fid} via {info['category']}"))

    @pyqtSlot(str)
    def _filter(self, text: str = ""):
        txt = (text or self.filter.text()).lower()
        for r in range(self.table.rowCount()):
            fid = self.table.item(r,1).text().lower() if self.table.item(r,1) else ""
            cat = self.table.item(r,2).text().lower() if self.table.item(r,2) else ""
            typ = self.table.item(r,3).text().lower() if self.table.item(r,3) else ""
            sev = self.table.item(r,4).text().lower() if self.table.item(r,4) else ""
            show = not txt or txt in fid or txt in cat or txt in typ or txt in sev
            self.table.setRowHidden(r, not show)

    def get_selected(self) -> list[str]:
        ids = []
        for r in range(self.table.rowCount()):
            it = self.table.item(r,0)
            if it and it.checkState()==Qt.CheckState.Checked:
                ids.append(self.table.item(r,1).text())
        return ids

    def select_all(self, checked=True):
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for r in range(self.table.rowCount()):
            if not self.table.isRowHidden(r):
                self.table.item(r,0).setCheckState(state)
