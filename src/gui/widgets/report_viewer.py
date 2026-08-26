"""Report viewer — HTML via QTextBrowser fallback if QWebEngine not installed."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTextBrowser

class ReportViewer(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        self.summary = QLabel("No report loaded")
        lay.addWidget(self.summary)
        self.browser = QTextBrowser()
        lay.addWidget(self.browser)
        btns = QHBoxLayout()
        for txt in ["Export PDF","Export HTML","Export JSON","Export JUnit"]:
            btns.addWidget(QPushButton(txt))
        lay.addLayout(btns)

    def show_result(self, result):
        self.summary.setText(f"Campaign: {result.campaign_name}  RI: {result.resilience_index}/100 Grade: {result.grade} Pass {result.pass_count}/{result.total_count}")
        html = "<h3>Critical Findings</h3><ul>"
        for f in result.failures:
            d = f.diagnose()
            html += f"<li><b>{f.fault_id}</b>: {d.root_cause}<br/><i>→ {', '.join(d.recommendations)}</i></li>"
        html += "</ul>"
        self.browser.setHtml(html)
