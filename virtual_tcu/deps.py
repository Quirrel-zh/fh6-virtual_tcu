"""Optional third-party dependencies and platform checks."""

import sys

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
    print("[WARN] aiohttp missing — web UI disabled. Run: pip install aiohttp")
    web = None
    WSMsgType = None

try:
    import vgamepad  # noqa: F401

    VGAMEPAD_OK = True
except ImportError:
    VGAMEPAD_OK = False
    print("[WARN] vgamepad missing — gamepad output mode unavailable. Run: pip install vgamepad")

if not KEYBOARD_OK:
    sys.exit(1)
