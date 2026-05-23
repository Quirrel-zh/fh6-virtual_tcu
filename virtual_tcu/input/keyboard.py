import threading
import time

import keyboard

from virtual_tcu.config.constants import Cfg
from virtual_tcu.config.store import ConfigStore


class VirtualKeyboard:
    def __init__(self, config: ConfigStore):
        self._config = config
        self._self_press_until: dict[str, float] = {}
        self.SELF_PRESS_WINDOW_S = 0.15

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
            print(f"[KB] {e}")

    def shift_up(self):
        threading.Thread(
            target=self._press_release, args=(self.key_up,), daemon=True
        ).start()

    def shift_down(self):
        threading.Thread(
            target=self._press_release, args=(self.key_down,), daemon=True
        ).start()

    def shift_down_double(self):
        """Two downshift presses with 60ms gap — skip-gear for hard braking."""

        def _double():
            self._press_release(self.key_down)
            time.sleep(0.06)
            self._press_release(self.key_down)

        threading.Thread(target=_double, daemon=True).start()
