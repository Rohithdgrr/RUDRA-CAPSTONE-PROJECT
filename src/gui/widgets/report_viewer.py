"""Report viewer — polished HTML report with icons on export buttons."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from src.gui.utils.icons import AppIcons


class ReportViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # ── Header with export buttons ────────────────────────
        header_row = QHBoxLayout()
        title = QLabel("Campaign Report")
        title.setObjectName("titleLabel")
        header_row.addWidget(title)
        header_row.addStretch()

        for txt, icon in [
            ("PDF", AppIcons.pdf("#D4D4D8")),
            ("HTML", AppIcons.json("#D4D4D8")),
            ("JSON", AppIcons.json("#D4D4D8")),
            ("JUnit", AppIcons.report("#D4D4D8")),
        ]:
            btn = QPushButton(icon, f" Export {txt}")
            btn.setObjectName("exportBtn")
            btn.setFixedHeight(34)
            header_row.addWidget(btn)
        root.addLayout(header_row)

        # ── Summary Banner ────────────────────────────────────
        self.banner = QFrame()
        self.banner.setObjectName("summaryCard")
        self.banner.setFixedHeight(80)
        banner_lay = QHBoxLayout(self.banner)
        banner_lay.setContentsMargins(20, 12, 20, 12)

        self.banner_ri = QLabel("--")
        self.banner_ri.setStyleSheet("font-size: 36px; font-weight: 800; color: #3B82F6;")
        self.banner_ri.setFixedWidth(120)
        banner_lay.addWidget(self.banner_ri)

        self.banner_grade = QLabel("--")
        self.banner_grade.setStyleSheet("font-size: 28px; font-weight: 800; color: #A1A1AA;")
        self.banner_grade.setFixedWidth(60)
        banner_lay.addWidget(self.banner_grade)

        info_lay = QVBoxLayout()
        self.banner_name = QLabel("No campaign loaded")
        self.banner_name.setStyleSheet("font-size: 14px; font-weight: 600; color: #F4F4F5;")
        info_lay.addWidget(self.banner_name)
        self.banner_stats = QLabel("Pass: 0/0  |  Fail: 0/0")
        self.banner_stats.setStyleSheet("color: #71717A; font-size: 12px;")
        info_lay.addWidget(self.banner_stats)
        banner_lay.addLayout(info_lay)
        banner_lay.addStretch()
        root.addWidget(self.banner)

        # ── Content ───────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Vertical)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        splitter.addWidget(self.browser)

        findings_frame = QFrame()
        findings_frame.setObjectName("summaryCard")
        findings_lay = QVBoxLayout(findings_frame)
        findings_lay.setContentsMargins(16, 12, 16, 12)

        findings_title = QLabel("Critical Findings & Recommendations")
        findings_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #F4F4F5;")
        findings_lay.addWidget(findings_title)

        self.findings_browser = QTextBrowser()
        self.findings_browser.setMaximumHeight(250)
        findings_lay.addWidget(self.findings_browser)

        splitter.addWidget(findings_frame)
        splitter.setSizes([500, 250])
        root.addWidget(splitter)

    def show_result(self, result):
        ri = getattr(result, "resilience_index", 0)
        grade = getattr(result, "grade", "?")
        name = getattr(result, "campaign_name", "Unknown")
        passed = getattr(result, "pass_count", 0)
        total = getattr(result, "total_count", 0)
        failed = total - passed

        gc = {"A": "#10B981", "B": "#3B82F6", "C": "#F59E0B", "D": "#F97316", "F": "#EF4444"}.get(
            grade, "#A1A1AA"
        )

        self.banner_ri.setText(f"{ri}/100")
        self.banner_ri.setStyleSheet(f"font-size: 36px; font-weight: 800; color: {gc};")
        self.banner_grade.setText(grade)
        self.banner_grade.setStyleSheet(f"font-size: 28px; font-weight: 800; color: {gc};")
        self.banner_name.setText(name)
        self.banner_stats.setText(
            f"Pass: {passed}/{total}  |  Fail: {failed}/{total}  |  Grade: {grade}"
        )

        self.browser.setHtml(f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: #D4D4D8;">
        <h2 style="color: #F4F4F5;">{name}</h2>
        <table style="width: 100%; border-collapse: collapse; margin: 12px 0;">
        <tr>
            <td style="padding: 8px; background: #1C1C32; border-radius: 6px; text-align: center;">
                <div style="font-size: 28px; font-weight: 800; color: {gc};">{ri}/100</div>
                <div style="color: #71717A; font-size: 11px;">RESILIENCE INDEX</div>
            </td>
            <td style="padding: 8px; background: #1C1C32; border-radius: 6px; text-align: center;">
                <div style="font-size: 28px; font-weight: 800; color: {gc};">{grade}</div>
                <div style="color: #71717A; font-size: 11px;">GRADE</div>
            </td>
            <td style="padding: 8px; background: #1C1C32; border-radius: 6px; text-align: center;">
                <div style="font-size: 28px; font-weight: 800; color: #10B981;">{passed}</div>
                <div style="color: #71717A; font-size: 11px;">PASSED</div>
            </td>
            <td style="padding: 8px; background: #1C1C32; border-radius: 6px; text-align: center;">
                <div style="font-size: 28px; font-weight: 800; color: #EF4444;">{failed}</div>
                <div style="color: #71717A; font-size: 11px;">FAILED</div>
            </td>
        </tr></table></div>""")

        # Color map for severity badge
        sev_col = {"CRITICAL": "#EF4444", "WARNING": "#F59E0B", "INFO": "#10B981"}
        cat_col = {
            "sensor_filter": "#3B82F6",
            "sensor_calibration": "#06B6D4",
            "timing": "#8B5CF6",
            "concurrency": "#EC4899",
            "communication": "#F97316",
            "memory": "#EF4444",
            "power": "#EAB308",
            "gpio": "#10B981",
            "generic": "#6B7280",
        }
        findings_html = "<ul style='list-style: none; padding: 0;'>"
        for f in getattr(result, "failures", []):
            fid = getattr(f, "fault_id", "?")
            d = f.diagnose() if hasattr(f, "diagnose") else None
            if d:
                rc = getattr(d, "root_cause", "Unknown")
                recs = getattr(d, "recommendations", [])
                sev = getattr(d, "severity", "WARNING")
                cat = getattr(d, "category", "generic")
                iso = getattr(d, "iso_mapping", "") or ""
                mode = getattr(d, "failure_mode", "") or ""
                latency = f"{d.latency_ms} ms" if getattr(d, "latency_ms", None) is not None else "-"
                sev_bg = sev_col.get(sev, "#71717A")
                cat_bg = cat_col.get(cat, "#71717A")
                recs_html = "".join(f"<li style='margin:2px 0'>{r}</li>" for r in recs[:3])
                findings_html += (
                    f"<li style='margin: 10px 0; padding: 10px 12px; background: #1C1C32; "
                    f"border-radius: 6px; border-left: 3px solid {sev_bg};'>"
                    f"<div style='display:flex; align-items:center; gap:6px;'>"
                    f"<b style='color: #F4F4F5;'>{fid}</b>"
                    f"<span style='background:{cat_bg}; color:#fff; padding:2px 6px; border-radius:4px; font-size:10px'>{cat}</span>"
                    f"<span style='background:{sev_bg}; color:#fff; padding:2px 6px; border-radius:4px; font-size:10px'>{sev}</span>"
                    f"<span style='color:#A1A1AA; font-size:10px'>{mode} · latency {latency}</span>"
                    f"</div>"
                    f"<div style='color:#F4F4F5; font-size:12px; margin-top:6px; font-weight:600'>{rc}</div>"
                    f"<div style='color:#60A5FA; font-size:10px; font-family:Consolas,monospace'>{iso}</div>"
                    f"<ol style='color:#9AA0A6; font-size:11px; margin:6px 0 0 16px; line-height:1.4'>{recs_html}</ol>"
                    f"</li>"
                )
            else:
                findings_html += (
                    f"<li style='margin: 4px 0; color: #EF4444;'><b>{fid}</b>: Failed</li>"
                )
        findings_html += "</ul>"
        if not getattr(result, "failures", []):
            findings_html = (
                "<p style='color: #10B981; font-size: 14px; padding: 20px;'>All faults passed!</p>"
            )
        self.findings_browser.setHtml(findings_html)
