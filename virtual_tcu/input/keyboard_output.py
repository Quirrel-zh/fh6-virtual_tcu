import time
from concurrent.futures import ThreadPoolExecutor

import keyboard

from virtual_tcu.config.constants import Cfg
from virtual_tcu.config.store import ConfigStore
from virtual_tcu.input.interface import OutputInterface


class KeyboardOutput(OutputInterface):
    """Inject shift commands as keyboard key-presses (E / Q by default)."""

    def __init__(self, config: ConfigStore):
        self._config = config
        self._self_press_until: dict[str, float] = {}
        self.SELF_PRESS_WINDOW_S = 0.15
        # Single worker ensures keystrokes are executed sequentially without thread leaks
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="KB_Worker")

    @property
    def key_up(self) -> str:
        return str(self._config.get("shift_key_up", "e")).lower()

    @property
    def key_down(self) -> str:
        return str(self._config.get("shift_key_down", "q")).lower()

    def is_self_press(self, key: str) -> bool:
        return time.time() < self._self_press_until.get(key.lower(), 0.0)

    def _press_release(self, key: str):
        try:
            key = key.lower()
            self._self_press_until[key] = time.time() + self.SELF_PRESS_WINDOW_S
            keyboard.press(key)
            time.sleep(Cfg.KEY_HOLD_S)
            keyboard.release(key)
        except Exception as e:
            print(f"[KB] Input simulation failed: {e}")

    def shift_to(self, from_gear: int, target_gear: int):
        # from_gear and target_gear must be 0-10
        if not (0 <= from_gear <= 10) or not (0 <= target_gear <= 10):
            print(f"[Keyboard] invalid gear numbers: from {from_gear} to {target_gear}")
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
