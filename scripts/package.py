"""Package helper — wraps build + OS installer stub."""
import argparse, pathlib
parser = argparse.ArgumentParser()
parser.add_argument("--version", default="1.0.0")
parser.add_argument("--with-updater", action="store_true")
args = parser.parse_args()
print(f"package.py — version {args.version} updater={args.with_updater}")
print("Would run: pyinstaller + NSIS (Win) / create-dmg (macOS) / appimagetool (Linux)")
print("See docs/19-PACKAGING.md for manual: python scripts/build.py")
# Placeholder for signing
dist = pathlib.Path("dist")
if dist.exists():
    print(f"dist contents: {list(dist.iterdir())}")
else:
    print("No dist/ yet — run build first")
