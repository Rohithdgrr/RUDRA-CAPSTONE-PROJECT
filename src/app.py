"""QApplication setup."""
from PyQt6.QtWidgets import QApplication
from pathlib import Path

def create_app():
    app = QApplication([])
    app.setApplicationName("RenodeResilience")
    app.setApplicationVersion("1.0.0")
    # Load dark theme
    qss = Path(__file__).parent / "gui" / "styles" / "dark_theme.qss"
    if qss.exists():
        app.setStyleSheet(qss.read_text(encoding="utf-8"))
    return app
