"""Console output widget with color-coded logs and timestamps."""

from PyQt6.QtCore import QDateTime
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import QTextEdit

COLORS = {
    "INFO": "#3B82F6",
    "PASS": "#10B981",
    "FAIL": "#EF4444",
    "WARN": "#F59E0B",
    "DEBUG": "#8B5CF6",
    "FAULT": "#F97316",
}

LEVEL_ICONS = {
    "INFO": "\u2139",
    "PASS": "\u2713",
    "FAIL": "\u2717",
    "WARN": "\u26a0",
    "DEBUG": "\u2699",
    "FAULT": "\u2622",
}


class ConsoleOutput(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setFont(QFont("Cascadia Code", 11))
        self.setMinimumHeight(120)
        self._line_count = 0
        self._max_lines = 10000
        # Efficient trimming via block count (O(1)), not manual cursor removes
        self.document().setMaximumBlockCount(self._max_lines)

    def append_log(self, level: str, msg: str):
        color = COLORS.get(level, "#D4D4D8")
        icon = LEVEL_ICONS.get(level, "")
        ts = QDateTime.currentDateTime().toString("HH:mm:ss")
        html = (
            f'<span style="color:#52525B">{ts}</span> '
            f'<span style="color:{color};font-weight:700">[{icon} {level}]</span> '
            f'<span style="color:palette(text)">{msg}</span>'
        )
        self.append(html)
        self._line_count += 1
        # Trimming is handled by document().setMaximumBlockCount — no manual cursor work
        # Keep _line_count in sync for diagnostics
        if self._line_count > self._max_lines:
            self._line_count = self.document().blockCount()

        sb = self.verticalScrollBar()
        sb.setValue(sb.maximum())

    def clear_logs(self):
        self.clear()
        self._line_count = 0
