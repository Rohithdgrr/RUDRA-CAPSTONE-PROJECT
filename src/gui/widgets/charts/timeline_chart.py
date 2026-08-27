from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

try:
    import pyqtgraph as pg

    HAS_PG = True
except ImportError:
    HAS_PG = False


class TimelineChart(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        if HAS_PG:
            self.plot = pg.PlotWidget(title="Detection Latency (ms)")
            self.plot.setBackground("#2A2A3C")
            self.plot.showGrid(x=True, y=True)
            lay.addWidget(self.plot)
        else:
            lay.addWidget(QLabel("Timeline Chart — install PyQtGraph for live plot"))

    def set_data(self, results):
        if not HAS_PG or not results:
            return
        xs = list(range(len(results)))
        ys = [r.latency_ms or 0 for r in results]
        self.plot.clear()
        self.plot.plot(xs, ys, pen=pg.mkPen("#3498DB", width=2), symbol="o", symbolBrush="#4CAF50")
        self.plot.setLabel("bottom", "Fault Index")
        self.plot.setLabel("left", "Latency ms")
