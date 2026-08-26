# 02 — Installation

> **Prerequisites:** Python 3.11+, Renode 1.15+ (tested 1.16.1, `renode-docker/Dockerfile:8`), Qt 6.6+, 4GB RAM (8GB rec.), 2GB disk. Optional: `pyrenode3` for typed `RenodeBridge.read_peripheral()` (`pyrenode3/README.md:15`).

## 1. Clone & Venv

```bash
git clone https://github.com/user/renode-resilience.git
cd renode-resilience

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
# or
pip install -e .
```

Verify:
```bash
python --version  # 3.11+
renode --version  # 1.15+ (1.16.1 via Docker verified, `renode/README.md:36`)
python -m src.main --help
renode-resilience --help  # Typer CLI
python -c "import pyrenode3; print(pyrenode3.__about__)"  # optional, `pyrenode3/pyproject.toml:6`
```

## 2. Renode Install (Per-OS)

### Windows
1. Install Visual C++ Redistributable.
2. Download Renode 1.15+ portable zip from renode.io → unzip to `C:\Renode`.
3. Add `C:\Renode` to `PATH`.
4. `renode --disable-xwt --port 1234` should open monitor.

### macOS
```bash
brew install renode
# may need
xcode-select --install
renode --version
```

### Linux (Debian/Ubuntu)
```bash
sudo apt update && sudo apt install renode
chmod +x /usr/bin/renode
renode --version
```

### Script Alternative
```bash
python scripts/install_renode.py  # auto-detects OS, downloads pinned version
```

## 3. PyQt6 & Qt + Optional pyrenode3

- `pip install PyQt6==6.6.* PyQtGraph==0.13.* pandas numpy pydantic PyYAML Jinja2 WeasyPrint scikit-learn FastAPI Typer`
- Optional (typed Renode access, `adr/002` hybrid): `pip install 'pyrenode3[all] @ git+https://github.com/antmicro/pyrenode3.git'` then `export PYRENODE_PATH=/opt/renode` or installed Renode (`pyrenode3/README.md:11`, `src/pyrenode3/__init__.py:34`). Fallback `subprocess.Popen --port 1234` works without it.
- Qt Creator optional for editing `resources/ui/*.ui`.
- QSS themes: `src/gui/styles/dark_theme.qss` (default) + `light_theme.qss`.

## 4. Launch

```bash
# Desktop app
python -m src.main
# headless API
uvicorn src.api.app:app --port 8000
# CLI single test
renode-resilience run --firmware examples/sensor-firmware/build/sensor.elf --platform platforms/stm32f4_discovery.repl --fault SF-01 --duration 60
```

## 5. Requirements Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Pinned prod deps with hashes |
| `requirements-dev.txt` | pytest, Robot, ruff, mypy |
| `pyproject.toml` | Build + tool config |
| `setup.py` | Legacy fallback |

## 6. Verification Checklist

- [ ] `python -m src.main` opens `QMainWindow 1400×900` blank window (`desktop-application.md:390`).
- [ ] Renode starts via `src/core/renode_bridge.py:RenodeBridge.start()` and monitor responds on 1234.
- [ ] `pip freeze | grep PyQt6` → 6.6+.
- [ ] Example ELF loads: `sysbus LoadELF @examples/sensor-firmware/build/sensor.elf` succeeds.

## 7. Common Install Failures → `18-TROUBLESHOOTING.md`

- `No module named 'PyQt6'` → venv not activated.
- `renode: command not found` → PATH miss; use absolute path in Settings dialog.
- Port 1234 in use → `netstat -ano | findstr 1234` (Win) / `lsof -i:1234` (Unix) then kill.

## 8. Docker (Optional) — Vendored `renode-docker/`

```bash
# Upstream renode-docker (DOTNET 8.0, RENODE_VERSION=1.16.1, `renode-docker/Dockerfile:8`)
docker build -t renode-resilience -f renode-docker/Dockerfile .
# Or minimized: renode-docker/Dockerfile.min (bookworm-slim)
docker build -t renode-resilience -f renode-docker/Dockerfile.min .
docker run -p 8000:8000 -v $(pwd)/examples:/app/examples renode-resilience
# Antmicro Hub alternative: docker run antmicro/renode:latest (renode/README.md:199)
```
See `19-PACKAGING.md` + `renode-docker/README.rst:1`.
