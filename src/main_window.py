"""MainWindow — QMainWindow controller per desktop-application.md:541."""
from PyQt6.QtWidgets import QMainWindow, QDockWidget, QStackedWidget, QLabel
from PyQt6.QtCore import Qt
from src.gui.widgets.sidebar import Sidebar
from src.gui.widgets.campaign_editor import CampaignEditor
from src.gui.widgets.test_runner_view import TestRunnerView
from src.gui.widgets.report_viewer import ReportViewer
from src.gui.widgets.comparison_view import ComparisonView
from src.gui.widgets.console_output import ConsoleOutput
from src.gui.widgets.property_panel import PropertyPanel
from src.gui.widgets.dialogs.settings_dialog import SettingsDialog
from src.core.campaign import Campaign
from src.core.test_runner import TestRunner

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RenodeResilience v1.0")
        self.setMinimumSize(1400, 900)
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)

        # screens
        self.welcome = QLabel("Welcome — Recent Projects | Templates: STM32 Sensor, Motor, CAN, Power, Communication")
        self.welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.editor = CampaignEditor()
        self.runner = TestRunnerView()
        self.report = ReportViewer()
        self.compare = ComparisonView()

        for w in [self.welcome, self.editor, self.runner, self.report, self.compare]:
            self.central_stack.addWidget(w)

        # Sidebar dock
        self.sidebar_dock = QDockWidget("Navigation", self)
        self.sidebar = Sidebar()
        self.sidebar_dock.setWidget(self.sidebar)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar_dock)
        self.sidebar.navigate.connect(self._navigate)

        # Properties dock
        self.props_dock = QDockWidget("Properties", self)
        self.props_dock.setWidget(PropertyPanel())
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.props_dock)

        # Console dock bottom
        self.console_dock = QDockWidget("Console", self)
        self.console = ConsoleOutput()
        self.console_dock.setWidget(self.console)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.console_dock)

        self.statusBar().showMessage("Ready | Renode: idle")

        # wiring
        self.editor.runRequested.connect(self._run_campaign)
        self.runner.stop_btn.clicked.connect(self._stop_campaign)
        self._runner_thread = None

        # menu
        m = self.menuBar().addMenu("File")
        m.addAction("Settings", self._open_settings)
        m.addAction("Exit", self.close)

    def _navigate(self, text):
        mapping = {"New":1, "Campaigns":1, "Recent":0, "Templates":0, "Settings":0, "Platforms":0}
        idx = mapping.get(text, 0)
        self.central_stack.setCurrentIndex(idx)

    def _run_campaign(self):
        # Build campaign from editor (simplified demo)
        from pathlib import Path
        import yaml
        cfg = {
            "name": self.editor.name_edit.text(),
            "firmware": "examples/sensor-firmware/build/sensor.elf",
            "platform": "resources/platforms/stm32f4_discovery.repl",
            "duration": int(self.editor.duration.value()),
            "parallel": int(self.editor.parallel.value()),
            "faults": [
                {"id":"SF-01","params":{"value":25.0,"target":"i2c0.sensor0"},"expected":"detect_stuck_sensor","timeout_ms":5000},
                {"id":"SF-03","params":{"amplitude":999},"expected":"outlier_detected","timeout_ms":5000},
                {"id":"TF-01","params":{"delay_ms":100,"target":"control_loop"},"expected":"watchdog_reset","timeout_ms":200},
            ]
        }
        from src.config.schemas import CampaignConfig
        config = CampaignConfig.model_validate(cfg)
        camp = Campaign(config)
        self.central_stack.setCurrentWidget(self.runner)
        self.runner.table.setRowCount(0)
        self._runner_thread = TestRunner(camp, parallel=cfg["parallel"])
        self._runner_thread.progress.connect(self.runner.set_progress)
        self._runner_thread.result.connect(self.runner.add_result)
        self._runner_thread.log.connect(self.console.append_log)
        self._runner_thread.finished_campaign.connect(self._on_finished)
        self._runner_thread.start()
        self.statusBar().showMessage("Renode: Running")

    def _on_finished(self, result):
        self.report.show_result(result)
        self.central_stack.setCurrentWidget(self.report)
        self.statusBar().showMessage(f"Done RI {result.resilience_index}/100 Grade {result.grade}")

    def _stop_campaign(self):
        if self._runner_thread:
            self._runner_thread.stop()
            self.console.append_log("WARN", "Stop requested")
            self.statusBar().showMessage("Renode: stopped")

    def _open_settings(self):
        d = SettingsDialog(self); d.exec()
