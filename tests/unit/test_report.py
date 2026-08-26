from pathlib import Path
from src.core.campaign import Campaign

def test_report_html_and_junit(tmp_path):
    c = Campaign.from_yaml("campaigns/sensor_suite.yaml")
    r = c.run()
    html = tmp_path / "out.html"
    r.to_html(html)
    assert html.exists()
    txt = html.read_text(encoding="utf-8")
    assert "RenodeResilience Report" in txt
    assert f"Grade {r.grade}" in txt
    junit = tmp_path / "junit.xml"
    r.to_junit(junit)
    assert junit.exists()
    assert "<testsuite" in junit.read_text(encoding="utf-8")

def test_comparison(tmp_path):
    c = Campaign.from_yaml("campaigns/sensor_suite.yaml")
    r1 = c.run()
    r2 = c.run()
    cmp = r1.compare(r2)
    assert cmp.delta_ri == 0
    out = tmp_path / "cmp.html"
    cmp.to_html(out)
    assert out.exists()
