"""Entry point — python -m src.main or python src/main.py"""

import pathlib
import sys

# Allow `python src/main.py` direct execution (adds repo root to path)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

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
