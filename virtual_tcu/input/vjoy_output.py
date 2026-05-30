import time
from concurrent.futures import ThreadPoolExecutor

from virtual_tcu.config.store import ConfigStore
from virtual_tcu.input.interface import OutputInterface

_BUTTON_MAP: dict[str, int] = {}


def _build_button_map() -> dict[str, int]:
    return {
        "B1": 1,
        "B2": 2,
        "B3": 3,
        "B4": 4,
        "B5": 5,
        "B6": 6,
        "B7": 7,
        "B8": 8,
        "B9": 9,
        "B10": 10,
        "B11": 11,
        "B12": 12,
        "B13": 13,
        "B14": 14,
    }


class VJoyOutput(OutputInterface):
    def __init__(self, config: ConfigStore):
        global _BUTTON_MAP
        self._config = config
        if not _BUTTON_MAP:
            _BUTTON_MAP = _build_button_map()
        try:
            from pyvjoy import VJoyDevice

            self._v_device = VJoyDevice(1)
        except Exception as e:
            raise RuntimeError(
                "vJoy driver not found - vJoy output unavailable.\n"
                "  Download the installer: https://github.com/BrunnerInnovation/vJoy/releases\n"
                "  After installing, reboot Windows, then restart Virtual TCU.\n"
                f"  (Original error: {e})"
            ) from e
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="VJoy_Worker")
        self._v_device.reset()
        self._v_device.reset_buttons()
        self._v_device.update()

    @property
    def key_up(self) -> str:
        return str(self._config.get("vjoy_shift_key_up", "B13")).upper()

    @property
    def key_down(self) -> str:
        return str(self._config.get("vjoy_shift_key_down", "B14")).upper()

    @property
    def key_clutch(self) -> str:
        return str(self._config.get("vjoy_clutch_key", "B12")).upper()

    @property
    def direct_shift(self) -> bool:
        return self._config.get("vjoy_direct_shift", True)

    @property
    def use_clutch(self) -> bool:
        return self._config.get("vjoy_use_clutch", False)

    def is_self_press(self, key: str) -> bool:
        # vJoy doesn't have a keyboard-style echo problem — the TCU
        # injects buttons, the game reads them, no paddle listener conflict.
        return False

    def shift_to(self, from_gear: int, target_gear: int):
        # from_gear and target_gear must be 0-10
        if not (0 <= from_gear <= 10) or not (0 <= target_gear <= 10):
            print(f"[VJoy] invalid gear numbers: from {from_gear} to {target_gear}")
            return
        if from_gear == target_gear:
            return
        shifts_needed = abs(target_gear - from_gear)
        if not self.direct_shift:
            # fallback to SMG
            def _multi_shift():
                for i in range(shifts_needed):
                    self._press_release(self.key_up if target_gear > from_gear else self.key_down)
                    if i < shifts_needed - 1:
                        time.sleep(0.06)

            self._executor.submit(_multi_shift)
        else:
            # 0 for reverse(B11), 1-10 for gears
            gear_btn = f"B{target_gear}" if target_gear > 0 else "B11"
            self._executor.submit(self._press_release, gear_btn)

    def shutdown(self):
        self._v_device.reset()
        self._v_device.reset_buttons()
        self._v_device.update()
        self._executor.shutdown(wait=False)

    # -- internals -------------------------------------------------------------

    def _press_release(self, name: str):
        """Press *name*, hold BUTTON_HOLD_S, release, and update the device."""
        btn = _BUTTON_MAP.get(name.upper())
        if btn is None:
            print(f"[VJoy] unknown button '{name}' - check config")
            return
        clutch_btn = _BUTTON_MAP.get(self.key_clutch) if self.use_clutch else None
        try:
            if self.direct_shift:
                self._v_device.reset_buttons()
            if self.use_clutch:
                self._v_device.set_button(clutch_btn, 1)
            self._v_device.set_button(btn, 1)
            if self.use_clutch:
                self._v_device.set_button(clutch_btn, 0)
            if self.direct_shift:
                return
            self._v_device.set_button(btn, 0)
        except Exception as e:
            print(f"[VJoy] input simulation failed: {e}")
