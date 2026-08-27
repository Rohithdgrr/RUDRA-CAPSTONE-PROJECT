"""QApplication setup."""

from pathlib import Path

from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication


def create_app(argv=None):
    app = QApplication(argv or [])
    app.setApplicationName("RenodeResilience")
    app.setApplicationVersion("1.0.0")
    for fam in ["Segoe UI", "Arial", "Noto Sans", "Helvetica"]:
        if fam in QFontDatabase.families():
            app.setFont(QFont(fam, 10))
            break
    settings = QSettings("RenodeResilience", "RUDRA")
    theme = settings.value("theme", "light", type=str)
    if theme not in ("light", "dark"):
        theme = "light"
    qss = Path(__file__).parent / "gui" / "styles" / f"{theme}_theme.qss"
    if qss.exists():
        try:
            app.setStyleSheet(qss.read_text(encoding="utf-8"))
        except Exception:
            pass
    return app
