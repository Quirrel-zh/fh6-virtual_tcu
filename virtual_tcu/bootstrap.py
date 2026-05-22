"""Startup helpers for dev and frozen (PyInstaller) builds."""

from __future__ import annotations

import sys
import traceback
from pathlib import Path


def crash_log_path() -> Path:
    from virtual_tcu import paths

    return paths.user_data_dir() / "crash.log"


def write_crash_log(exc: BaseException) -> Path:
    log = crash_log_path()
    try:
        log.write_text(
            "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
            encoding="utf-8",
        )
    except OSError:
        pass
    return log


def pause_before_exit(code: int = 1) -> None:
    """Keep console open on failure when double-clicking the exe."""
    from virtual_tcu import paths

    if code == 0 and not paths.is_frozen():
        return
    try:
        input("\nPress Enter to exit...")
    except (EOFError, KeyboardInterrupt):
        pass


def report_fatal(message: str, *, exc: BaseException | None = None) -> None:
    print(f"\n[ERROR] {message}")
    if exc is not None:
        print()
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        log = write_crash_log(exc)
        print(f"\n  Crash log: {log}")
    pause_before_exit(1)
    sys.exit(1)
