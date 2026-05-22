from typing import Dict, Optional

from virtual_tcu.telemetry.model import Telemetry

class _ParabolaFit:
    """Incremental least-squares fit of torque = a*r^2 + b*r + c, where r
    is rpm fraction (0..1). Accumulators decay slowly so the model adapts
    if the car setup changes. O(1) memory — only sums are kept."""

    DECAY = 0.9997

    def __init__(self):
        self.n = self.sx = self.sx2 = self.sx3 = self.sx4 = 0.0
        self.sy = self.sxy = self.sx2y = 0.0
        self._abc = None

    def add(self, x: float, y: float, weight: float = 1.0):
        d = self.DECAY
        self.n = self.n * d + weight
        self.sx = self.sx * d + weight * x
        self.sx2 = self.sx2 * d + weight * x * x
        self.sx3 = self.sx3 * d + weight * x ** 3
        self.sx4 = self.sx4 * d + weight * x ** 4
        self.sy = self.sy * d + weight * y
        self.sxy = self.sxy * d + weight * x * y
        self.sx2y = self.sx2y * d + weight * x * x * y
        self._abc = None

    def solve(self):
        """Return (a, b, c) of the fitted parabola, or None if ill-posed."""
        if self._abc is not None:
            return self._abc
        if self.n < 4:
            return None
        m = [
            [self.sx4, self.sx3, self.sx2],
            [self.sx3, self.sx2, self.sx],
            [self.sx2, self.sx, self.n],
        ]
        rhs = [self.sx2y, self.sxy, self.sy]

        def det3(mat):
            return (
                mat[0][0] * (mat[1][1] * mat[2][2] - mat[1][2] * mat[2][1])
                - mat[0][1] * (mat[1][0] * mat[2][2] - mat[1][2] * mat[2][0])
                + mat[0][2] * (mat[1][0] * mat[2][1] - mat[1][1] * mat[2][0])
            )

        det = det3(m)
        if abs(det) < 1e-9:
            return None

        def swap(mat, col, vec):
            return [
                [vec[r] if c == col else mat[r][c] for c in range(3)]
                for r in range(3)
            ]

        a = det3(swap(m, 0, rhs)) / det
        b = det3(swap(m, 1, rhs)) / det
        c = det3(swap(m, 2, rhs)) / det
        self._abc = (a, b, c)
        return self._abc

    @property
    def x_spread(self) -> float:
        if self.n < 2:
            return 0.0
        mean = self.sx / self.n
        var = self.sx2 / self.n - mean * mean
        return var ** 0.5 if var > 0 else 0.0


class PowerCurveDetector:
    """Per-car engine model. Fits a parabola to (rpm, torque) samples and
    derives peak torque and peak power analytically from the curve.

    Unlike a bucket histogram, this gives a usable estimate from very few
    samples (the curve shape extrapolates the peak) and converges smoothly
    as more data arrives — no binary learning/learned threshold."""

    MIN_SAMPLES = 8
    FULL_CONF_SAMPLES = 80
    MIN_SPREAD = 0.06
    GOOD_SPREAD = 0.16

    def __init__(self):
        self._fits: Dict[int, _ParabolaFit] = {}

    def observe(self, td: Telemetry):
        if td.car_ordinal <= 0 or td.gear < 2:
            return
        if td.throttle < 0.45 or td.torque_nm <= 0 or td.is_shifting:
            return
        r = td.rpm_pct
        if r < 0.20 or r > 1.0:
            return
        # Partial throttle and some slip still carry curve-shape info but
        # weigh less — the least-squares fit absorbs them as soft evidence.
        weight = 1.0
        if td.throttle < 0.70:
            weight *= 0.5
        if td.rear_slip > 0.5:
            weight *= 0.4
        self._fits.setdefault(td.car_ordinal, _ParabolaFit()).add(
            r, td.torque_nm, weight
        )

    def _peaks(self, car_ordinal: int):
        """Return (peak_torque_rpm, peak_power_rpm, confidence)."""
        fit = self._fits.get(car_ordinal)
        if fit is None or fit.n < self.MIN_SAMPLES:
            return None, None, 0.0
        abc = fit.solve()
        if abc is None:
            return None, None, 0.0
        a, b, c = abc
        if a >= -1e-6:  # not concave-down → no torque peak in range yet
            return None, None, 0.0

        pt = max(0.40, min(0.98, -b / (2 * a)))

        # Peak power: maximize torque*rpm = a r^3 + b r^2 + c r.
        # dP/dr = 3a r^2 + 2b r + c.
        deriv_at_redline = 3 * a + 2 * b + c
        if deriv_at_redline > 0:
            # Power still climbing at the limiter — high-rev NA engines
            # (e.g. BMW S54). The "peak" is effectively the redline:
            # shift as late as possible.
            pp = 0.97
        else:
            disc = 4 * b * b - 12 * a * c
            if disc < 0:
                pp = min(pt + 0.10, 0.95)
            else:
                sq = disc ** 0.5
                roots = [(-2 * b + sq) / (6 * a), (-2 * b - sq) / (6 * a)]
                cands = [r for r in roots if pt - 0.02 <= r <= 1.0]
                pp = max(cands) if cands else min(pt + 0.10, 0.95)
        pp = max(pt, min(0.97, pp))

        n_conf = max(0.0, min(1.0,
            (fit.n - self.MIN_SAMPLES) / (self.FULL_CONF_SAMPLES - self.MIN_SAMPLES)))
        s_conf = max(0.0, min(1.0,
            (fit.x_spread - self.MIN_SPREAD) / (self.GOOD_SPREAD - self.MIN_SPREAD)))
        return pt, pp, n_conf * s_conf

    def peak_torque_rpm(self, car_ordinal: int) -> Optional[float]:
        return self._peaks(car_ordinal)[0]

    def peak_power_rpm(self, car_ordinal: int) -> Optional[float]:
        return self._peaks(car_ordinal)[1]

    def confidence(self, car_ordinal: int) -> float:
        return self._peaks(car_ordinal)[2]

    def optimal_upshift_rpm(
        self, td: Telemetry, fallback: float = 0.85, offset: float = 0.03
    ) -> float:
        pt, pp, conf = self._peaks(td.car_ordinal)
        if pp is None:
            return fallback
        model = max(0.65, min(0.97, pp + offset))
        # Blend: early low-confidence estimates lean on the fallback,
        # mature ones trust the model fully.
        return conf * model + (1.0 - conf) * fallback

    def has_data(self, car_ordinal: int) -> bool:
        return self._peaks(car_ordinal)[1] is not None

