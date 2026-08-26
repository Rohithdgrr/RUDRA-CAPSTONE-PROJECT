"""Build helper — runs pyinstaller src/main.py."""
import subprocess, sys, pathlib, shutil

def main():
    # Clean
    for d in ["build", "dist"]:
        p = pathlib.Path(d)
        if p.exists():
            shutil.rmtree(p)
            print(f"cleaned {p}")
    # Check pyinstaller
    try:
        import PyInstaller  # noqa
    except ImportError:
        print("Installing pyinstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    cmd = [sys.executable, "-m", "PyInstaller", "--windowed", "--onefile", "--name", "RenodeResilience", "--add-data", "resources;resources", "--add-data", "src/gui/styles;src/gui/styles", "src/main.py"]
    print(" ".join(cmd))
    try:
        subprocess.check_call(cmd)
        print("Build done → dist/RenodeResilience.exe (Win) or dist/RenodeResilience (Linux)")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
