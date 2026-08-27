"""Comparison view — side-by-side with delta coloring and icons."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ComparisonView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("Campaign Comparison")
        title.setObjectName("titleLabel")
        root.addWidget(title)

        subtitle = QLabel("Compare two campaign runs to identify improvements and regressions")
        subtitle.setObjectName("subtitleLabel")
        root.addWidget(subtitle)

        # ── Summary Cards ─────────────────────────────────────
        cards = QHBoxLayout()
        cards.setSpacing(12)
        self.card_baseline = self._make_card("Baseline RI", "--", "#3B82F6")
        self.card_optimized = self._make_card("Optimized RI", "--", "#8B5CF6")
        self.card_delta = self._make_card("Delta", "--", "#10B981")
        self.card_improvement = self._make_card("Improvement", "--", "#F59E0B")
        for card in [
            self.card_baseline,
            self.card_optimized,
            self.card_delta,
            self.card_improvement,
        ]:
            cards.addWidget(card)
        root.addLayout(cards)

        # ── Table ─────────────────────────────────────────────
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Fault ID", "Baseline RI", "Optimized RI", "Delta", "Status"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        for c in range(5):
            self.table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeMode.Stretch)
        root.addWidget(self.table)

    def _make_card(self, label: str, value: str, color: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("summaryCard")
        frame.setFixedHeight(70)
        frame.setMinimumWidth(160)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #71717A; font-size: 11px; font-weight: 600;")
        lay.addWidget(lbl)
        val = QLabel(value)
        val.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 800;")
        lay.addWidget(val)
        frame._val_label = val
        return frame

    def show_comparison(self, baseline_results, optimized_results):
        self.table.setRowCount(0)
        b_map = {r.fault_id: r.resilience_index for r in baseline_results}
        o_map = {r.fault_id: r.resilience_index for r in optimized_results}
        all_ids = sorted(set(list(b_map.keys()) + list(o_map.keys())))

        improved = regressed = 0
        for fid in all_ids:
            b_ri = b_map.get(fid, 0)
            o_ri = o_map.get(fid, 0)
            delta = o_ri - b_ri
            if delta > 0:
                improved += 1
            elif delta < 0:
                regressed += 1

            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(fid))
            self.table.setItem(r, 1, QTableWidgetItem(str(b_ri)))
            self.table.setItem(r, 2, QTableWidgetItem(str(o_ri)))

            d_item = QTableWidgetItem(f"{int(delta):+d}")
            d_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            d_item.setForeground(
                QColor("#10B981" if delta > 0 else "#EF4444" if delta < 0 else "#6B7280")
            )
            d_font = d_item.font()
            d_font.setBold(True)
            d_item.setFont(d_font)
            self.table.setItem(r, 3, d_item)

            status = "IMPROVED" if delta > 0 else ("REGRESSED" if delta < 0 else "SAME")
            s_item = QTableWidgetItem(status)
            s_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            s_item.setForeground(
                QColor({"IMPROVED": "#10B981", "REGRESSED": "#EF4444", "SAME": "#6B7280"}[status])
            )
            self.table.setItem(r, 4, s_item)

        n = len(all_ids)
        avg_b = sum(b_map.get(fid, 0) for fid in all_ids) // n if n else 0
        avg_o = sum(o_map.get(fid, 0) for fid in all_ids) // n if n else 0
        delta_total = avg_o - avg_b
        pct = (delta_total / avg_b * 100) if avg_b else 0

        self.card_baseline._val_label.setText(str(avg_b))
        self.card_optimized._val_label.setText(str(avg_o))
        self.card_delta._val_label.setText(f"{delta_total:+d}")
        self.card_improvement._val_label.setText(f"{pct:+.1f}%")

        color = "#10B981" if delta_total >= 0 else "#EF4444"
        self.card_delta._val_label.setStyleSheet(
            f"color: {color}; font-size: 22px; font-weight: 800;"
        )
        self.card_improvement._val_label.setStyleSheet(
            f"color: {color}; font-size: 22px; font-weight: 800;"
        )
