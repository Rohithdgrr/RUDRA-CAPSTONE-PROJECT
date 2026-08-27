"""TestRunner — QThread-based parallel runner with stop support."""

from PyQt6.QtCore import QThread, pyqtSignal

from src.core.campaign import Campaign


class TestRunner(QThread):
    progress = pyqtSignal(int, int)
    result = pyqtSignal(object)
    log = pyqtSignal(str, str)
    finished_campaign = pyqtSignal(object)

    def __init__(
        self,
        campaign: Campaign,
        parallel: int = 1,
        use_renode: bool = False,
        renode_bin: str = "renode",
        renode_port: int = 1234,
    ):
        super().__init__()
        self.campaign = campaign
        self.parallel = parallel
        self.use_renode = use_renode
        self.renode_bin = renode_bin
        self.renode_port = renode_port
        self._stop = False

    def run(self):
        self._stop = False
        total = len(self.campaign.config.faults)
        mode = "renode" if self.use_renode else "simulation"
        self.log.emit(
            "INFO", f"Campaign started: {self.campaign.config.name} ({total} faults) [{mode}]"
        )

        def on_prog(cur, tot):
            if self._stop:
                return
            self.progress.emit(cur, tot)

        def on_res(tr):
            if self._stop:
                return
            self.result.emit(tr)
            level = "PASS" if tr.status == "PASS" else "FAIL"
            self.log.emit(level, f"{tr.fault_id} RI {tr.resilience_index} Grade {tr.grade}")

        try:
            stop_check = lambda: self._stop or self.isInterruptionRequested()
            res = self.campaign.run(
                parallel=self.parallel,
                on_progress=on_prog,
                on_result=on_res,
                use_renode=self.use_renode,
                renode_bin=self.renode_bin,
                renode_port=self.renode_port,
                stop_check=stop_check,
            )
        except Exception as e:
            self.log.emit("FAIL", f"Campaign error: {e}")
            return

        if not self._stop:
            self.finished_campaign.emit(res)
            self.log.emit("INFO", f"Campaign finished RI {res.resilience_index} Grade {res.grade}")
        else:
            self.log.emit("WARN", "Campaign stopped by user")

    def stop(self):
        """Request graceful stop — no terminate() (avoids orphaned Renode)."""
        self._stop = True
        self.requestInterruption()
        # Give the worker a chance to exit its poll loops (max 2s), then return.
        # We do not call terminate() — that can corrupt Qt/Python and leak the
        # Renode subprocess (Campaign.run owns its bridge and will stop() it on
        # next iteration / finally block).
        self.wait(2000)
