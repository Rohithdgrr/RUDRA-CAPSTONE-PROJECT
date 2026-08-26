"""Console output color-coded."""
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QColor

COLORS = {"INFO":"#2196F3", "PASS":"#4CAF50", "FAIL":"#F44336", "WARN":"#FF9800"}

class ConsoleOutput(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setStyleSheet("font-family: Consolas; font-size: 9pt; background:#1E1E2F; color:#E0E0E0;")
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

    def append_log(self, level: str, msg: str):
        color = COLORS.get(level, "#E0E0E0")
        self.append(f'<span style="color:{color}">[{level}] {msg}</span>')
        # cap 10k lines -> trim
        if self.document().blockCount() > 10000:
            c = self.textCursor()
            c.movePosition(c.MoveOperation.Start)
            c.movePosition(c.MoveOperation.Down, c.MoveMode.KeepAnchor, 5000)
            c.removeSelectedText()
