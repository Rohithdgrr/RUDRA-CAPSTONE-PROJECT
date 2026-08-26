import os

# Env variable names
PYRENODE_BIN          = "PYRENODE_BIN"
PYRENODE_BUILD_DIR    = "PYRENODE_BUILD_DIR"
PYRENODE_BUILD_OUTPUT = "PYRENODE_BUILD_OUTPUT"
PYRENODE_PATH         = "PYRENODE_PATH"
PYRENODE_PKG          = "PYRENODE_PKG"
PYRENODE_SKIP_LOAD    = "PYRENODE_SKIP_LOAD"

PYRENODE_PATH_ALIASES = (
    PYRENODE_PKG,
    PYRENODE_BUILD_DIR,
    PYRENODE_BIN,
)

# Values of env variables
pyrenode_bin          = os.environ.get(PYRENODE_BIN)
pyrenode_build_dir    = os.environ.get(PYRENODE_BUILD_DIR)
pyrenode_build_output = os.environ.get(PYRENODE_BUILD_OUTPUT)
pyrenode_path         = os.environ.get(PYRENODE_PATH)
pyrenode_pkg          = os.environ.get(PYRENODE_PKG)
pyrenode_skip_load    = os.environ.get(PYRENODE_SKIP_LOAD)
