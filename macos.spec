# -*- mode: python ; coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.abspath(SPECPATH))

from src.video_tagger import __version__

block_cipher = None

# python_lib = "/Users/changjo/miniconda3/envs/py3.12/lib/libpython3.12.dylib"
# binaries = []
# if os.path.exists(python_lib):
#     binaries.append((python_lib, "."))
# else:
#     print("libpython3.12.dylib not found at", python_lib)

a = Analysis(
    ["main.py"],
    pathex=[os.path.abspath(SPECPATH)],
    # binaries=binaries,
    datas=[
        ("./config/*", "./config"),
        ("./resources/*", "./resources"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    exclude_binaries=False,
    name="SimpleVideoTagger",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)

app = BUNDLE(
    exe,
    name="SimpleVideoTagger.app",
    icon="resources/icons/icon.icns",
    version=__version__,
    bundle_identifier="com.simplevideotagger.app",
)
