"""Async workers with QThreadPool."""
from PyQt6.QtCore import QRunnable, pyqtSignal, QObject

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            res = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(res)
        except Exception as e:
            self.signals.error.emit((type(e), e, e.__traceback__))
        finally:
            self.signals.finished.emit()
