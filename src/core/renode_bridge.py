"""RenodeBridge — QProcess/subprocess wrapper for Renode monitor."""
from __future__ import annotations

import subprocess
import tempfile
import time
import socket
from pathlib import Path
from typing import Optional


class RenodeBridge:
    """Launch Renode headless, send monitor commands, read peripherals."""

    def __init__(self, renode_bin: str = "renode", port: int = 1234):
        self.renode_bin = renode_bin
        self.port = port
        self.process: Optional[subprocess.Popen] = None
        self.log_file = None
        self._log_path: Optional[Path] = None

    def start(self, platform_file: Path, firmware_file: Path) -> bool:
        """Launch Renode with platform + firmware. Returns True if monitor ready."""
        # Build monitor script path via temp file (renode monitor reads stdin)
        self.log_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".log", delete=False, encoding="utf-8")
        self._log_path = Path(self.log_file.name)
        # Prepare renode script executed via stdin
        # We launch renode and then send commands via stdin
        try:
            self.process = subprocess.Popen(
                [self.renode_bin, "--disable-xwt", "--port", str(self.port)],
                stdin=subprocess.PIPE,
                stdout=self.log_file,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except FileNotFoundError:
            return False

        # Wait for monitor port
        if not self._wait_for_monitor(timeout=15.0):
            return False

        # Send platform + firmware load
        script = f'include @{platform_file}\n'
        script += f'sysbus LoadELF @{firmware_file}\n'
        script += 'start\n'
        if self.process.stdin:
            self.process.stdin.write(script)
            self.process.stdin.flush()
        return True

    def _wait_for_monitor(self, timeout: float = 15.0) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            # Check process still alive
            if self.process and self.process.poll() is not None:
                return False
            # Try TCP connect
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=0.5):
                    return True
            except OSError:
                time.sleep(0.3)
        return False

    def send_command(self, cmd: str) -> bool:
        if not self.process or not self.process.stdin:
            return False
        try:
            self.process.stdin.write(cmd + "\n")
            self.process.stdin.flush()
            return True
        except BrokenPipeError:
            return False

    def inject_fault(self, fault_id: str, params: dict) -> bool:
        from src.core.fault_injector import build_fault_command
        cmd = build_fault_command(fault_id, params)
        return self.send_command(cmd)

    def read_peripheral(self, path: str) -> str:
        """Send read and return placeholder. Real Renode would respond via monitor."""
        # Use monitor sysbus ReadDoubleWord etc. For now, return simulated value.
        self.send_command(f"sysbus ReadDoubleWord {path}")
        return "0"

    def stop(self, graceful: bool = True) -> bool:
        if self.process:
            try:
                if graceful and self.process.stdin:
                    try:
                        self.process.stdin.write("quit\n")
                        self.process.stdin.flush()
                    except BrokenPipeError:
                        pass
                    try:
                        self.process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                else:
                    self.process.kill()
                    self.process.wait(timeout=5)
            finally:
                self.process = None
        return True

    @property
    def log_path(self) -> Optional[Path]:
        return self._log_path
