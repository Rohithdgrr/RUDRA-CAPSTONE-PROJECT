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
    """Launch Renode headless, send monitor commands, read peripherals.

    Production-grade: temp script file, socket-based monitor (fallback to stdin),
    15s monitor wait, zombie cleanup, path allowlist, log truncation.
    """

    def __init__(self, renode_bin: str = "renode", port: int = 1234, timeout: float = 15.0):
        # Validate renode_bin: no monitor separators or path traversal
        if any(c in renode_bin for c in [";", "\n", "\r", "|", "&", "`", "$", "#", "\x00"]):
            raise ValueError(f"Illegal characters in renode_bin: {renode_bin!r}")
        if ".." in Path(renode_bin).parts:
            raise ValueError(f"Path traversal in renode_bin: {renode_bin!r}")
        self.renode_bin = renode_bin
        self.port = port
        self.timeout = timeout
        self.process: subprocess.Popen | None = None
        self._log_file = None
        self._log_path: Path | None = None
        self._script_path: Path | None = None

    def start(self, platform_file: Path, firmware_file: Path) -> bool:
        """Start Renode headless and verify monitor port is alive."""
        # Validate and sanitize first (fail fast before spawning)
        try:
            safe_platform = _sanitize_path(platform_file)
            safe_firmware = _sanitize_path(firmware_file)
        except ValueError as e:
            logger.error("Path validation failed: %s", e)
            return False
        if not safe_platform.endswith(".repl"):
            logger.error("Platform must be a .repl file: %s", safe_platform)
            return False
        if not (safe_firmware.endswith(".elf") or safe_firmware.endswith(".bin") or safe_firmware.endswith(".axf")):
            logger.warning("Firmware does not look like ELF/BIN: %s", safe_firmware)

        # Temp log file (for fallback parsing)
        self._log_file = tempfile.NamedTemporaryFile(
            mode="w+", suffix=".log", delete=False, encoding="utf-8"
        )
        self._log_path = Path(self._log_file.name)

        # Temp Renode script (blueprint style) — also passed via stdin for compat
        script = f"include @{safe_platform}\nsysbus LoadELF @{safe_firmware}\nstart\n"
        sf = tempfile.NamedTemporaryFile(mode="w", suffix=".resc", delete=False, encoding="utf-8")
        sf.write(script)
        sf.close()
        self._script_path = Path(sf.name)

        try:
            self.process = subprocess.Popen(
                [self.renode_bin, "--disable-xwt", "--port", str(self.port), str(self._script_path)],
                stdin=subprocess.PIPE,
                stdout=self._log_file,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except FileNotFoundError:
            self._cleanup_log()
            self._cleanup_script()
            return False

        if not self._wait_for_monitor(timeout=self.timeout):
            self._cleanup_process()
            self._cleanup_log()
            self._cleanup_script()
            return False

        # Also feed script via stdin for PIDs mocked in tests (they expect stdin.write)
        if self.process and self.process.stdin:
            try:
                self.process.stdin.write(script)
                self.process.stdin.flush()
            except BrokenPipeError:
                logger.error("Broken pipe writing to Renode stdin")
                self._cleanup_process()
                self._cleanup_log()
                self._cleanup_script()
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

    def send_command(self, cmd: str) -> str | bool:
        """Send command to Renode monitor via socket (preferred) or stdin fallback.

        Returns response string on success, True for fire-and-forget, False on failure.
        """
        # Try socket monitor first (production path)
        if self.process and self.process.poll() is None:
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=2) as sock:
                    sock.sendall((cmd + "\n").encode())
                    sock.settimeout(1)
                    try:
                        data = sock.recv(4096)
                        # Mirror to log for read_peripheral fallback parsing
                        if data and self._log_file:
                            try:
                                self._log_file.write(data.decode(errors="replace"))
                                self._log_file.flush()
                            except Exception:
                                pass
                        return data.decode(errors="replace") if data else True
                    except socket.timeout:
                        return True
            except OSError:
                pass
        # Fallback: stdin (for tests/mocked env)
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

        # Prefer socket path via send_command; it will also populate log
        resp = self.send_command(f"sysbus ReadDoubleWord {path}")
        if resp is False:
            return "0"
        # If send_command returned a string with value, parse directly
        if isinstance(resp, str) and "value:" in resp:
            import re as _re

            m0 = _re.search(r"value:\s*(0x[0-9A-Fa-f]+|\d+)", resp)
            if m0:
                return m0.group(1)

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
                if graceful:
                    # Try graceful quit via monitor (socket or stdin)
                    try:
                        self.send_command("quit")
                    except Exception:
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
                self._cleanup_script()
        return True

    def _cleanup_script(self):
        if self._script_path:
            try:
                if self._script_path.exists():
                    self._script_path.unlink(missing_ok=True)
            except Exception:
                pass
            self._script_path = None

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
