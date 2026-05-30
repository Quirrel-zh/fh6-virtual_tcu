from dataclasses import dataclass

from virtual_tcu.telemetry.model import Telemetry


@dataclass(frozen=True)
class AirState:
    """Per-frame airtime result. ``airborne`` is the steady state; the two
    ``*_started`` / ``just_landed`` flags are one-frame edges the caller uses
    to fire takeoff / landing hooks exactly once."""

    airborne: bool
    airborne_started: bool
    just_landed: bool


class AirtimeDetector:
    """Detects the car leaving the ground and the moment it lands again.

    Evidence is weighted rather than all-or-nothing: vertical motion
    (``vel_y``) and low vertical G are the gate, wheel slip grades the
    confidence. All four wheels spinning is strong evidence and engages in
    two frames; two-to-three wheels is medium and needs three. A short
    landing window stays open after touchdown so the shift logic can pull a
    recovery gear before normal rules resume."""

    LOW_VERTICAL_G_THRESHOLD = 3.0
    VERTICAL_VEL_THRESHOLD = 1.0
    VERTICAL_VEL_GROUNDED = 0.6
    SLIP_WHEEL_THRESHOLD = 1.2
    MIN_SPEED_FOR_AIRBORNE = 20.0
    FRAMES_STRONG_ENGAGE = 2
    FRAMES_MEDIUM_ENGAGE = 3
    FRAMES_TO_DISENGAGE = 2
    LANDING_WINDOW_S = 0.75

    def __init__(self):
        self._strong_streak = 0
        self._entry_streak = 0  # medium-or-stronger frames in a row
        self._grounded_streak = 0
        self._is_airborne = False
        self._landing_until = 0.0

    def update(self, td: Telemetry, now: float) -> AirState:
        low_g = abs(td.accel_y) < self.LOW_VERTICAL_G_THRESHOLD
        vertical_motion = abs(td.vel_y) > self.VERTICAL_VEL_THRESHOLD
        thr = self.SLIP_WHEEL_THRESHOLD
        n_slip = (
            (abs(td.slip_fl) > thr)
            + (abs(td.slip_fr) > thr)
            + (abs(td.slip_rl) > thr)
            + (abs(td.slip_rr) > thr)
        )

        # Gate: must be moving and either free-falling (low G) or visibly
        # travelling vertically. Without the gate, plain wheelspin on tarmac
        # would read as airborne.
        gate = td.speed_kmh > self.MIN_SPEED_FOR_AIRBORNE and (low_g or vertical_motion)

        strong = gate and n_slip == 4
        medium = gate and n_slip >= 2
        any_evidence = gate and (n_slip >= 2 or (vertical_motion and low_g))

        if strong:
            self._strong_streak += 1
        else:
            self._strong_streak = 0
        if medium:
            self._entry_streak += 1
        else:
            self._entry_streak = 0

        airborne_started = False
        just_landed = False

        if not self._is_airborne:
            if (
                self._strong_streak >= self.FRAMES_STRONG_ENGAGE
                or self._entry_streak >= self.FRAMES_MEDIUM_ENGAGE
            ):
                self._is_airborne = True
                self._grounded_streak = 0
                airborne_started = True
        else:
            # Any evidence (down to a weak vel_y candidate) keeps us aloft and
            # bridges momentary slip dropouts at the jump's apex.
            grounded_vote = (
                not any_evidence
                and abs(td.vel_y) < self.VERTICAL_VEL_GROUNDED
                and not low_g
                and n_slip == 0
            )
            if grounded_vote:
                self._grounded_streak += 1
                if self._grounded_streak >= self.FRAMES_TO_DISENGAGE:
                    self._is_airborne = False
                    self._landing_until = now + self.LANDING_WINDOW_S
                    just_landed = True
            else:
                self._grounded_streak = 0

        return AirState(
            airborne=self._is_airborne,
            airborne_started=airborne_started,
            just_landed=just_landed,
        )

    @property
    def is_airborne(self) -> bool:
        return self._is_airborne

    @property
    def landing_until(self) -> float:
        return self._landing_until
