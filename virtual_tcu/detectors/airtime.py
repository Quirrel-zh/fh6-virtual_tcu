from virtual_tcu.telemetry.model import Telemetry

class AirtimeDetector:
    """Detects all four wheels off the ground. Primary: vertical accel
    near zero (free fall). Confirmation: all four wheels spinning. 3
    frames to engage, 2 to disengage."""

    LOW_VERTICAL_G_THRESHOLD = 3.0
    SLIP_ALL_WHEELS_THRESHOLD = 1.2
    MIN_SPEED_FOR_AIRBORNE = 20.0
    FRAMES_TO_ENGAGE = 3
    FRAMES_TO_DISENGAGE = 2

    def __init__(self):
        self._airborne_streak = 0
        self._grounded_streak = 0
        self._is_airborne = False
        self._just_landed = False

    def update(self, td: Telemetry) -> bool:
        low_g = abs(td.accel_y) < self.LOW_VERTICAL_G_THRESHOLD
        thr = self.SLIP_ALL_WHEELS_THRESHOLD
        all_spin = (
            abs(td.slip_fl) > thr
            and abs(td.slip_fr) > thr
            and abs(td.slip_rl) > thr
            and abs(td.slip_rr) > thr
        )
        airborne_now = td.speed_kmh > self.MIN_SPEED_FOR_AIRBORNE and low_g and all_spin

        was_airborne = self._is_airborne

        if airborne_now:
            self._airborne_streak += 1
            self._grounded_streak = 0
            if self._airborne_streak >= self.FRAMES_TO_ENGAGE:
                self._is_airborne = True
        else:
            self._grounded_streak += 1
            self._airborne_streak = 0
            if self._grounded_streak >= self.FRAMES_TO_DISENGAGE:
                self._is_airborne = False

        if was_airborne and not self._is_airborne:
            self._just_landed = True

        return self._is_airborne

    @property
    def is_airborne(self) -> bool:
        return self._is_airborne

    @property
    def just_landed(self) -> bool:
        val = self._just_landed
        self._just_landed = False
        return val

