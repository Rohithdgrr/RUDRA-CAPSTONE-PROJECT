"""Default settings & constants."""

import os
from pathlib import Path

DEFAULT_WEIGHTS = {"detection": 0.4, "recovery": 0.3, "safety": 0.3}

# Optional Bearer token for API auth (env var, not YAML — see docs/16-SECURITY)
# Set RENODE_TOKEN or RENODE_RESILIENCE_TOKEN in env or ~/.config/renode-resilience/token
API_TOKEN = os.getenv("RENODE_TOKEN") or os.getenv("RENODE_RESILIENCE_TOKEN") or None
# If a token file exists at ~/.config/renode-resilience/token, use it as fallback
try:
    _token_file = Path.home() / ".config" / "renode-resilience" / "token"
    if not API_TOKEN and _token_file.exists():
        API_TOKEN = _token_file.read_text(encoding="utf-8").strip() or None
except Exception:
    pass
DEFAULT_THRESHOLDS = {"grade_a": 90, "grade_b": 70, "grade_c": 50, "grade_d": 30}

SUPPORTED_PLATFORMS = ["stm32f4", "nrf52840", "riscv_hifive1"]
PLATFORM_REPL_MAP = {
    "stm32f4": "resources/platforms/stm32f4_discovery.repl",
    "nrf52840": "resources/platforms/nrf52840dk.repl",
    "riscv_hifive1": "resources/platforms/riscv_hifive1.repl",
}

RENODE_DEFAULT_PORT = 1234
RENODE_MONITOR_TIMEOUT = 15.0
RENODE_STOP_TIMEOUT = 10.0

LOG_RETENTION_DAYS = 30
CONSOLE_MAX_LINES = 10_000
RESULTS_DIR = Path("results")
CAMPAIGNS_DIR = Path("campaigns")

GRADE_COLORS = {
    "A": "#2ECC71",
    "B": "#3498DB",
    "C": "#F1C40F",
    "D": "#E67E22",
    "F": "#E74C3C",
}
STATUS_COLORS = {
    "PASS": "#4CAF50",
    "FAIL": "#F44336",
    "WARNING": "#FF9800",
    "INFO": "#2196F3",
}
