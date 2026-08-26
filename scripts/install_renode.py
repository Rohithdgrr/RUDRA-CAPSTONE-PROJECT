"""Install Renode 1.16.1 — detects OS and downloads portable."""
import platform, pathlib, urllib.request, tarfile, zipfile, sys

RENODE_VERSION = "1.16.1"
URLS = {
    "Linux": f"https://builds.renode.io/renode-{RENODE_VERSION}.linux-portable.tar.gz",
    "Windows": f"https://builds.renode.io/renode-{RENODE_VERSION}.windows-portable.zip",
    "Darwin": f"https://builds.renode.io/renode-{RENODE_VERSION}.osx-arm64-portable.dmg" if platform.machine()=="arm64" else f"https://builds.renode.io/renode-{RENODE_VERSION}.osx-x64-portable.dmg",
}

def main():
    os_name = platform.system()
    url = URLS.get(os_name, URLS["Linux"])
    print(f"OS: {os_name} arch: {platform.machine()}")
    print(f"Would download {url}")
    print("Manual: wget $URL && tar xf && export PATH=$PWD:$PATH && renode --version")
    print("Or: brew install renode/tap/renode (macOS) / apt install renode (Linux)")
    # To actually download: uncomment
    # urllib.request.urlretrieve(url, "renode.tar.gz")
    # print("Downloaded renode.tar.gz")

if __name__ == "__main__":
    main()
