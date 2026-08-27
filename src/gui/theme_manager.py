"""Theme manager — hot-swappable dark/light with persistence.

Usage:
    from src.gui.theme_manager import ThemeManager
    tm = ThemeManager(app)
    tm.set_theme("light")  # or "dark"
    tm.toggle()
"""
from __future__ import annotations

from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, QSettings
from PyQt6.QtWidgets import QApplication

LIGHT_QSS = Path(__file__).parent / "styles" / "light_theme.qss"
DARK_QSS = Path(__file__).parent / "styles" / "dark_theme.qss"


class ThemeManager(QObject):
    themeChanged = pyqtSignal(str)  # "light" | "dark"

    def __init__(self, app: QApplication | None = None, parent=None):
        super().__init__(parent)
        self.app = app or QApplication.instance()
        self.settings = QSettings("RenodeResilience", "RUDRA")
        self._current = self.settings.value("theme", "dark", type=str)
        if self._current not in ("light", "dark"):
            self._current = "dark"

    @property
    def current(self) -> str:
        return self._current

    def is_light(self) -> bool:
        return self._current == "light"

    def toggle(self) -> str:
        return self.set_theme("dark" if self._current == "light" else "light")

    def set_theme(self, name: str) -> str:
        name = name.lower()
        if name not in ("light", "dark"):
            raise ValueError(f"Unknown theme {name!r}")
        qss_path = LIGHT_QSS if name == "light" else DARK_QSS
        try:
            qss = qss_path.read_text(encoding="utf-8")
            if self.app:
                self.app.setStyleSheet(qss)
        except Exception as e:
            # Fallback: log but don't crash
            print(f"[ThemeManager] Failed to load {qss_path}: {e}")
        self._current = name
        self.settings.setValue("theme", name)
        self.themeChanged.emit(name)
        return name

    def apply_saved(self) -> str:
        """Apply theme stored in QSettings on startup."""
        return self.set_theme(self._current)
