# PyInstaller spec — RenodeResilience.spec
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None
a = Analysis(['src/main.py'], pathex=[], binaries=[], datas=[('resources','resources'), ('src/gui/styles','src/gui/styles')], hiddenimports=['PyQt6','pyqtgraph','pandas'], hookspath=[], runtime_hooks=[])
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, name='RenodeResilience', debug=False, strip=False, upx=True, console=False)
