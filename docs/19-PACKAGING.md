# 19 — Packaging & Distribution

> **Tool:** PyInstaller 6.0+, NSIS (Win), create-dmg (macOS), appimagetool (Linux) | `scripts/package.py`, `scripts/build.py`

## 1. Outputs

| Platform | Artifact | Toolchain | Size |
|----------|----------|-----------|------|
| Windows | `RenodeResilience-1.0.0-setup.exe` | PyInstaller + NSIS | ~150MB |
| macOS | `RenodeResilience-1.0.0.dmg` | PyInstaller + create-dmg | ~180MB |
| Linux | `RenodeResilience-1.0.0.AppImage` | PyInstaller + appimagetool | ~160MB |

Bundles Python 3.11 runtime, PyQt6, Renode portable, all pip deps frozen (`desktop-application.md:583-596`).

## 2. Build Steps

```bash
# 1. Install pyinstaller
pip install pyinstaller

# 2. Build (auto-detects OS)
python scripts/build.py   # runs pyinstaller src/main.py --windowed --onefile

# 3. Package
python scripts/package.py --version 1.0.0
# Win: + NSIS script → dist/RenodeResilience-1.0.0-setup.exe
# mac: + create-dmg
# linux: + AppImage

# Optional: auto-updater bundle
python scripts/package.py --with-updater  # pyupdater 4.0+
```

PyInstaller spec: `RenodeResilience.spec` includes `resources/*`, `src/gui/styles/*`, `platforms/*.repl`, `templates/*.html`, hidden imports `PyQt6, PyQtGraph`.

## 3. Scripts

| Script | Purpose |
|--------|---------|
| `scripts/build.py` | Clean `build/ dist/`, run PyInstaller, copy resources |
| `scripts/package.py` | OS-specific installer, codesign placeholder |
| `scripts/install_renode.py` | Download pinned Renode 1.15+ (tested `1.16.1` `renode-docker/Dockerfile:8`, `renode/README.md:36`) portable per OS |

## 4. CI/CD (GitHub Actions) — Uses `renode-test-action`

`.github/workflows/release.yml` (planned `README.md:776`) + `renode-test-action/action.yml:1` `Run tests in Renode` (`composite` 9 steps: clone renode at `renode-revision`, `actions/cache/restore@v4`, `build.sh --net`, `setup-uv@v7`, `renode-test -r`):
```yaml
on: tag v*
jobs:
  build:
    matrix: [windows-latest, macos-latest, ubuntu-latest]
    steps: [checkout, setup-python 3.11, pip install -r requirements.txt, run scripts/build.py, upload artifact]
  test:
    uses: ./renode-test-action
    with: { renode-revision: 'master', tests-to-run: 'tests/integration/**/*.robot', gather-execution-metrics: 'no' }
```

## 5. Docker (Optional) — Vendored `renode-docker/`

Upstream `renode-docker/Dockerfile:1` (`mcr.microsoft.com/dotnet/runtime:8.0-noble ARG RENODE_VERSION=1.16.1`) + `Dockerfile.min:1` multi-stage `builder ubuntu:24.04 → runtime bookworm-slim` are vendored. Fork for resilience:

```dockerfile
FROM python:3.11-slim
RUN apt update && apt install -y renode libcairo2  # or COPY --from=renode-docker builder
COPY . /app
RUN pip install -r requirements.txt -r renode/tests/requirements.txt
CMD ["python","-m","src.main", "--headless"]
# Or use renode-docker directly: docker run -ti --net=host antmicro/renode:nightly-dotnet (renode/README.md:208)
```
Build: `docker build -t renode-resilience .` or `docker build -f renode-docker/Dockerfile -t renode .` — see `02-INSTALL.md` + `renode-docker/README.rst:1`.

## 6. Auto-Updater

`pyupdater` 4.0+ (`desktop-application.md:94`) — checks GitHub releases; incremental patches. Config `src/config/defaults.py:auto_update=True`.

## 7. Signing & Notarization

- Windows: `signtool sign /fd SHA256 dist/*.exe` (EV cert).
- macOS: `codesign --deep` + `notarytool submit`.
- Linux: GPG sign AppImage.

## 8. Smoke Test

After package:
```bash
# Win
dist/RenodeResilience/RenodeResilience.exe --help
# Check QMainWindow opens, RenodeBridge.start() works, RI calc
```

## 9. Future

- MSIX (Win Store), Homebrew cask, AUR.
- One-click installer with bundled Renode vs system Renode choice (`README.md:809`).
