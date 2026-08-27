#!/usr/bin/env python3
"""RUDRA Demo — Run full pipeline and capture screenshots.

Usage:
    python demo/run_demo.py          # Run with headless screenshots
    python demo/run_demo.py --gui    # Launch live PyQt6 window

Requires: PyQt6, pillow (for screenshot capture)
"""
import sys, os, json, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

SCREENSHOTS = ROOT / "demo" / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)


def capture_qt_screenshot(widget, filename):
    """Save a QPixmap screenshot of a widget."""
    try:
        from PyQt6.QtCore import QTimer
        pixmap = widget.grab()
        pixmap.save(str(SCREENSHOTS / filename))
        print(f"  [screenshot] {filename}")
        return True
    except Exception as e:
        print(f"  [skip] {filename}: {e}")
        return False


def run_campaign_demo():
    """Run a campaign and save JSON output as proof."""
    print("=== RUDRA Demo: Full Campaign Pipeline ===\n")

    # Step 1: Run campaign via Python API
    print("1. Running 3-fault sensor suite campaign...")
    from src.core.campaign import Campaign
    from src.config.schemas import CampaignConfig

    cfg = CampaignConfig.model_validate({
        "name": "Demo Campaign",
        "firmware": "firmware/demo.elf",
        "platform": "stm32f4",
        "duration": 30,
        "parallel": 1,
        "faults": [
            {"id": "SF-01", "params": {"path": "0x40020000"}, "expected": "", "timeout_ms": 5000},
            {"id": "SF-03", "params": {"path": "0x40020000", "mask": "0xFF"}, "expected": "", "timeout_ms": 5000},
            {"id": "TF-01", "params": {"path": "0x40020000", "value": "0xDEADBEEF"}, "expected": "", "timeout_ms": 5000},
        ]
    })

    result = campaign_run(cfg)
    print(f"   RI: {result['resilience_index']}/100  Grade: {result['grade']}")
    print(f"   Tests: {len(result['results'])} faults executed")

    # Save JSON as proof
    out = SCREENSHOTS / "demo_result.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"   Saved: {out}")

    # Step 2: Generate HTML report
    print("\n2. Generating HTML report...")
    from src.core.result_aggregator import CampaignResult, TestResult
    cr = CampaignResult(
        campaign_name=result["campaign"],
        resilience_index=result["resilience_index"],
        grade=result["grade"],
        results=[TestResult(**{k: v for k, v in x.items() if k in TestResult.__dataclass_fields__}) for x in result["results"]],
    )
    html_path = SCREENSHOTS / "demo_report.html"
    cr.to_html(html_path)
    print(f"   Saved: {html_path}")

    # Step 3: CLI-style output
    print("\n3. Fault breakdown:")
    for r in result["results"]:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"   [{status}] {r['fault_id']} — RI: {r['ri_score']:.0f} — {r['diagnosis'][:60]}")

    print(f"\n=== Demo Complete ===")
    print(f"   Screenshots: {SCREENSHOTS}")
    return result


def campaign_run(cfg):
    """Run a campaign and return dict result."""
    from src.core.campaign import Campaign
    camp = Campaign(cfg)
    result_obj = camp.run(parallel=1)
    return result_obj.to_dict()


def run_gui_demo():
    """Launch the actual PyQt6 GUI."""
    print("Launching RUDRA GUI...")
    from src.main import main
    main()


if __name__ == "__main__":
    if "--gui" in sys.argv:
        run_gui_demo()
    else:
        run_campaign_demo()
