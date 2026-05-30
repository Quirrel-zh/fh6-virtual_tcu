"""Gamepad output via vgamepad / ViGEmBus virtual XInput device.

Requires ``pip install vgamepad`` and the ViGEmBus driver (the vgamepad
installer launches it automatically on first install — accept the UAC
prompt).  Only Windows is supported in production.
"""

import time
from concurrent.futures import ThreadPoolExecutor

from virtual_tcu.config.store import ConfigStore
from virtual_tcu.input.interface import OutputInterface

# Friendly-name → XUSB_BUTTON constant lookup table.
# Populated lazily in __init__ so the import error for vgamepad is surfaced
# at the right time with a clear message.
_BUTTON_MAP: dict[str, int] = {}


def _build_button_map() -> dict[str, int]:
    """Return {friendly_name: xusb_constant} for every supported button."""
    import vgamepad as vg

    return {
        "A": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
        "B": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
        "X": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
        "Y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
        "LB": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
        "RB": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
        "DPAD_UP": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
        "DPAD_DOWN": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
        "DPAD_LEFT": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
        "DPAD_RIGHT": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
        "START": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
        "BACK": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        "L3": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
        "R3": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
    }


def check_gamepad_available() -> tuple[bool, str]:
    """Probe whether the ViGEmBus driver is installed and functional.

    Opens a transient bus connection only — does **not** spawn a virtual
    XInput device.  Spawning ``VX360Gamepad`` during a check would create a
    ghost controller in Windows and can fail while an active ``GamepadOutput``
    instance already holds the bus.
    """
    try:
        import vgamepad.win.vigem_client as vcli
        import vgamepad.win.vigem_commons as vcom
    except (ImportError, OSError) as e:
        return False, f"client_unavailable: {e}"

    busp = None
    try:
        busp = vcli.vigem_alloc()
        if not busp:
            return False, "alloc_failed"
        err = vcli.vigem_connect(busp)
        if err != vcom.VIGEM_ERRORS.VIGEM_ERROR_NONE:
            name = vcom.VIGEM_ERRORS(err).name
            if name == "VIGEM_ERROR_BUS_NOT_FOUND":
                return False, "driver_missing"
            return False, name
        return True, ""
    except Exception as e:
        return False, str(e)
    finally:
        if busp:
            try:
                vcli.vigem_disconnect(busp)
                vcli.vigem_free(busp)
            except Exception:
                pass


class GamepadOutput(OutputInterface):
    """Inject shift commands as virtual Xbox 360 controller button presses.

    Creates a virtual XInput device via the ViGEmBus driver.  The device
    appears in Windows as soon as this object is constructed and disappears
    when ``shutdown()`` is called or the process exits.

    **ViGEmBus driver required.**  If the driver is not installed, the
    constructor raises ``RuntimeError`` with a link to the installer.
    The driver is a one-time system-level install (requires admin + reboot).
    Many gaming tools (Steam, DS4Windows, reWASD) already ship it, so it
    may already be present.
    """

    VIGEMBUS_URL = (
        "https://github.com/Forza-Love/fh6-virtual_tcu/raw/main/driver/ViGEmBusSetup_x64.msi"
    )

    # How long a button is held down (seconds).
    BUTTON_HOLD_S = 0.06

    def __init__(self, config: ConfigStore):
        global _BUTTON_MAP
        if not _BUTTON_MAP:
            _BUTTON_MAP = _build_button_map()

        import vgamepad as vg

        self._config = config
        self._vg = vg

        try:
            self._gamepad = vg.VX360Gamepad()
        except Exception as e:
            raise RuntimeError(
                "ViGEmBus driver not found - gamepad output unavailable.\n"
                f"  Download the installer: {self.VIGEMBUS_URL}\n"
                "  After installing, reboot Windows, then restart Virtual TCU.\n"
                f"  (Original error: {e})"
            ) from e

        # Wake the device — some games ignore the first input otherwise.
        self._gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        self._gamepad.update()
        time.sleep(0.02)
        self._gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        self._gamepad.update()

        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="GP_Worker")

    # -- OutputInterface -------------------------------------------------------

    @property
    def key_up(self) -> str:
        return str(self._config.get("gamepad_shift_up", "B")).upper()

    @property
    def key_down(self) -> str:
        return str(self._config.get("gamepad_shift_down", "X")).upper()

    def is_self_press(self, key: str) -> bool:
        # Gamepads don't have a keyboard-style echo problem — the TCU
        # injects buttons, the game reads them, no paddle listener conflict.
        return False

    def shift_to(self, from_gear: int, target_gear: int):
        # from_gear and target_gear must be 0-10
        if not (0 <= from_gear <= 10) or not (0 <= target_gear <= 10):
            print(f"[Gamepad] invalid gear numbers: from {from_gear} to {target_gear}")
            return
        if from_gear == target_gear:
            return

        shifts_needed = abs(target_gear - from_gear)

        def _multi_shift():
            for i in range(shifts_needed):
                self._press_release(self.key_up if target_gear > from_gear else self.key_down)
                if i < shifts_needed - 1:
                    time.sleep(0.06)

        self._executor.submit(_multi_shift)

    def shutdown(self):
        self._executor.shutdown(wait=False)
        try:
            self._gamepad.reset()
            self._gamepad.update()
        except Exception:
            pass

    # -- internals -------------------------------------------------------------

    def _press_release(self, name: str):
        """Press *name*, hold BUTTON_HOLD_S, release, and update the device."""
        btn = _BUTTON_MAP.get(name.upper())
        if btn is None:
            print(f"[Gamepad] unknown button '{name}' - check config")
            return
        try:
            self._gamepad.press_button(button=btn)
            self._gamepad.update()
            time.sleep(self.BUTTON_HOLD_S)
            self._gamepad.release_button(button=btn)
            self._gamepad.update()
        except Exception as e:
            print(f"[Gamepad] input simulation failed: {e}")
