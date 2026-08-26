"""Report generator — HTML/PDF/JSON/JUnit."""
from pathlib import Path
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "resources" / "templates"

def _env():
    # Simple inline template if file missing
    return Environment(autoescape=select_autoescape())

def generate_html(result, path):
    path = Path(path)
    html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'><title>{result.campaign_name}</title>
<style>body{{font-family:sans-serif;background:#1E1E2F;color:#E0E0E0;padding:20px}} .card{{background:#2A2A3C;padding:16px;border-radius:8px}}</style></head>
<body><h1>{result.campaign_name}</h1><div class=card>RI: {result.resilience_index}/100 Grade: {result.grade} Pass {result.pass_count}/{result.total_count}</div>
<table border=1 cellpadding=6 style='margin-top:16px'><tr><th>ID</th><th>Status</th><th>RI</th></tr>
{"".join(f"<tr><td>{r.fault_id}</td><td>{r.status}</td><td>{r.resilience_index}</td></tr>" for r in result.results)}
</table></body></html>"""
    path.write_text(html, encoding="utf-8")

def generate_pdf(result, path):
    # Try HTML -> PDF via WeasyPrint, fallback to HTML renamed
    try:
        from weasyprint import HTML
        html_path = Path(path).with_suffix(".html")
        generate_html(result, html_path)
        HTML(filename=str(html_path)).write_pdf(str(path))
    except Exception:
        generate_html(result, Path(path).with_suffix(".html"))

def generate_junit(result, path):
    import xml.etree.ElementTree as ET
    suite = ET.Element("testsuite", name=result.campaign_name, tests=str(result.total_count), failures=str(result.fail_count))
    for r in result.results:
        tc = ET.SubElement(suite, "testcase", classname="fault", name=r.fault_id, time=str((r.latency_ms or 0)/1000))
        if r.status == "FAIL":
            ET.SubElement(tc, "failure", message=f"{r.fault_id} RI {r.resilience_index}")
    tree = ET.ElementTree(suite)
    tree.write(path, encoding="utf-8", xml_declaration=True)
