"""MainWindow — QMainWindow with welcome screen, icons, theme switching."""

import json
from pathlib import Path

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDockWidget,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.core.campaign import Campaign
from src.core.test_runner import TestRunner
from src.gui.theme_manager import ThemeManager
from src.gui.utils.icons import AppIcons
from src.gui.widgets.campaign_editor import CampaignEditor
from src.gui.widgets.charts.category_radar import CategoryRadar
from src.gui.widgets.charts.pass_fail_pie import PassFailPie
from src.gui.widgets.charts.ri_gauge import RIGauge
from src.gui.widgets.comparison_view import ComparisonView
from src.gui.widgets.console_output import ConsoleOutput
from src.gui.widgets.dialogs.settings_dialog import SettingsDialog
from src.gui.widgets.metric_card import MetricCard
from src.gui.widgets.property_panel import PropertyPanel
from src.gui.widgets.report_viewer import ReportViewer
from src.gui.widgets.sidebar import Sidebar
from src.gui.widgets.test_runner_view import TestRunnerView
from src.gui.widgets.toast import show_toast

DARK_THEME = Path(__file__).parent / "gui" / "styles" / "dark_theme.qss"
LIGHT_THEME = Path(__file__).parent / "gui" / "styles" / "light_theme.qss"


class WelcomeScreen(QWidget):
    """Professional welcome screen with cards and quick actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 40, 40, 40)
        root.setSpacing(20)

        # ── Hero ──────────────────────────────────────────────
        hero = QVBoxLayout()
        hero.setSpacing(6)

        brand = QLabel("RUDRA")
        brand.setFont(QFont("Segoe UI", 36, QFont.Weight.Black))
        brand.setStyleSheet("color: #3B82F6;")
        hero.addWidget(brand)

        tagline = QLabel("RenodeResilience Fault Injection & Testing Framework")
        tagline.setFont(QFont("Segoe UI", 16))
        tagline.setStyleSheet("color: #A1A1AA;")
        hero.addWidget(tagline)

        desc = QLabel(
            "Automated fault injection, resilience scoring (RI 0-100), diagnosis engine,\n"
            "and comprehensive reporting for embedded firmware on Renode."
        )
        desc.setFont(QFont("Segoe UI", 12))
        desc.setStyleSheet("color: #71717A;")
        hero.addWidget(desc)

        root.addLayout(hero)
        root.addSpacing(8)

        # ── Quick Actions ─────────────────────────────────────
        actions_label = QLabel("QUICK ACTIONS")
        actions_label.setObjectName("sectionLabel")
        root.addWidget(actions_label)

        actions_grid = QGridLayout()
        actions_grid.setSpacing(12)

        cards_data = [
            (
                "New Campaign",
                "Create and configure a new fault injection campaign",
                AppIcons.new("#3B82F6"),
                "#3B82F6",
            ),
            (
                "Run Demo",
                "Execute the 3-fault sensor suite demo",
                AppIcons.play("#10B981"),
                "#10B981",
            ),
            (
                "Open Report",
                "View the latest campaign report",
                AppIcons.report("#8B5CF6"),
                "#8B5CF6",
            ),
            (
                "Compare Runs",
                "Compare two campaign results side by side",
                AppIcons.compare("#F59E0B"),
                "#F59E0B",
            ),
        ]

        for i, (title, desc_text, icon, color) in enumerate(cards_data):
            card = QFrame()
            card.setObjectName("card")
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.setFixedHeight(90)
            card_lay = QHBoxLayout(card)
            card_lay.setContentsMargins(20, 16, 20, 16)
            card_lay.setSpacing(16)

            # Icon
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(28, 28))
            icon_label.setFixedSize(28, 28)
            card_lay.addWidget(icon_label)

            # Text column
            text_col = QVBoxLayout()
            text_col.setSpacing(4)
            t = QLabel(title)
            t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            t.setStyleSheet("color: #F4F4F5;")
            text_col.addWidget(t)
            d = QLabel(desc_text)
            d.setStyleSheet("color: #71717A; font-size: 11px;")
            d.setWordWrap(True)
            text_col.addWidget(d)
            text_col.addStretch()
            card_lay.addLayout(text_col, 1)

            actions_grid.addWidget(card, i // 2, i % 2)

        root.addLayout(actions_grid)
        root.addSpacing(8)

        # ── Recent Campaigns ──────────────────────────────────
        recent_label = QLabel("RECENT CAMPAIGNS")
        recent_label.setObjectName("sectionLabel")
        root.addWidget(recent_label)

        recent_data = [
            (
                "Sensor Suite Validation",
                "3 faults  |  RI: 30/100  |  Grade D",
                "Today",
                AppIcons.campaign("#3B82F6"),
            ),
            (
                "Full 27-Fault Campaign",
                "27 faults  |  RI: 78/100  |  Grade B",
                "Yesterday",
                AppIcons.campaign("#10B981"),
            ),
            (
                "Motor Controller Test",
                "5 faults  |  RI: 65/100  |  Grade C",
                "2 days ago",
                AppIcons.campaign("#8B5CF6"),
            ),
        ]

        for name, info, date, icon in recent_data:
            row = QFrame()
            row.setObjectName("card")
            row.setFixedHeight(56)
            row.setCursor(Qt.CursorShape.PointingHandCursor)
            row_lay = QHBoxLayout(row)
            row_lay.setContentsMargins(16, 8, 16, 8)
            row_lay.setSpacing(14)

            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(20, 20))
            icon_label.setFixedSize(20, 20)
            row_lay.addWidget(icon_label)

            n = QLabel(name)
            n.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
            n.setStyleSheet("color: #F4F4F5;")
            row_lay.addWidget(n)

            row_lay.addStretch()

            i = QLabel(info)
            i.setStyleSheet("color: #71717A; font-size: 11px;")
            row_lay.addWidget(i)

            row_lay.addSpacing(16)

            d = QLabel(date)
            d.setStyleSheet("color: #52525B; font-size: 11px;")
            row_lay.addWidget(d)

            root.addWidget(row)

        root.addStretch()

        # ── Footer ────────────────────────────────────────────
        footer = QLabel(
            "v1.5  |  27 Faults  |  3 Platforms  |  Python 3.11+  |  PyQt6  |  Renode 1.15+"
        )
        footer.setStyleSheet("color: #3F3F5A; font-size: 10px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(footer)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RenodeResilience v1.5")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        self.settings = QSettings("RenodeResilience", "RUDRA")
        self._current_theme = self.settings.value("theme", "light", type=str)
        if self._current_theme not in ("light", "dark"):
            self._current_theme = "light"
        # Theme manager (hot-swap)
        self.theme_manager = None  # init after app exists, wired in _init_theme
        # Renode settings (from SettingsDialog) — persisted via QSettings
        self._use_renode = self.settings.value("renode/use_renode", False, type=bool)
        self._renode_bin = self.settings.value("renode/bin", "renode", type=str)
        self._renode_port = int(self.settings.value("renode/port", 1234))
        # Restore geometry if available
        try:
            geom = self.settings.value("geometry")
            if geom:
                self.restoreGeometry(geom)
            state = self.settings.value("windowState")
            if state:
                self.restoreState(state)
        except Exception:
            pass

        # ── Central Stack ─────────────────────────────────────
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)

        self.welcome = WelcomeScreen()
        self.central_stack.addWidget(self.welcome)  # 0

        self.editor = CampaignEditor()
        self.central_stack.addWidget(self.editor)  # 1

        self.runner = TestRunnerView()
        self.central_stack.addWidget(self.runner)  # 2

        # Report with charts
        self.report_container = QWidget()
        rc_layout = QVBoxLayout(self.report_container)
        rc_layout.setContentsMargins(0, 0, 0, 0)

        charts_frame = QFrame()
        charts_frame.setObjectName("summaryCard")
        charts_lay = QHBoxLayout(charts_frame)
        charts_lay.setContentsMargins(16, 12, 16, 12)
        charts_lay.setSpacing(16)

        self.ri_gauge = RIGauge()
        self.ri_gauge.setFixedWidth(200)
        charts_lay.addWidget(self.ri_gauge)

        self.pass_fail_pie = PassFailPie()
        self.pass_fail_pie.setFixedWidth(160)
        charts_lay.addWidget(self.pass_fail_pie)

        self.category_radar = CategoryRadar()
        charts_lay.addWidget(self.category_radar)

        rc_layout.addWidget(charts_frame)

        self.report = ReportViewer()
        rc_layout.addWidget(self.report)
        self.central_stack.addWidget(self.report_container)  # 3

        self.compare = ComparisonView()
        self.central_stack.addWidget(self.compare)  # 4

        # ── Sidebar Dock ──────────────────────────────────────
        self.sidebar_dock = QDockWidget("Navigation", self)
        self.sidebar = Sidebar()
        self.sidebar_dock.setWidget(self.sidebar)
        self.sidebar_dock.setMinimumWidth(220)
        self.sidebar_dock.setMaximumWidth(220)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar_dock)
        self.sidebar.navigate.connect(self._navigate)

        # ── Properties Dock ───────────────────────────────────
        self.props_dock = QDockWidget("Properties", self)
        self.props_panel = PropertyPanel()
        self.props_dock.setWidget(self.props_panel)
        self.props_dock.setMinimumWidth(280)
        self.props_dock.setMaximumWidth(280)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.props_dock)

        # ── Console Dock ──────────────────────────────────────
        self.console_dock = QDockWidget("Console", self)
        self.console = ConsoleOutput()
        self.console_dock.setWidget(self.console)
        self.console_dock.setMinimumHeight(120)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.console_dock)

        # ── Status Bar ────────────────────────────────────────
        self.statusBar().showMessage("Ready  |  Renode: idle")

        # ── Wiring ────────────────────────────────────────────
        self.editor.runRequested.connect(self._run_campaign)
        self.runner.stop_btn.clicked.connect(self._stop_campaign)
        self._runner_thread = None

        # ── Menu Bar ──────────────────────────────────────────
        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        file_menu.addAction(AppIcons.new("#A1A1AA"), "New Campaign", self._new_campaign)
        file_menu.addAction(AppIcons.open("#A1A1AA"), "Open Campaign", self._open_campaign)
        file_menu.addSeparator()
        file_menu.addAction(AppIcons.settings("#A1A1AA"), "Settings", self._open_settings)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        view_menu = menu.addMenu("View")
        view_menu.addAction(
            AppIcons.home("#A1A1AA"), "Dashboard", lambda: self.central_stack.setCurrentIndex(0)
        )
        view_menu.addAction(
            AppIcons.campaign("#A1A1AA"),
            "Campaign Designer",
            lambda: self.central_stack.setCurrentIndex(1),
        )
        view_menu.addAction(
            AppIcons.compare("#A1A1AA"), "Compare", lambda: self.central_stack.setCurrentIndex(4)
        )
        view_menu.addSeparator()

        self._toggle_console_action = view_menu.addAction(
            AppIcons.report("#A1A1AA"), "Toggle Console", self._toggle_console
        )

        view_menu.addSeparator()

        # Theme submenu
        theme_menu = view_menu.addMenu("Theme")
        self._dark_action = theme_menu.addAction("Dark", lambda: self._set_theme("dark"))
        self._light_action = theme_menu.addAction("Light", lambda: self._set_theme("light"))
        self._dark_action.setCheckable(True)
        self._light_action.setCheckable(True)
        self._dark_action.setChecked(self._current_theme == "dark")
        self._light_action.setChecked(self._current_theme == "light")

        help_menu = menu.addMenu("Help")
        help_menu.addAction("About", self._show_about)

        # Theme manager (after menu actions exist)
        try:
            from PyQt6.QtWidgets import QApplication
            self.theme_manager = ThemeManager(QApplication.instance(), self)
            self.theme_manager.themeChanged.connect(self._on_theme_changed)
            self.theme_manager.set_theme(self._current_theme)
        except Exception:
            self._set_theme(self._current_theme)

        # Wire property panel to fault selection
        try:
            self.editor.fault_table.itemSelectionChanged.connect(self._on_fault_selected)
            self.editor.fault_table.itemChanged.connect(lambda _: self._on_fault_selected())
        except Exception:
            pass

    def _set_theme(self, theme: str):
        self._current_theme = theme
        self.settings.setValue("theme", theme)
        # Prefer ThemeManager if available
        if hasattr(self, "theme_manager") and self.theme_manager:
            try:
                self.theme_manager.set_theme(theme)
            except Exception:
                pass
        else:
            qss = DARK_THEME if theme == "dark" else LIGHT_THEME
            if qss.exists():
                try:
                    self.setStyleSheet(qss.read_text(encoding="utf-8"))
                except Exception:
                    pass
        self._dark_action.setChecked(theme == "dark")
        self._light_action.setChecked(theme == "light")

    def _on_theme_changed(self, theme: str):
        # Hook for toast + chart recolor if needed
        try:
            show_toast(self, f"Theme: {theme.capitalize()}", "info", 1500)
        except Exception:
            pass

    def _navigate(self, nav_id: str):
        mapping = {
            "Dashboard": 0,
            "New Campaign": 1,
            "Open Campaign": 1,
            "Campaigns": 1,
            "Reports": 3,
            "Compare": 4,
            "New": 1,
            "Open": 1,
            "Save": None,
            "Recent": 0,
            "Templates": 0,
            "Load ELF": 1,
            "Select Target": 1,
            "Build": 1,
            "Verify": 1,
            "STM32F4 Discovery": 1,
            "nRF52840 DK": 1,
            "HiFive1 RISC-V": 1,
            "Settings": None,
        }
        idx = mapping.get(nav_id)
        if idx is not None:
            self.central_stack.setCurrentIndex(idx)

    def _new_campaign(self):
        self.central_stack.setCurrentIndex(1)

    def _open_campaign(self):
        self.central_stack.setCurrentIndex(1)

    def _toggle_console(self):
        self.console_dock.setVisible(not self.console_dock.isVisible())

    def _show_about(self):
        QMessageBox.about(
            self,
            "About RenodeResilience",
            "<h2>RenodeResilience v1.5</h2>"
            "<p>Automated fault-injection and resilience-testing framework "
            "for embedded firmware on Renode.</p>"
            "<p>27 canonical faults | 3 platforms | RI scoring (0-100)</p>"
            "<p>GitHub: Rohithdgrr/RUDRA-CAPSTONE-PROJECT</p>",
        )

    def _run_campaign(self):
        from src.config.defaults import PLATFORM_REPL_MAP
        from src.config.schemas import CampaignConfig

        # Use faults selected in the editor; fallback to demo 3 if none selected
        selected = self.editor.get_selected_faults()
        if not selected:
            self.console.append_log("WARN", "No faults selected — select at least one fault")
            return

        # Map platform display name to .repl path
        platform_text = self.editor.platform.currentText()
        _plat_map = {
            "STM32F4 Discovery": PLATFORM_REPL_MAP.get(
                "stm32f4", "resources/platforms/stm32f4_discovery.repl"
            ),
            "nRF52840 DK": PLATFORM_REPL_MAP.get("nrf52840", "resources/platforms/nrf52840dk.repl"),
            "HiFive1 RISC-V": PLATFORM_REPL_MAP.get(
                "riscv_hifive1", "resources/platforms/riscv_hifive1.repl"
            ),
        }
        platform_repl = _plat_map.get(platform_text, "resources/platforms/stm32f4_discovery.repl")

        # Build fault list from selection with sensible defaults for all 27 faults
        _default_params = {
            "SF-01": {"value": 25.0, "target": "sysbus.i2c0.sensor0"},
            "SF-02": {"std_dev": 1.0, "target": "sysbus.i2c0.sensor0"},
            "SF-03": {"amplitude": 999, "rate_hz": 10},
            "SF-04": {"rate": 0.1},
            "SF-05": {"offset": 1.0},
            "SF-06": {"drop_rate": 0.2},
            "SF-07": {"jitter_ms": 5},
            "TF-01": {"delay_ms": 100, "target": "control_loop"},
            "TF-02": {"skew_ppm": 100},
            "TF-03": {"irq": "0", "rate_hz": 1000},
            "TF-04": {"timeout_ms": 10},
            "TF-05": {"threads": 2},
            "CF-01": {"loss_rate": 0.3, "bus": "can0"},
            "CF-02": {"delay_ms": 50, "bus": "can0"},
            "CF-03": {"rate_hz": 5000, "bus": "can0"},
            "CF-04": {"ber": 0.01, "bus": "can0"},
            "CF-05": {"bus": "can0"},
            "CF-06": {"bus": "can0", "id": 0x123},
            "MF-01": {"overflow_bytes": 512},
            "MF-02": {"addr": "0x20000000", "size": 64},
            "MF-03": {"addr": "0x08000000", "bit": 3},
            "MF-04": {"addr": "0x20000000", "ecc_bits": 2},
            "PF-01": {"voltage": 2.0, "duration_ms": 100},
            "PF-02": {"glitch_us": 10, "count": 1},
            "PF-03": {"sleep_mode": "stop"},
            "GF-01": {"pin": "0", "mode": "float"},
            "GF-02": {"periph": "adc", "value": 0},
        }
        _default_expected = {
            "SF-01": "detect_stuck_sensor",
            "SF-02": "std_dev_filtered",
            "SF-03": "outlier_detected",
            "SF-04": "drift_compensated",
            "SF-05": "bias_corrected",
            "SF-06": "interpolation_ok",
            "SF-07": "jitter_tolerated",
            "TF-01": "watchdog_reset",
            "TF-02": "clock_resync",
            "TF-03": "irq_throttled",
            "TF-04": "wdg_reset",
            "TF-05": "race_avoided",
            "CF-01": "arq_recovered",
            "CF-02": "deadline_ok",
            "CF-03": "flood_mitigated",
            "CF-04": "crc_ok",
            "CF-05": "bus_recovered",
            "CF-06": "arbitration_ok",
            "MF-01": "stack_ok",
            "MF-02": "heap_ok",
            "MF-03": "ecc_corrected",
            "MF-04": "ecc_handled",
            "PF-01": "bor_handled",
            "PF-02": "glitch_filtered",
            "PF-03": "sleep_ok",
            "GF-01": "pin_safe",
            "GF-02": "adc_ok",
        }
        faults = []
        for fid in selected:
            faults.append(
                {
                    "id": fid,
                    "params": _default_params.get(fid, {}),
                    "expected": _default_expected.get(fid, ""),
                    "timeout_ms": 200 if fid == "TF-01" else 5000,
                }
            )
        # Validate platform REPL exists before launching
        if not Path(platform_repl).exists():
            self.console.append_log("FAIL", f"Platform REPL not found: {platform_repl}")
            self.statusBar().showMessage("Platform not found")
            return

        # Safety cap: config allows 1..27, UI enforces via table
        if len(faults) > 27:
            faults = faults[:27]

        cfg = {
            "name": self.editor.name_edit.text() or "Campaign",
            "firmware": self.editor.firmware_edit.text(),
            "platform": platform_repl,
            "duration": int(self.editor.duration.value()),
            "parallel": int(self.editor.parallel.value()),
            "faults": faults,
        }

        try:
            config = CampaignConfig.model_validate(cfg)
            camp = Campaign(config)
        except Exception as e:
            self.console.append_log("FAIL", f"Failed to create campaign: {e}")
            return

        self.central_stack.setCurrentIndex(2)
        self.runner.clear()
        self._runner_thread = TestRunner(
            camp,
            parallel=cfg["parallel"],
            use_renode=self._use_renode,
            renode_bin=self._renode_bin,
            renode_port=self._renode_port,
        )
        self._runner_thread.progress.connect(self.runner.set_progress)
        self._runner_thread.result.connect(self.runner.add_result)
        self._runner_thread.log.connect(self.console.append_log)
        self._runner_thread.finished_campaign.connect(self._on_finished)
        self._runner_thread.start()
        mode = "renode" if self._use_renode else "simulation"
        self.statusBar().showMessage(f"Renode: Running [{mode}]...")

    def _on_finished(self, result):
        ri = getattr(result, "resilience_index", 0)
        grade = getattr(result, "grade", "?")

        self.ri_gauge.set_value(ri)

        passed = getattr(result, "pass_count", 0)
        total = getattr(result, "total_count", 0)
        self.pass_fail_pie.set_data(passed, total - passed)

        # Radar should reflect all faults, not just failures (otherwise PASS campaigns show empty)
        cat_scores = {}
        for f in getattr(result, "results", []):
            fid = getattr(f, "fault_id", "")
            prefix = fid[:2] if len(fid) >= 2 else ""
            cat_map = {
                "SF": "Sensor",
                "TF": "Timing",
                "CF": "Comm",
                "MF": "Memory",
                "PF": "Power",
                "GF": "GPIO",
            }
            cat = cat_map.get(prefix, "Sensor")
            ri_val = getattr(f, "resilience_index", 0)
            cat_scores.setdefault(cat, []).append(ri_val)

        avg_scores = {c: sum(v) // len(v) for c, v in cat_scores.items() if v}
        self.category_radar.set_scores(avg_scores)

        self.report.show_result(result)
        self.central_stack.setCurrentIndex(3)
        self.statusBar().showMessage(f"Done  |  RI {ri}/100  |  Grade {grade}")

    def _stop_campaign(self):
        if self._runner_thread:
            self._runner_thread.stop()
            self.console.append_log("WARN", "Stop requested by user")
            self.statusBar().showMessage("Renode: stopped")

    def _on_fault_selected(self):
        """Update property panel when fault selection changes."""
        try:
            selected = self.editor.get_selected_faults()
            if selected:
                fid = selected[0]
                self.props_panel.target.setText(fid)
                # Update severity from table
                for i in range(self.editor.fault_table.rowCount()):
                    if self.editor.fault_table.item(i, 1).text() == fid:
                        sev = self.editor.fault_table.item(i, 3).text()
                        self.props_panel.severity.setCurrentText(sev)
                        break
        except Exception:
            pass

    def closeEvent(self, event):  # noqa: N802
        try:
            self.settings.setValue("theme", self._current_theme)
            self.settings.setValue("renode/use_renode", self._use_renode)
            self.settings.setValue("renode/bin", self._renode_bin)
            self.settings.setValue("renode/port", self._renode_port)
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue("windowState", self.saveState())
        except Exception:
            pass
        super().closeEvent(event)

    def _open_settings(self):
        d = SettingsDialog(self)
        # preload current values
        d.use_renode.setChecked(self._use_renode)
        d.renode_path.setText(self._renode_bin)
        d.monitor_port.setText(str(self._renode_port))
        # preload theme
        try:
            d.theme.setCurrentText(self._current_theme.capitalize())
        except Exception:
            pass
        if d.exec():
            self._use_renode = d.use_renode.isChecked()
            self._renode_bin = d.renode_path.text().strip() or "renode"
            try:
                self._renode_port = int(d.monitor_port.text().strip() or "1234")
            except ValueError:
                self._renode_port = 1234
            # Persist
            self.settings.setValue("renode/use_renode", self._use_renode)
            self.settings.setValue("renode/bin", self._renode_bin)
            self.settings.setValue("renode/port", self._renode_port)
            try:
                self.settings.setValue("theme", d.theme.currentText().lower())
                self._set_theme(d.theme.currentText().lower())
            except Exception:
                pass
            self.console.append_log(
                "INFO",
                f"Settings: renode={'on' if self._use_renode else 'off'} bin={self._renode_bin} port={self._renode_port}",
            )
            self.statusBar().showMessage(
                f"Settings saved | Renode {'enabled' if self._use_renode else 'simulation'}"
            )
