"""Test Runner — live progress, summary cards, colored table."""

from PyQt6.QtCore import QSettings, Qt, pyqtSlot
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.gui.utils.icons import AppIcons


def _is_light() -> bool:
    return QSettings("RenodeResilience", "RUDRA").value("theme", "light") == "light"


def _status_colors() -> dict:
    if _is_light():
        return {
            "PASS": ("#059669", "#ECFDF5"),
            "FAIL": ("#DC2626", "#FEF2F2"),
            "SKIP": ("#6B7280", "#F3F4F6"),
        }
    return {
        "PASS": ("#10B981", "#052E16"),
        "FAIL": ("#EF4444", "#2D0A0A"),
        "SKIP": ("#6B7280", "#1F2937"),
    }


class TestRunnerView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # ── Header ────────────────────────────────────────────
        title = QLabel("Test Runner")
        title.setObjectName("titleLabel")
        root.addWidget(title)

        # ── Summary Cards ─────────────────────────────────────
        cards = QHBoxLayout()
        cards.setSpacing(12)
        self.card_total = self._make_card("Total", "0", "#3B82F6")
        self.card_pass = self._make_card("Passed", "0", "#10B981")
        self.card_fail = self._make_card("Failed", "0", "#EF4444")
        self.card_ri = self._make_card("RI", "--", "#8B5CF6")
        for card in [self.card_total, self.card_pass, self.card_fail, self.card_ri]:
            cards.addWidget(card)
        root.addLayout(cards)

        # ── Progress ──────────────────────────────────────────
        prog_row = QHBoxLayout()
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(10)
        prog_row.addWidget(self.progress)
        self.eta = QLabel("Waiting...")
        self.eta.setStyleSheet(f"color: {'#6B7280' if _is_light() else '#71717A'}; font-size: 12px;")
        self.eta.setFixedWidth(120)
        prog_row.addWidget(self.eta)
        root.addLayout(prog_row)

        # ── Table ─────────────────────────────────────────────
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(
            ["#", "Fault ID", "Status", "Detection", "Recovery", "Safety", "RI", "Duration"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 40)
        for c in range(1, 8):
            header.setSectionResizeMode(c, QHeaderView.ResizeMode.Stretch)
        root.addWidget(self.table)

        # ── Controls ──────────────────────────────────────────
        ctrl = QHBoxLayout()
        ctrl.addStretch()
        self.pause_btn = QPushButton(AppIcons.pause("#D4D4D8"), " Pause")
        self.pause_btn.setObjectName("exportBtn")
        self.pause_btn.setFixedWidth(110)
        ctrl.addWidget(self.pause_btn)
        self.stop_btn = QPushButton(AppIcons.stop("#FFFFFF"), " Stop")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setFixedWidth(110)
        ctrl.addWidget(self.stop_btn)
        root.addLayout(ctrl)

    def _make_card(self, label: str, value: str, color: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("summaryCard")
        frame.setFixedHeight(70)
        frame.setMinimumWidth(140)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {'#6B7280' if _is_light() else '#71717A'}; font-size: 11px; font-weight: 600;")
        lay.addWidget(lbl)
        val = QLabel(value)
        val.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 800;")
        lay.addWidget(val)
        frame._val_label = val
        return frame

    def set_progress(self, current: int, total: int):
        self.progress.setMaximum(total)
        self.progress.setValue(current)
        self.eta.setText(f"{current}/{total} faults")

    @pyqtSlot(object)
    def add_result(self, tr):
        r = self.table.rowCount()
        self.table.insertRow(r)
        status = getattr(tr, "status", "FAIL")
        # Duration = latency + recovery if available, fallback to latency_ms
        dur_val = getattr(tr, "duration_ms", None)
        if dur_val is None:
            lat = getattr(tr, "latency_ms", None)
            rec = getattr(tr, "recovery_ms", None)
            if lat is not None and rec is not None:
                dur_val = lat + rec
            elif lat is not None:
                dur_val = lat
            else:
                dur_val = 0
        row_data = [
            str(r + 1),
            getattr(tr, "fault_id", "?"),
            status,
            f"{(getattr(tr, 'latency_ms', None) or 0):.1f}ms",
            f"{(getattr(tr, 'recovery_ms', None) or 0):.1f}ms",
            "Yes" if getattr(tr, "safe", False) else "No",
            str(getattr(tr, "resilience_index", 0)),
            f"{dur_val:.0f}ms",
        ]
        for c, val in enumerate(row_data):
            item = QTableWidgetItem(val)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if c == 2:
                fg, bg = _status_colors().get(status, ("#6B7280", "#F3F4F6"))
                item.setForeground(QColor(fg))
                item.setBackground(QColor(bg))
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            elif c == 6:
                ri = getattr(tr, "resilience_index", 0)
                item.setForeground(
                    QColor("#10B981" if ri >= 70 else "#F59E0B" if ri >= 50 else "#EF4444")
                )
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            self.table.setItem(r, c, item)
        self._update_cards()

    def _update_cards(self):
        total = self.table.rowCount()
        passed = sum(
            1
            for i in range(total)
            if self.table.item(i, 2) and self.table.item(i, 2).text() == "PASS"
        )
        self.card_total._val_label.setText(str(total))
        self.card_pass._val_label.setText(str(passed))
        self.card_fail._val_label.setText(str(total - passed))
        if total > 0:
            ris = []
            for i in range(total):
                it = self.table.item(i, 6)
                if it:
                    try:
                        ris.append(int(it.text()))
                    except ValueError:
                        pass
            if ris:
                self.card_ri._val_label.setText(str(sum(ris) // len(ris)))

    def clear(self):
        self.table.setRowCount(0)
        self.progress.setValue(0)
        self.eta.setText("Waiting...")
        self.card_total._val_label.setText("0")
        self.card_pass._val_label.setText("0")
        self.card_fail._val_label.setText("0")
        self.card_ri._val_label.setText("--")
