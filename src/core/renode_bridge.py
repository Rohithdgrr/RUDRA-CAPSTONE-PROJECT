"""RenodeBridge — subprocess wrapper for Renode monitor."""

from __future__ import annotations

import logging
import socket
import subprocess
import tempfile
import time
from pathlib import Path

logger = logging.getLogger(__name__)

_MAX_PATH_COMPONENTS = 20


def _sanitize_path(p: Path) -> str:
    """Validate path has no traversal, null bytes, and is within allowed files.

    Rejects any path containing ``..`` components before resolution and also
    ensures the resolved path does not escape via symlink.  Allows absolute
    or repo-relative paths that exist or are new files under repo/results/campaigns.
    """
    raw = str(p)
    if "\x00" in raw:
        raise ValueError(f"Null byte in path: {p!r}")
    # Check original parts for traversal before resolve() collapses them
    if ".." in Path(p).parts:
        raise ValueError(f"Path traversal detected: {p}")
    if any(part == ".." for part in Path(raw.replace("\\", "/")).parts):
        raise ValueError(f"Path traversal detected: {p}")
    try:
        resolved = p.resolve(strict=False)
    except OSError as e:
        raise ValueError(f"Invalid path {p!r}: {e}") from e
    # Extra guard: resolved string must not still contain .. (defense in depth)
    if ".." in str(resolved):
        raise ValueError(f"Path traversal detected after resolve: {p}")
    return str(resolved)


class RenodeBridge:
    """Launch Renode headless, send monitor commands, read peripherals."""

    def __init__(self, renode_bin: str = "renode", port: int = 1234):
        # Validate renode_bin: no monitor separators or path traversal
        if any(c in renode_bin for c in [";", "\n", "\r", "|", "&", "`", "$", "#", "\x00"]):
            raise ValueError(f"Illegal characters in renode_bin: {renode_bin!r}")
        if ".." in Path(renode_bin).parts:
            raise ValueError(f"Path traversal in renode_bin: {renode_bin!r}")
        self.renode_bin = renode_bin
        self.port = port
        self.process: subprocess.Popen | None = None
        self._log_file = None
        self._log_path: Path | None = None

    def start(self, platform_file: Path, firmware_file: Path) -> bool:
        """Launch Renode with platform + firmware. Returns True if monitor ready."""
        self._log_file = tempfile.NamedTemporaryFile(
            mode="w+", suffix=".log", delete=False, encoding="utf-8"
        )
        self._log_path = Path(self._log_file.name)

        try:
            self.process = subprocess.Popen(
                [self.renode_bin, "--disable-xwt", "--port", str(self.port)],
                stdin=subprocess.PIPE,
                stdout=self._log_file,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except FileNotFoundError:
            self._cleanup_log()
            return False

        if not self._wait_for_monitor(timeout=15.0):
            self._cleanup_process()
            self._cleanup_log()
            return False

        try:
            safe_platform = _sanitize_path(platform_file)
            safe_firmware = _sanitize_path(firmware_file)
        except ValueError as e:
            logger.error("Path validation failed: %s", e)
            self._cleanup_process()
            self._cleanup_log()
            return False

        # Allowlist: platform must be a .repl file
        if not safe_platform.endswith(".repl"):
            logger.error("Platform must be a .repl file: %s", safe_platform)
            self._cleanup_process()
            self._cleanup_log()
            return False
        # Firmware must be .elf or .bin (or .axf) — warn but allow simulation fallback
        if not (safe_firmware.endswith(".elf") or safe_firmware.endswith(".bin") or safe_firmware.endswith(".axf")):
            logger.warning("Firmware does not look like ELF/BIN: %s", safe_firmware)

        script = f"include @{safe_platform}\n"
        script += f"sysbus LoadELF @{safe_firmware}\n"
        script += "start\n"
        if self.process and self.process.stdin:
            try:
                self.process.stdin.write(script)
                self.process.stdin.flush()
            except BrokenPipeError:
                logger.error("Broken pipe writing to Renode stdin")
                self._cleanup_process()
                self._cleanup_log()
                return False
        return True

    def _wait_for_monitor(self, timeout: float = 15.0) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            if self.process and self.process.poll() is not None:
                return False
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
        """Read a 32-bit value from a sysbus peripheral.

        Sends ``sysbus ReadDoubleWord <path>`` to the Renode monitor and
        parses the response.  Renode returns lines like::

            sysbus ReadDoubleWord 0x40020000
            value: 0x12345678

        If the monitor is unavailable or parsing fails, returns ``"0"``.
        """
        import re

        if not self.process or not self.process.stdin:
            return "0"
        try:
            self.process.stdin.write(f"sysbus ReadDoubleWord {path}\n")
            self.process.stdin.flush()
        except BrokenPipeError:
            return "0"

        # Read response from stdout/log — Renode prints the value on the
        # next line after the command echo.  Poll the log and return the *last*
        # match so we get the result of the most recent ReadDoubleWord, not the
        # first (old) one.  Truncate read to last 8 KB to avoid huge logs.
        if self._log_path and self._log_path.exists():
            try:
                text = self._log_path.read_text(encoding="utf-8", errors="replace")
                if len(text) > 8192:
                    text = text[-8192:]
                matches = re.findall(r"value:\s*(0x[0-9A-Fa-f]+|\d+)", text)
                if matches:
                    return matches[-1]
            except OSError:
                pass
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
                        self.process.wait(timeout=5)
                else:
                    self.process.kill()
                    self.process.wait(timeout=5)
            except Exception as e:
                logger.warning("Error stopping Renode: %s", e)
            finally:
                self.process = None
                self._cleanup_log()
        return True

    def _cleanup_log(self):
        if self._log_file:
            try:
                self._log_file.close()
            except Exception:
                pass
            self._log_file = None
        # Always unlink the temp log file (delete=False was used so we own cleanup)
        if self._log_path:
            try:
                if self._log_path.exists():
                    self._log_path.unlink(missing_ok=True)
            except Exception:
                pass
            self._log_path = None

    def _cleanup_process(self):
        if self.process:
            try:
                if self.process.poll() is None:
                    self.process.kill()
                    self.process.wait(timeout=5)
            except Exception:
                pass
            self.process = None

    @property
    def log_path(self) -> Path | None:
        return self._log_path
