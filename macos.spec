# -*- mode: python ; coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.abspath(SPECPATH))

from src.video_tagger import __version__

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("./config/*", "./config"),
        ("./resources/*", "./resources"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SimpleVideoTagger",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="main",
)

app = BUNDLE(
    coll,
    name="SimpleVideoTagger.app",
    icon="resources/icons/icon.icns",
    version=__version__,
    bundle_identifier="com.simplevideotagger.app",
)
