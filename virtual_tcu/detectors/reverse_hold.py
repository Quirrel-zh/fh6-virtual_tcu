from virtual_tcu.config.constants import Cfg
from virtual_tcu.input.interface import OutputInterface
from virtual_tcu.telemetry.model import Telemetry


class ReverseHoldDetector:
    """For wheel users without a Reverse button: hold Q while stopped in
    1st → engage R; hold E in R while stopped → exit to 1st. Requires
    paddle release between actions to prevent re-triggering."""

    def __init__(self, kb: OutputInterface):
        self._kb = kb
        self._down_pressed_since: float | None = None
        self._up_pressed_since: float | None = None
        self._down_armed = True
        self._up_armed = True

    def update(self, td: Telemetry, q_held: bool, e_held: bool, now: float):
        if not q_held:
            self._down_armed = True
        if not e_held:
            self._up_armed = True

        if self._down_armed and td.gear == 1 and td.speed_kmh < 3.0 and q_held:
            if self._down_pressed_since is None:
                self._down_pressed_since = now
            elif (now - self._down_pressed_since) * 1000 >= Cfg.REVERSE_HOLD_MS:
                self._kb.shift_to(1, 0)
                self._down_pressed_since = None
                self._down_armed = False
                return "ENGAGED_REVERSE"
        else:
            self._down_pressed_since = None

        if self._up_armed and td.gear == 0 and td.speed_kmh < 3.0 and e_held:
            if self._up_pressed_since is None:
                self._up_pressed_since = now
            elif (now - self._up_pressed_since) * 1000 >= Cfg.REVERSE_EXIT_MS:
                self._kb.shift_to(0, 1)
                self._up_pressed_since = None
                self._up_armed = False
                return "EXITED_REVERSE"
        else:
            self._up_pressed_since = None

        return None
