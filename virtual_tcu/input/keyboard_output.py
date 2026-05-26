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

    def shift_up(self):
        self._executor.submit(self._press_release, self.key_up)

    def shift_down(self):
        self._executor.submit(self._press_release, self.key_down)

    def shift_down_double(self):
        def _double():
            self._press_release(self.key_down)
            time.sleep(0.06)
            self._press_release(self.key_down)

        self._executor.submit(_double)

    def shutdown(self):
        self._executor.shutdown(wait=False)
