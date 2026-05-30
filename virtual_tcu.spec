# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — onedir bundle with pre-built web/dist."""

import importlib.util
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None
project_root = Path(SPECPATH)


def _vgamepad_package_root() -> Path:
    """Locate vgamepad on disk without importing it.

    Importing vgamepad connects to ViGEmBus at module load time, which fails
    on CI/build hosts that do not have the driver installed.
    """
    spec = importlib.util.find_spec("vgamepad")
    if spec is None or not spec.submodule_search_locations:
        raise SystemExit("vgamepad not installed — pip install vgamepad before building")
    return Path(spec.submodule_search_locations[0])


def _vgamepad_hiddenimports(root: Path) -> list[str]:
    names = {"vgamepad"}
    for path in root.rglob("*.py"):
        rel = path.relative_to(root)
        if rel.name == "__init__.py":
            if rel.parent == Path("."):
                continue
            names.add("vgamepad." + ".".join(rel.parent.parts))
        else:
            names.add("vgamepad." + ".".join(rel.with_suffix("").parts))
    return sorted(names)


dist_data = project_root / "virtual_tcu" / "web" / "dist"
if not dist_data.is_dir():
    raise SystemExit(
        f"Missing {dist_data} — run: cd web-ui && npm install && npm run build"
    )

_kb_datas, _kb_binaries, _kb_hidden = collect_all("keyboard")
_aio_datas, _aio_binaries, _aio_hidden = collect_all("aiohttp")

_vg_root = _vgamepad_package_root()
_vg_binaries: list[tuple[str, str]] = []
_vg_hidden = _vgamepad_hiddenimports(_vg_root)

# vgamepad loads ViGEmClient.dll via a hard-coded relative path at import time;
# ensure both arch variants land under the exact tree vigem_client.py expects.
_vg_client = _vg_root / "win" / "vigem" / "client"
_vg_dll_datas = [
    (str(_vg_client / arch / "ViGEmClient.dll"), f"vgamepad/win/vigem/client/{arch}")
    for arch in ("x64", "x86")
    if (_vg_client / arch / "ViGEmClient.dll").is_file()
]
if not _vg_dll_datas:
    raise SystemExit(
        f"Missing ViGEmClient.dll under {_vg_client} — reinstall vgamepad before building"
    )

hiddenimports = (
    list(_kb_hidden)
    + list(_aio_hidden)
    + list(_vg_hidden)
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
        "vgamepad",
        # Listed by name (not collect_submodules) so the build does not import
        # pyvjoy — importing pyvjoy._sdk loads vJoyInterface.dll, which is absent
        # on CI. The DLL ships with the user's vJoy driver install, not with us.
        "pyvjoy",
        "pyvjoy.vjoydevice",
        "pyvjoy._sdk",
        "pyvjoy.constants",
        "pyvjoy.exceptions",
    ]
)

a = Analysis(
    ["virtual_tcu.py"],
    pathex=[str(project_root)],
    binaries=_kb_binaries + _aio_binaries + _vg_binaries,
    datas=[(str(dist_data), "virtual_tcu/web/dist")]
    + _kb_datas
    + _aio_datas
    + _vg_dll_datas,
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
