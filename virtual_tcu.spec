# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — onedir bundle with pre-built web/dist."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None
project_root = Path(SPECPATH)

dist_data = project_root / "virtual_tcu" / "web" / "dist"
if not dist_data.is_dir():
    raise SystemExit(
        f"Missing {dist_data} — run: cd web-ui && npm install && npm run build"
    )

_kb_datas, _kb_binaries, _kb_hidden = collect_all("keyboard")
_aio_datas, _aio_binaries, _aio_hidden = collect_all("aiohttp")

hiddenimports = (
    list(_kb_hidden)
    + list(_aio_hidden)
    + collect_submodules("multidict")
    + collect_submodules("yarl")
    + collect_submodules("frozenlist")
    + collect_submodules("aiosignal")
    + collect_submodules("virtual_tcu")
    + [
        "virtual_tcu.bootstrap",
        "virtual_tcu.paths",
        "virtual_tcu.deps",
        "virtual_tcu.state.shift_history",
        "keyboard",
    ]
)

a = Analysis(
    ["virtual_tcu.py"],
    pathex=[str(project_root)],
    binaries=_kb_binaries + _aio_binaries,
    datas=[(str(dist_data), "virtual_tcu/web/dist")] + _kb_datas + _aio_datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name="VirtualTCU",
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
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="VirtualTCU",
)
