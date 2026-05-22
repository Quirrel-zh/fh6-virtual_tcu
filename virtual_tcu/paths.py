"""Runtime path resolution for dev and PyInstaller frozen builds."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def bundle_root() -> Path:
    """Read-only bundle root (_MEIPASS when frozen, repo root in dev)."""
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent


def user_data_dir() -> Path:
    """Writable data directory (%APPDATA%/VirtualTCU when frozen, cwd in dev)."""
    if is_frozen():
        root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        data = root / "VirtualTCU"
    else:
        data = Path.cwd()
    data.mkdir(parents=True, exist_ok=True)
    return data


def web_dist_dir() -> Path:
    return bundle_root() / "virtual_tcu" / "web" / "dist"


def config_file() -> Path:
    return user_data_dir() / "tcu_config.json"


def profiles_file() -> Path:
    return user_data_dir() / "tcu_profiles.json"


def log_dir() -> Path:
    d = user_data_dir() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def last_run_marker() -> Path:
    return user_data_dir() / ".tcu_last_run"
