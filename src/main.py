"""Entry point — python -m src.main"""
import sys
from src.app import create_app
from src.main_window import MainWindow

def main():
    # headless flag
    if "--headless" in sys.argv or "--help" in sys.argv:
        print("RenodeResilience v1.0.0 — use renode-resilience CLI")
        return
    app = create_app()
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
