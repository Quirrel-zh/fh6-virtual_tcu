"""Console encoding helpers for Windows regional locales (e.g. cp932)."""

from __future__ import annotations

import sys


def configure_stdio_utf8() -> None:
    """Force UTF-8 on stdout/stderr so Unicode prints never crash the backend."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass
