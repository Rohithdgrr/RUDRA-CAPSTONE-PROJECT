#!/usr/bin/env python3
"""Capture 5 screenshots as required by 10/10 checklist."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.app import create_app
from src.main_window import MainWindow

OUT = Path("docs/screenshots")
OUT.mkdir(parents=True, exist_ok=True)

def capture(w, name):
    pix = w.grab()
    p = OUT / f"{name}.png"
    pix.save(str(p))
    print(f"[OK] {p} {pix.width()}x{pix.height()}")

def main():
    app = create_app(sys.argv)
    w = MainWindow()
    w.show()

    # Ensure a demo campaign is pre-filled and run
    QTimer.singleShot(500, lambda: w._run_campaign())

    def seq():
        # 0: welcome
        w.central_stack.setCurrentIndex(0)
        app.processEvents()
        capture(w, "01-welcome")
        # 1: campaign designer
        w.central_stack.setCurrentIndex(1)
        app.processEvents()
        capture(w, "02-campaign-designer")
        # 2: runner (may still be running, but capture)
        w.central_stack.setCurrentIndex(2)
        app.processEvents()
        capture(w, "03-test-runner")
        # 3: report
        w.central_stack.setCurrentIndex(3)
        app.processEvents()
        capture(w, "04-report-viewer")
        # 4: comparison (create dummy comparison)
        try:
            from src.core.result_aggregator import CampaignResult, TestResult
            cr1 = CampaignResult("Baseline", [TestResult("SF-01","FAIL",False,False,False,0,None,30,"F","")], 30, "F")
            cr2 = CampaignResult("Optimized", [TestResult("SF-01","PASS",True,True,True,10,5,95,"A","")], 95, "A")
            # ComparisonView expects two lists
            w.compare.show_comparison(cr1.results, cr2.results)
        except Exception as e:
            print(f"[WARN] comparison dummy failed: {e}")
        w.central_stack.setCurrentIndex(4)
        app.processEvents()
        capture(w, "05-comparison")
        # also full window
        capture(w, "00-full-window")
        print(f"[DONE] screenshots in {OUT.resolve()}")
        app.quit()

    QTimer.singleShot(3500, seq)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
