"""Race downshift aggressiveness + global airborne-hold tests.

Covers the P0 changes:
- power-demand downshift fires on heavy-throttle / low-rev / flat ground
- over-rev guard still blocks a downshift that would exceed redline
- Race brake-down uses a looser gate than Comfort (moderate sustained
  brake while slowing downshifts in Race, not in Comfort)
- the global airborne hold blocks the pre-dispatch GEAR MISMATCH path that
  the per-mode transient block never reached
"""

from tests.conftest import make_telemetry
from virtual_tcu.config.constants import Cfg


def _kinds(out):
    return [k for k, _ in out.shifts]


def test_power_demand_downshift_fires(make_logic, out, clock):
    # gear 5 @ 130 km/h, ratio 35 -> rpm ~4550 (pct 0.57 < 0.60 floor),
    # heavy throttle, no brake, flat road -> should drop a gear.
    tcu = make_logic("RACE")
    td = make_telemetry(speed_ms=130 / 3.6, current_rpm=35 * 130, accel_raw=int(0.90 * 255), gear=5)
    for _ in range(20):
        clock.now += 0.016
        out.now = clock.now
        tcu.process(td)
    assert "DOWN" in _kinds(out) or "DOWN2" in _kinds(out)


def test_power_demand_skips_when_in_band(make_logic, out, clock):
    # Already in the power band (rpm_pct ~0.85) -> no power-demand downshift.
    tcu = make_logic("RACE")
    speed = (0.85 * 8000) / 35  # ratio 35 -> rpm_pct 0.85
    td = make_telemetry(
        speed_ms=speed / 3.6, current_rpm=0.85 * 8000, accel_raw=int(0.90 * 255), gear=5
    )
    for _ in range(20):
        clock.now += 0.016
        out.now = clock.now
        tcu.process(td)
    assert "DOWN" not in _kinds(out) and "DOWN2" not in _kinds(out)


def test_shift_down_blocks_overrev(make_logic, out, clock):
    # gear 3 @ 110 km/h; downshift to gear 2 (ratio 80) -> 8800 rpm > 1.02*8000.
    tcu = make_logic("RACE")
    td = make_telemetry(speed_ms=110 / 3.6, current_rpm=58 * 110, gear=3)
    assert tcu._shift_down(td, 300, "TEST") is False
    assert out.shifts == []
    assert tcu._tcu_state == "OVER-REV BLOCKED"


def _feed_decel(tcu, out, clock, *, gear, brake, throttle, start_kmh, ratio, frames=16, step=1.2):
    for i in range(frames):
        spd = start_kmh - i * step
        clock.now += 0.016
        out.now = clock.now
        td = make_telemetry(
            speed_ms=spd / 3.6,
            current_rpm=ratio * spd,
            accel_raw=int(throttle * 255),
            brake_raw=int(brake * 255),
            gear=gear,
        )
        tcu.process(td)


def test_race_brake_down_on_moderate_sustained_brake(make_logic, out, clock):
    # Moderate brake (0.40) while clearly slowing -> Race downshifts.
    tcu = make_logic("RACE")
    _feed_decel(tcu, out, clock, gear=4, brake=0.40, throttle=0.0, start_kmh=135, ratio=44.0)
    assert "DOWN" in _kinds(out)


def test_comfort_holds_on_moderate_sustained_brake(make_logic, out, clock):
    # Same moderate brake in Comfort -> strict gate, no downshift.
    tcu = make_logic("COMFORT")
    _feed_decel(tcu, out, clock, gear=4, brake=0.40, throttle=0.0, start_kmh=135, ratio=44.0)
    assert "DOWN" not in _kinds(out)


def test_airborne_hold_blocks_mismatch(make_logic, out, clock):
    # Establish airborne at speed (no mismatch), then drop into a
    # mismatch-shaped frame (tall gear, low speed, low rpm) while still
    # airborne. The global hold must suppress the MISMATCH downshift.
    tcu = make_logic("RACE")
    high = make_telemetry(speed_ms=140 / 3.6, accel_y=-12.5, current_rpm=35 * 140, gear=5)
    for _ in range(5):
        clock.now += 0.016
        out.now = clock.now
        tcu.process(high)
    assert tcu._airtime.is_airborne
    # mismatch-shaped, still airborne (speed 30 > 15 keeps detector aloft)
    mismatch = make_telemetry(speed_ms=30 / 3.6, accel_y=-12.5, current_rpm=35 * 30, gear=5)
    for _ in range(5):
        clock.now += 0.016
        out.now = clock.now
        tcu.process(mismatch)
    assert out.shifts == []
    assert tcu._tcu_state == "AIRBORNE"


def test_grounded_mismatch_downshifts(make_logic, out, clock):
    # Same mismatch shape on the ground -> MISMATCH downshift fires,
    # proving it's the airborne hold (not some other guard) doing the work.
    tcu = make_logic("RACE")
    md = make_telemetry(speed_ms=30 / 3.6, accel_y=0.0, current_rpm=35 * 30, gear=5)
    clock.now += 0.016
    out.now = clock.now
    tcu.process(md)
    assert "DOWN" in _kinds(out)
    assert Cfg.MIN_SPEED_KMH < 30  # sanity: not the standstill path
