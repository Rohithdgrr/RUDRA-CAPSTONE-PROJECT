"""TestRunner — QThread-based parallel runner."""
from PyQt6.QtCore import QThread, pyqtSignal
from src.core.campaign import Campaign

class TestRunner(QThread):
    progress = pyqtSignal(int, int)  # current, total
    result = pyqtSignal(object)  # TestResult
    log = pyqtSignal(str, str)  # level, message
    finished_campaign = pyqtSignal(object)  # CampaignResult

    def __init__(self, campaign: Campaign, parallel: int = 1):
        super().__init__()
        self.campaign = campaign
        self.parallel = parallel
        self._stop = False

    def run(self):
        total = len(self.campaign.config.faults)
        self.log.emit("INFO", f"Campaign started: {self.campaign.config.name} ({total} faults)")
        # Simple sequential via Campaign.run with callbacks
        def on_prog(cur, tot):
            self.progress.emit(cur, tot)
        def on_res(tr):
            self.result.emit(tr)
            self.log.emit("PASS" if tr.status=="PASS" else "FAIL", f"{tr.fault_id} RI {tr.resilience_index} Grade {tr.grade}")
        res = self.campaign.run(parallel=self.parallel, on_progress=on_prog, on_result=on_res)
        self.finished_campaign.emit(res)
        self.log.emit("INFO", f"Campaign finished RI {res.resilience_index} Grade {res.grade}")

    def stop(self):
        self._stop = True
