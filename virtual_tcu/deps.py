"""Optional third-party dependencies and platform checks."""

import sys

from virtual_tcu.console import configure_stdio_utf8

configure_stdio_utf8()

try:
    import winsound

    WINSOUND_OK = True
except ImportError:
    winsound = None  # type: ignore[misc, assignment]
    WINSOUND_OK = False

try:
    import keyboard  # noqa: F401

    KEYBOARD_OK = True
except ImportError:
    KEYBOARD_OK = False
    print("[ERROR] keyboard library missing. Run: pip install keyboard")

try:
    from aiohttp import WSMsgType, web

    AIOHTTP_OK = True
except ImportError:
    AIOHTTP_OK = False
    print("[WARN] aiohttp missing - web UI disabled. Run: pip install aiohttp")
    web = None
    WSMsgType = None

if not KEYBOARD_OK:
    sys.exit(1)
