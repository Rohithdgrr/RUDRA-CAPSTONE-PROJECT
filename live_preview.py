import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.app import create_app
from src.main_window import MainWindow

def main():
    app = create_app(sys.argv)
    print(f"platform: {app.platformName()} fonts: {len(app.font().family())}")
    w = MainWindow()
    w.show()
    # auto-run demo
    w._run_campaign()
    def capture():
        # ensure runner finished (wait 1s)
        pix = w.grab()
        out = Path("live_preview.png")
        pix.save(str(out))
        print(f"saved {out.resolve()} {pix.width()}x{pix.height()} dpr {pix.devicePixelRatio()}")
        # switch to report if available
        try:
            w.central_stack.setCurrentWidget(w.report)
            app.processEvents()
            pix2 = w.report.grab()
            p2 = Path("live_report.png")
            pix2.save(str(p2))
            print(f"saved {p2} {pix2.width()}x{pix2.height()}")
        except Exception as e:
            print(f"report grab fail: {e}")
        app.quit()
    QTimer.singleShot(2500, capture)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
