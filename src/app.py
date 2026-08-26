"""QApplication setup."""
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontDatabase
from pathlib import Path

def create_app(argv=None):
    app = QApplication(argv or [])
    app.setApplicationName("RenodeResilience")
    app.setApplicationVersion("1.0.0")
    # Ensure a real font is available (fixes offscreen 'square' glyphs on headless)
    for fam in ["Segoe UI", "Arial", "Noto Sans", "Helvetica"]:
        if fam in QFontDatabase.families():
            app.setFont(QFont(fam, 10))
            break
    # Load dark theme
    qss = Path(__file__).parent / "gui" / "styles" / "dark_theme.qss"
    if qss.exists():
        try:
            app.setStyleSheet(qss.read_text(encoding="utf-8"))
        except Exception:
            pass
    return app
