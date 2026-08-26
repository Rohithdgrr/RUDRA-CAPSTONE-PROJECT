import os
import importlib.util

if os.name != 'nt' and importlib.util.find_spec('bpython'):
    import bpython
    run_repl_with = lambda local: bpython.embed(local)
elif importlib.util.find_spec('ptpython'):
    import ptpython
    run_repl_with = lambda local: ptpython.repl.embed(local)
else:
    import code
    run_repl_with = lambda local: code.interact(local=local)

import pyrenode3


def main():
    local = {
        "e": pyrenode3.wrappers.Emulation(),
        "m": pyrenode3.wrappers.Monitor(),
        "RPath": pyrenode3.RPath,
        "interface_to_class": pyrenode3.interface_to_class,
    }

    for wrapper_name in pyrenode3.wrappers.__all__:
        local[wrapper_name] = getattr(pyrenode3.wrappers, wrapper_name)

    run_repl_with(local)
