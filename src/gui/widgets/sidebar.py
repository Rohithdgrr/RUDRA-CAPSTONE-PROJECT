"""Sidebar navigation with vector icons, sections, and hover/active states."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from src.gui.utils.icons import AppIcons


class SidebarButton(QFrame):
    """A single sidebar navigation button with icon and label."""

    clicked = pyqtSignal(str)

    def __init__(self, text: str, icon=None, nav_id: str = "", is_sub: bool = False, parent=None):
        super().__init__(parent)
        self.nav_id = nav_id or text
        self._active = False
        self._icon = icon

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(34 if is_sub else 38)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20 if is_sub else 14, 0, 12, 0)
        lay.setSpacing(10)

        if icon is not None:
            from PyQt6.QtWidgets import QPushButton

            icon_btn = QPushButton(icon, "")
            icon_btn.setFixedSize(20, 20)
            icon_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            icon_btn.setStyleSheet(
                "QPushButton { border: none; padding: 0; background: transparent; }"
            )
            lay.addWidget(icon_btn)

        self._text_label = QLabel(text)
        self._text_label.setFont(
            QFont(
                "Segoe UI",
                11 if is_sub else 12,
                QFont.Weight.DemiBold if not is_sub else QFont.Weight.Normal,
            )
        )
        lay.addWidget(self._text_label)
        lay.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.nav_id)
        super().mousePressEvent(event)

    def set_active(self, active: bool):
        self._active = active
        if active:
            self.setStyleSheet(
                "SidebarButton { background: #1E1E35; border-radius: 6px; }"
                "QLabel { color: #3B82F6 !important; }"
            )
        else:
            self.setStyleSheet("")


class SidebarSection(QFrame):
    """Section header."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 12, 0)
        lbl = QLabel(title.upper())
        lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #52525B; letter-spacing: 1px;")
        lay.addWidget(lbl)
        lay.addStretch()
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet("background: #27273A;")
        lay.addWidget(line)


class Sidebar(QWidget):
    """Modern sidebar with vector icons."""

    navigate = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setObjectName("sidebar")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 8, 0, 8)
        root.setSpacing(0)

        # Brand
        brand = QLabel("  RUDRA")
        brand.setFont(QFont("Segoe UI", 16, QFont.Weight.Black))
        brand.setStyleSheet("color: #3B82F6; padding: 8px 0 16px 0;")
        brand.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        root.addWidget(brand)

        self._buttons: list[SidebarButton] = []

        # Navigation
        root.addWidget(SidebarSection("Navigation"))
        for text, icon in [
            ("Dashboard", AppIcons.home("#71717A")),
            ("Campaigns", AppIcons.campaign("#71717A")),
            ("Reports", AppIcons.report("#71717A")),
            ("Compare", AppIcons.compare("#71717A")),
        ]:
            btn = SidebarButton(text, icon)
            btn.clicked.connect(self._on_nav)
            root.addWidget(btn)
            self._buttons.append(btn)

        root.addSpacing(8)

        # Campaign actions
        root.addWidget(SidebarSection("Campaign"))
        for text, icon in [
            ("New Campaign", AppIcons.new("#71717A")),
            ("Open Campaign", AppIcons.open("#71717A")),
            ("Save", AppIcons.save("#71717A")),
            ("Recent", AppIcons.recent("#71717A")),
            ("Templates", AppIcons.template("#71717A")),
        ]:
            btn = SidebarButton(text, icon, is_sub=True)
            btn.clicked.connect(self._on_nav)
            root.addWidget(btn)
            self._buttons.append(btn)

        root.addSpacing(8)

        # Firmware
        root.addWidget(SidebarSection("Firmware"))
        for text, icon in [
            ("Load ELF", AppIcons.load("#71717A")),
            ("Select Target", AppIcons.select("#71717A")),
            ("Build", AppIcons.build("#71717A")),
            ("Verify", AppIcons.verify("#71717A")),
        ]:
            btn = SidebarButton(text, icon, is_sub=True)
            btn.clicked.connect(self._on_nav)
            root.addWidget(btn)
            self._buttons.append(btn)

        root.addSpacing(8)

        # Platforms
        root.addWidget(SidebarSection("Platforms"))
        for text, icon in [
            ("STM32F4 Discovery", AppIcons.platform("#71717A")),
            ("nRF52840 DK", AppIcons.platform("#71717A")),
            ("HiFive1 RISC-V", AppIcons.platform("#71717A")),
        ]:
            btn = SidebarButton(text, icon, is_sub=True)
            btn.clicked.connect(self._on_nav)
            root.addWidget(btn)
            self._buttons.append(btn)

        root.addStretch()

        # Settings at bottom
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet("background: #27273A; margin: 4px 12px;")
        root.addWidget(line)
        btn = SidebarButton("Settings", AppIcons.settings("#71717A"))
        btn.clicked.connect(self._on_nav)
        root.addWidget(btn)
        self._buttons.append(btn)

        # Version
        ver = QLabel("  v1.5")
        ver.setFont(QFont("Segoe UI", 9))
        ver.setStyleSheet("color: #3F3F5A; padding: 4px 0;")
        root.addWidget(ver)

    def _on_nav(self, nav_id: str):
        for btn in self._buttons:
            btn.set_active(btn.nav_id == nav_id)
        self.navigate.emit(nav_id)
