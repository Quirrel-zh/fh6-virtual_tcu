import math
import threading
import time
from collections import deque
from typing import Optional

import keyboard

from virtual_tcu.config.constants import Cfg
from virtual_tcu.config.store import ConfigStore
from virtual_tcu.core.mode import MODE_ORDER, Mode
from virtual_tcu.deps import WINSOUND_OK, winsound
from virtual_tcu.detectors.airtime import AirtimeDetector
from virtual_tcu.detectors.reverse_hold import ReverseHoldDetector
from virtual_tcu.detectors.yaw_transient import YawTransientDetector
from virtual_tcu.input.keyboard import VirtualKeyboard
from virtual_tcu.integrations.discord import DiscordRPC
from virtual_tcu.learning.drive_style import DriveStyleTracker
from virtual_tcu.learning.gear_ratio import GearRatioCalibrator
from virtual_tcu.learning.power_curve import PowerCurveDetector
from virtual_tcu.learning.rev_limiter import RevLimiterDetector
from virtual_tcu.state.graph_buffer import GraphBuffer
from virtual_tcu.state.session_stats import SessionStats
from virtual_tcu.state.shift_history import ShiftHistory
from virtual_tcu.state.watchdog import Watchdog
from virtual_tcu.storage.profiles import ProfileStore
from virtual_tcu.telemetry.logger import TelemetryLogger
from virtual_tcu.telemetry.model import Telemetry

class TCULogic:
    def __init__(
        self,
        kb: VirtualKeyboard,
        profiles: ProfileStore,
        config: ConfigStore,
        logger: TelemetryLogger,
    ):
        self._kb = kb
        self._profiles = profiles
        self._config = config
        self._logger = logger
        self._mode_lock = threading.Lock()
        try:
            self._mode = Mode(config.get("current_mode", "COMFORT"))
        except ValueError:
            self._mode = Mode.COMFORT
        self._last_auto_mode = self._mode if self._mode != Mode.MANUAL else Mode.COMFORT
        self._last_processed_mode = self._mode

        self._lock_until = 0.0
        self._no_upshift_until = 0.0
        self._shift_count = 0
        self._peak_rpm = 0.0
        self._peak_g = 0.0
        self._turbo_bar = 0.0

        self._brake_history = deque(maxlen=10)
        self._throttle_history = deque(maxlen=6)
        self._speed_history = deque(maxlen=20)
        self._brake_raw_history = deque(maxlen=10)
        self._throttle_raw_history = deque(maxlen=10)
        self._no_downshift_until = 0.0
        self._no_predictive_until = 0.0
        self._last_brake_time = 0.0
        self._last_hard_brake_time = 0.0
        self._last_downshift_time = 0.0
        self._last_packet_time = 0.0
        self._prev_gear = -1
        self._we_shifted = False

        self._reverse_lock_until = 0.0
        self._current_car_ord = 0

        self._reverse_hold = ReverseHoldDetector(kb)
        self._calibrator = GearRatioCalibrator()
        self._power_curve = PowerCurveDetector()
        self._airtime = AirtimeDetector()
        self._yaw_transient = YawTransientDetector()
        self._drive_style = DriveStyleTracker()
        self._rev_limiter = RevLimiterDetector()
        self._shift_history = ShiftHistory()
        self._session_stats = SessionStats()
        self._graph_buffer = GraphBuffer()
        self._watchdog = Watchdog()
        self._discord_rpc = DiscordRPC() if config.get("feat_discord_rpc") else None
        self._last_decision = {"rule": "", "reason": "", "blocked_by": None}

        self._tcu_state = "STANDBY"
        self._tcu_state_sub = ""
        self._attitude = "NEUTRAL"
        self._attitude_sub = ""
        self._shift_hint = ""
        self._grip_usage = 0.0
        self._g_lat = 0.0
        self._g_lon = 0.0

        self._launch_armed = False
        self._cornering_locked = False
        self._down_held = False
        self._up_held = False
        self._slip_streak = 0
        self._paddle_keys: tuple[str, str] = ("", "")
        if Cfg.REVERSE_HOLD_MS > 0:
            self._setup_paddle_listeners()

    def _setup_paddle_listeners(self):
        kb = self._kb
        down_key = kb.key_down
        up_key = kb.key_up

        if (down_key, up_key) == self._paddle_keys:
            return

        self._teardown_paddle_listeners()
        self._down_held = False
        self._up_held = False

        def on_down_press(_e):
            if not kb.is_self_press(down_key):
                self._down_held = True

        def on_down_release(_e):
            if not kb.is_self_press(down_key):
                self._down_held = False

        def on_up_press(_e):
            if not kb.is_self_press(up_key):
                self._up_held = True

        def on_up_release(_e):
            if not kb.is_self_press(up_key):
                self._up_held = False

        try:
            keyboard.on_press_key(down_key, on_down_press)
            keyboard.on_release_key(down_key, on_down_release)
            keyboard.on_press_key(up_key, on_up_press)
            keyboard.on_release_key(up_key, on_up_release)
            self._paddle_keys = (down_key, up_key)
        except Exception as e:
            print(f"[Paddle hooks] failed: {e}")

    def _teardown_paddle_listeners(self):
        down_key, up_key = self._paddle_keys
        for key in (down_key, up_key):
            if not key:
                continue
            try:
                keyboard.unhook_key(key)
            except Exception:
                pass
        self._paddle_keys = ("", "")

    def refresh_shift_keys(self):
        if Cfg.REVERSE_HOLD_MS > 0:
            self._setup_paddle_listeners()

    @property
    def mode(self) -> Mode:
        with self._mode_lock:
            return self._mode

    def set_mode(self, mode_name: str):
        try:
            new_mode = Mode(mode_name)
            with self._mode_lock:
                if new_mode == Mode.MANUAL and self._mode != Mode.MANUAL:
                    self._last_auto_mode = self._mode
                self._mode = new_mode
            self._config.set("current_mode", new_mode.value)
        except ValueError:
            pass

    def cycle_mode(self):
        with self._mode_lock:
            idx = MODE_ORDER.index(self._mode)
            new_mode = MODE_ORDER[(idx + 1) % len(MODE_ORDER)]
            if new_mode == Mode.MANUAL and self._mode != Mode.MANUAL:
                self._last_auto_mode = self._mode
            self._mode = new_mode
            new_value = self._mode.value
        self._config.set("current_mode", new_value)

    @property
    def shift_count(self) -> int:
        return self._shift_count

    def snapshot(self, td: Optional[Telemetry]) -> dict:
        if td is None:
            return {
                "gear": -1,
                "speed_kmh": 0,
                "rpm": 0,
                "rpm_max": 0,
                "rpm_pct": 0,
                "throttle": 0,
                "brake": 0,
                "tcu_state": "OFFLINE",
                "tcu_state_sub": "no telemetry",
                "power_kw": 0,
                "torque_nm": 0,
                "turbo_bar": 0,
                "drivetrain": "—",
                "attitude": "NEUTRAL",
                "attitude_sub": "",
                "g_lat": 0,
                "g_lon": 0,
                "grip_usage": 0,
                "shift_hint": "",
                "peak_rpm": self._peak_rpm,
                "peak_g": self._peak_g,
                "calibrated": False,
                "log_status": self._logger.status,
                "power_curve_learned": False,
                "shift_history": [],
                "session_stats": self._session_stats.snapshot(),
                "watchdog_stuck": self._watchdog.check(),
                "drive_style_index": 0.0,
                "drive_style_regime": "CRUISE",
                "airborne": False,
                "yaw_transient": False,
                "peak_power_rpm_pct": None,
                "peak_torque_rpm_pct": None,
            }
        return {
            "gear": td.gear,
            "speed_kmh": td.speed_kmh,
            "rpm": td.current_rpm,
            "rpm_max": td.engine_max_rpm,
            "rpm_pct": td.rpm_pct,
            "throttle": td.throttle,
            "brake": td.brake,
            "tcu_state": self._tcu_state,
            "tcu_state_sub": self._tcu_state_sub,
            "power_kw": td.power_w / 1000.0,
            "torque_nm": td.torque_nm,
            "turbo_bar": self._turbo_bar,
            "drivetrain": td.drivetrain_name,
            "attitude": self._attitude,
            "attitude_sub": self._attitude_sub,
            "g_lat": self._g_lat,
            "g_lon": self._g_lon,
            "grip_usage": self._grip_usage,
            "shift_hint": self._shift_hint,
            "peak_rpm": self._peak_rpm,
            "peak_g": self._peak_g,
            "calibrated": self._calibrator.has_data(td.car_ordinal),
            "power_curve_learned": self._power_curve.has_data(td.car_ordinal),
            "log_status": self._logger.status,
            "shift_history": self._shift_history.snapshot(),
            "session_stats": self._session_stats.snapshot(),
            "watchdog_stuck": self._watchdog.check(),
            "car_ordinal": td.car_ordinal,
            "drive_style_index": round(self._drive_style.index, 2),
            "drive_style_regime": self._drive_style.regime,
            "airborne": self._airtime.is_airborne,
            "yaw_transient": self._yaw_transient.is_blocking,
            "peak_power_rpm_pct": self._power_curve.peak_power_rpm(td.car_ordinal),
            "peak_torque_rpm_pct": self._power_curve.peak_torque_rpm(td.car_ordinal),
        }

    def snapshot_graph(self) -> list:
        return self._graph_buffer.snapshot()

    def process(self, td: Telemetry, raw_packet: Optional[bytes] = None):
        now = time.time()

        if self._last_packet_time > 0.0 and (now - self._last_packet_time) > 0.8:
            self._prev_gear = td.gear
            self._no_downshift_until = 0.0
            self._no_upshift_until = 0.0
            self._lock_until = 0.0
            self._no_predictive_until = 0.0
            self._reverse_lock_until = 0.0
            self._launch_armed = False
            self._slip_streak = 0
            self._last_hard_brake_time = 0.0
            self._brake_history.clear()
            self._throttle_history.clear()
            self._speed_history.clear()
            self._brake_raw_history.clear()
            self._throttle_raw_history.clear()
            self._tcu_state = "RESUMING"
            self._tcu_state_sub = "from menu/pause"
        self._last_packet_time = now

        if td.is_shifting:
            self._tcu_state = "SHIFTING"
            self._tcu_state_sub = "Forza mid-shift"
            return

        if td.gear != self._prev_gear and td.gear > 0 and self._prev_gear > 0:
            if not self._we_shifted:
                airborne = (
                    self._config.get("feat_airtime_lock") and self._airtime.is_airborne
                )
                if td.brake < 0.30 and not airborne:
                    self._no_downshift_until = max(self._no_downshift_until, now + 0.8)
                if not airborne:
                    self._no_upshift_until = max(self._no_upshift_until, now + 0.5)
        self._prev_gear = td.gear
        self._we_shifted = False

        self._brake_history.append(td.brake)
        self._throttle_history.append(td.throttle)
        self._speed_history.append(td.speed_kmh)
        self._brake_raw_history.append(td.brake)
        self._throttle_raw_history.append(td.throttle)
        td.accel_raw = int(
            (sum(self._throttle_history) / len(self._throttle_history)) * 255
        )
        td.brake_raw = int((sum(self._brake_history) / len(self._brake_history)) * 255)

        if td.brake > 0.15:
            self._last_brake_time = now
        if td.brake > 0.50:
            self._last_hard_brake_time = now

        if td.current_rpm > self._peak_rpm:
            self._peak_rpm = td.current_rpm

        self._g_lat = td.accel_x / 9.81
        self._g_lon = td.accel_z / 9.81
        g_total = (self._g_lat**2 + self._g_lon**2) ** 0.5
        if g_total > self._peak_g:
            self._peak_g = g_total

        self._update_turbo(td)
        self._update_attitude(td)
        self._calibrator.observe(td)

        # Learn the real rev limiter and correct engine_max_rpm in place.
        # Forza's nominal value is often well above the actual fuel cut;
        # correcting it here means power curve, modes, target gear and the
        # over-rev guard all use the true cutoff with no other changes.
        self._rev_limiter.observe(td, self._last_downshift_time, now)
        real_redline = self._rev_limiter.effective_redline(td)
        if (real_redline is not None
                and td.engine_max_rpm * 0.5 < real_redline <= td.engine_max_rpm):
            td.engine_max_rpm = real_redline

        if self._config.get("feat_power_curve"):
            self._power_curve.observe(td)
        if self._config.get("feat_airtime_lock"):
            self._airtime.update(td)
        if self._config.get("feat_transient_lock"):
            self._yaw_transient.update(td, now)
        if self._config.get("feat_drive_style"):
            self._drive_style.update(td, self._g_lat, now)

        self._session_stats.update_peaks(
            td, self._g_lat, self._g_lon, td.power_w / 1000.0
        )
        self._graph_buffer.push(td)
        self._watchdog.heartbeat()
        if self._discord_rpc is not None and self._config.get("feat_discord_rpc"):
            self._discord_rpc.update(self.mode.value, self._shift_count, td.speed_kmh)

        if self._config.get("feat_reverse_hold"):
            result = self._reverse_hold.update(td, self._down_held, self._up_held, now)
            if result == "ENGAGED_REVERSE":
                self._tcu_state = "REVERSE (held)"
                self._tcu_state_sub = "user engaged R"

        is_reverse_now = (td.gear == 0) or (td.vel_z < -1.5 and td.gear <= 1)
        if is_reverse_now:
            self._tcu_state = "REVERSE"
            self._tcu_state_sub = "TCU passive"
            self._reverse_lock_until = now + 2.0
            return
        if now < self._reverse_lock_until:
            self._tcu_state = "REVERSE"
            self._tcu_state_sub = "exiting R..."
            return

        if td.car_ordinal > 0 and td.car_ordinal != self._current_car_ord:
            self._current_car_ord = td.car_ordinal
            self._peak_rpm = 0.0
            self._peak_g = 0.0

        current_mode = self.mode
        if current_mode != self._last_processed_mode:
            self._last_processed_mode = current_mode
            self._launch_armed = False
            self._no_upshift_until = 0.0

        if self.mode == Mode.MANUAL:
            self._tcu_state = "MANUAL"
            self._tcu_state_sub = "TCU off"
            if self._config.get("feat_shift_advisor"):
                self._compute_shift_advisor(td)
            return
        self._shift_hint = ""

        if self._config.get("feat_launch_control") and self._launch_control(td, now):
            return

        if now < self._lock_until:
            if td.brake > 0.45 and (self._lock_until - now) > 0.20:
                self._lock_until = now + 0.20
            else:
                self._tcu_state = "POST-SHIFT"
                self._tcu_state_sub = "stabilizing"
                return

        min_sensible_speed = self._min_sensible_speed_for_gear(td)
        if td.gear >= 2 and td.speed_kmh < min_sensible_speed and td.rpm_pct < 0.40:
            self._tcu_state = "GEAR MISMATCH"
            self._tcu_state_sub = f"too high for {td.speed_kmh:.0f} km/h"
            self._no_downshift_until = 0.0
            self._shift_down(td, 350, "MISMATCH", f"{td.gear}→{td.gear - 1}")
            return

        if td.speed_kmh < Cfg.MIN_SPEED_KMH:
            self._tcu_state = "STANDSTILL"
            self._tcu_state_sub = ""
            if td.gear >= 2 and td.speed_kmh < 10.0:
                self._shift_down(td, 600, "STANDSTILL", f"{td.gear}→{td.gear - 1}")
            return

        self._cornering_locked = False
        cornering_thr = self._config.get("cornering_yaw", 22) / 100.0
        if (
            self._config.get("feat_cornering_lock")
            and abs(td.ang_vel_z) > cornering_thr
        ):
            self._cornering_locked = True
            self._tcu_state = "CORNERING"
            self._tcu_state_sub = "upshift locked"

        m = self.mode
        if m == Mode.COMFORT:
            self._mode_comfort(td, now)
        elif m == Mode.DYNAMIC:
            self._mode_dynamic(td, now)
        elif m == Mode.RACE:
            self._mode_race(td, now)
        elif m == Mode.DRIFT:
            self._mode_drift(td, now)
        elif m == Mode.OFFROAD:
            self._mode_offroad(td, now)

    def _shift_up(self, td: Telemetry, lock_ms: int, state: str, sub: str = "") -> bool:
        if td.gear >= 10:
            return False
        if self._cornering_locked:
            return False
        if td.gear <= 2:
            lock_ms = max(lock_ms, Cfg.LOW_GEAR_LOCK_MS)
        self._tcu_state = state
        self._tcu_state_sub = sub
        now = time.time()
        self._lock_until = now + (lock_ms / 1000.0)
        self._no_upshift_until = max(self._no_upshift_until, self._lock_until)
        self._no_downshift_until = max(self._no_downshift_until, now + 1.0)
        self._we_shifted = True
        self._shift_count += 1
        self._kb.shift_up()
        self._logger.mark_event()
        self._shift_history.record("UP", td, reason=state, rule=self.mode.value)
        self._session_stats.record_shift("UP", state)
        if WINSOUND_OK and self._config.get("feat_sound_beep"):
            threading.Thread(
                target=lambda: winsound.Beep(3000, 40), daemon=True
            ).start()
        return True

    def _shift_down(
        self, td: Telemetry, lock_ms: int, state: str, sub: str = ""
    ) -> bool:
        if td.gear <= 1:
            return False
        now = time.time()
        if now < self._no_downshift_until:
            return False
        projected = self._calibrator.project_rpm_after_shift(td, td.gear - 1)
        if projected is None:
            projected = td.current_rpm * (td.gear / max(td.gear - 1, 1))
        if projected > td.engine_max_rpm * Cfg.OVER_REV_LIMIT:
            self._tcu_state = "OVER-REV BLOCKED"
            return False
        self._tcu_state = state
        self._tcu_state_sub = sub
        self._lock_until = now + (lock_ms / 1000.0)

        if state in ("BRAKE DOWN", "MISMATCH", "ENGINE BRAKE") or td.brake > 0.45:
            cascade_lock = 0.30
        elif state in ("KICKDOWN", "PREDICTIVE", "TORQUE DOWN", "BAND DOWN"):
            cascade_lock = 0.70
        elif state in ("ANTI-STALL", "STANDSTILL", "COAST DOWN", "DRIFT HOLD"):
            cascade_lock = 0.60
        else:
            cascade_lock = 0.90
        self._no_downshift_until = now + cascade_lock

        self._we_shifted = True
        self._shift_count += 1
        self._last_downshift_time = now
        self._kb.shift_down()
        self._logger.mark_event()
        self._shift_history.record("DOWN", td, reason=state, rule=self.mode.value)
        self._session_stats.record_shift("DOWN", state)
        if WINSOUND_OK and self._config.get("feat_sound_beep"):
            threading.Thread(
                target=lambda: winsound.Beep(1500, 50), daemon=True
            ).start()
        return True

    def _shift_down_double(self, td: Telemetry, lock_ms: int, target: int) -> bool:
        """Skip-gear: two Q presses with 60ms gap. For panic braking where
        the single-step cascade (300ms × N) is too slow."""
        if td.gear <= 2:
            return False
        now = time.time()
        if now < self._no_downshift_until:
            return False
        projected = self._calibrator.project_rpm_after_shift(td, td.gear - 2)
        if projected is None:
            projected = td.current_rpm * (td.gear / max(td.gear - 2, 1))
        if projected > td.engine_max_rpm * Cfg.OVER_REV_LIMIT:
            return False
        self._tcu_state = "BRAKE DOWN"
        self._tcu_state_sub = f"skip →{target}"
        self._lock_until = now + (lock_ms / 1000.0)
        self._no_downshift_until = now + 0.30
        self._we_shifted = True
        self._shift_count += 2
        self._last_downshift_time = now
        self._kb.shift_down_double()
        self._logger.mark_event()
        self._shift_history.record("DOWN", td, reason="SKIP DOWN",
                                   rule=self.mode.value)
        self._session_stats.record_shift("DOWN", "BRAKE DOWN")
        self._session_stats.record_shift("DOWN", "BRAKE DOWN")
        if WINSOUND_OK and self._config.get("feat_sound_beep"):
            threading.Thread(
                target=lambda: winsound.Beep(1500, 50), daemon=True
            ).start()
        return True

    @staticmethod
    def _curve(throttle: float, low: float, mid: float, high: float) -> float:
        if throttle <= 0.50:
            t = throttle / 0.50
            return low + (mid - low) * t
        t = (throttle - 0.50) / 0.50
        return mid + (high - mid) * t

    def _speed_stable(self, delta_kmh: float = 3.0) -> bool:
        if len(self._speed_history) < 15:
            return False
        return (max(self._speed_history) - min(self._speed_history)) < delta_kmh

    def _kickdown_pedal_threshold(self, td: Telemetry, base: float) -> float:
        if not self._config.get("feat_drivetrain_aware"):
            return base
        if td.drivetrain == 0:
            return min(0.95, base + 0.08)
        elif td.drivetrain == 2:
            return max(0.40, base - 0.05)
        return base

    def _brake_is_spike(self) -> bool:
        if len(self._brake_raw_history) < 8:
            return False
        recent = list(self._brake_raw_history)
        old = sum(recent[:4]) / 4
        new = sum(recent[-4:]) / 4
        return (new - old) > Cfg.BRAKE_SPIKE_DELTA

    def _throttle_ramp_up(self) -> float:
        if len(self._throttle_raw_history) < 9:
            return 0.0
        recent = list(self._throttle_raw_history)
        old = sum(recent[:3]) / 3
        new = sum(recent[-3:]) / 3
        return max(0.0, new - old)

    def _should_brake_downshift(self, td: Telemetry, base_thr: float) -> bool:
        if td.brake < base_thr:
            return False
        if not self._config.get("feat_brake_curve"):
            return True
        if self._brake_is_spike():
            return True
        if len(self._brake_raw_history) >= 6 and td.brake > 0.55:
            recent = list(self._brake_raw_history)[-6:]
            if min(recent) > 0.45:
                return True
        return False

    def _wheelspin_upshift_now(self, td: Telemetry) -> bool:
        if not self._config.get("feat_drivetrain_aware"):
            return False
        if td.drivetrain == 0:
            return False
        if td.gear < 1 or td.gear > 3:
            self._slip_streak = 0
            return False
        if td.throttle < 0.40:
            self._slip_streak = 0
            return False
        if td.rear_slip > 1.2:
            self._slip_streak += 1
            return self._slip_streak >= 3
        else:
            self._slip_streak = 0
            return False

    def _should_engine_brake(self, td: Telemetry) -> bool:
        if not self._config.get("feat_engine_brake"):
            return False
        if td.throttle > 0.05 or td.brake > 0.05:
            return False
        if td.gear <= 2 or td.speed_kmh < 40.0:
            return False
        if len(self._speed_history) < 15:
            return False
        old_speed = sum(list(self._speed_history)[:5]) / 5
        new_speed = sum(list(self._speed_history)[-5:]) / 5
        return (new_speed - old_speed) > 2.0

    def _on_climb(self, td: Telemetry) -> bool:
        """Climb detection by physical evidence: throttle on but speed flat
        or dropping. Gravity opposes forward motion uphill; we observe the
        result without needing pitch data from telemetry."""
        if td.throttle < 0.30 or td.brake > 0.05 or td.gear <= 1:
            return False
        if len(self._speed_history) < 15:
            return False
        recent = list(self._speed_history)
        old_speed = sum(recent[:5]) / 5
        new_speed = sum(recent[-5:]) / 5
        return (new_speed - old_speed) < -0.5

    def _min_sensible_speed_for_gear(self, td: Telemetry) -> float:
        ratios = self._calibrator.get_ratios(td.car_ordinal)
        if td.gear in ratios:
            ratio_rpm_per_kmh = ratios[td.gear]
            if ratio_rpm_per_kmh > 0:
                target_rpm = td.engine_max_rpm * 0.25
                return target_rpm / ratio_rpm_per_kmh
        if td.gear <= 1:
            return 0.0
        return max(0.0, (td.gear - 2) * 20 + 15)

    def _turbo_lag_block_upshift(self, td: Telemetry) -> bool:
        if not self._config.get("feat_turbo_compensate"):
            return False
        if td.boost_raw < 0.3 or td.throttle < 0.50:
            return False
        # At high RPM the turbo is fully spooled — never block
        if td.rpm_pct > 0.85:
            return False
        if self._turbo_bar < td.boost_raw * 0.7:
            return True
        return False

    def _update_turbo(self, td: Telemetry):
        if 0.01 < td.boost_raw < 5.0:
            target = min(td.boost_raw, 1.8)
        else:
            target = td.throttle * td.rpm_pct * 1.8
        dt = 1.0 / 60.0
        if target > self._turbo_bar:
            self._turbo_bar += 3.5 * dt * (target - self._turbo_bar)
        else:
            self._turbo_bar -= 4.2 * dt * (self._turbo_bar - target)
        self._turbo_bar = max(0.0, min(self._turbo_bar, 1.8))

    def _update_attitude(self, td: Telemetry):
        speed = td.speed_effective_ms
        if speed < 5.0:
            self._attitude = "NEUTRAL"
            self._attitude_sub = "low speed"
            self._grip_usage = 0.0
            return
        lat_g = abs(self._g_lat)
        self._grip_usage = min(1.0, lat_g / 1.2)
        yaw_abs = abs(td.ang_vel_z)
        if lat_g < 0.3 and yaw_abs < 0.1:
            self._attitude = "NEUTRAL"
            self._attitude_sub = "straight or gentle"
        elif lat_g > 1.0 and yaw_abs > 0.5:
            self._attitude = "OVER"
            self._attitude_sub = "oversteering"
        elif lat_g > 0.6 and yaw_abs < 0.2:
            self._attitude = "UNDER"
            self._attitude_sub = "understeering"
        else:
            self._attitude = "NEUTRAL"
            self._attitude_sub = "grip ok"

    def _compute_shift_advisor(self, td: Telemetry):
        thr = td.throttle
        base_mode = self._last_auto_mode

        if base_mode == Mode.RACE:
            up_pct = self._power_curve.optimal_upshift_rpm(
                td, fallback=self._config.get("race_up_wot", 94) / 100, offset=0.03
            )
        elif base_mode == Mode.DYNAMIC:
            up_pct = self._power_curve.optimal_upshift_rpm(
                td, fallback=self._config.get("dynamic_up_wot", 82) / 100, offset=0.05
            )
        elif base_mode == Mode.OFFROAD:
            up_pct = self._power_curve.optimal_upshift_rpm(
                td, fallback=self._config.get("offroad_up_wot", 90) / 100, offset=0.07
            )
        elif base_mode == Mode.DRIFT:
            up_pct = self._config.get("drift_up", 92) / 100
        else:
            up_pct = self._curve(
                thr,
                self._config.get("comfort_up_idle", 40) / 100,
                self._config.get("comfort_up_mid", 58) / 100,
                self._config.get("comfort_up_wot", 82) / 100,
            )

        if td.rpm_pct >= up_pct and td.speed_kmh > Cfg.MIN_SPEED_KMH:
            self._shift_hint = f"↑ UP to {td.gear + 1}"
        elif td.rpm_pct < 0.30 and td.gear > 2 and thr > 0.30:
            self._shift_hint = f"↓ DOWN to {td.gear - 1}"
        elif td.brake > 0.50 and td.rpm_pct < 0.40 and td.gear > 1:
            self._shift_hint = f"↓ DOWN to {td.gear - 1} (brake)"
        else:
            self._shift_hint = ""

    def _launch_control(self, td: Telemetry, now: float) -> bool:
        is_stationary = td.speed_effective_ms < 3.0
        target_rpm = self._config.get("launch_rpm", 4500)

        if is_stationary and td.gear <= 1 and td.brake > 0.30 and td.throttle > 0.70:
            if not self._launch_armed:
                self._launch_armed = True
                self._no_upshift_until = now + 999
            self._tcu_state = "LAUNCH ARMED"
            self._tcu_state_sub = "release brake — hold throttle"
            return True

        if (
            self._launch_armed
            and is_stationary
            and td.brake < 0.10
            and td.throttle > 0.70
        ):
            self._launch_armed = False
            self._no_upshift_until = 0.0
            self._tcu_state = "LAUNCHING !"
            self._tcu_state_sub = "full send"
            self._lock_until = now + 0.3
            return True

        if self._launch_armed and (td.throttle < 0.40 or td.speed_kmh > 5.0):
            self._launch_armed = False
            self._no_upshift_until = 0.0
        return False

    def _blocked_by_transient(self) -> Optional[str]:
        if self._config.get("feat_airtime_lock") and self._airtime.is_airborne:
            return "AIRBORNE"
        if self._config.get("feat_transient_lock") and self._yaw_transient.is_blocking:
            return "CORRECTING"
        return None

    def _target_gear_for_braking(
        self, td: Telemetry, speed_override: Optional[float] = None
    ) -> Optional[int]:
        car_ratios = self._calibrator.get_ratios(td.car_ordinal)
        if not car_ratios:
            return None
        speed = speed_override if speed_override is not None else td.speed_kmh
        if speed < 10.0:
            return 1

        peak_torque = self._power_curve.peak_torque_rpm(td.car_ordinal)
        peak_power = self._power_curve.peak_power_rpm(td.car_ordinal)
        if peak_torque is None or peak_power is None:
            target_rpm = td.engine_max_rpm * 0.70
        else:
            # Defensive: ensure power peak is at or above torque peak.
            # On flat-torque engines (electrics, some diesels) noise can
            # invert these momentarily.
            peak_power = max(peak_power, peak_torque)
            target_pct = peak_torque + (peak_power - peak_torque) * 0.6
            target_rpm = td.engine_max_rpm * target_pct

        best_gear = td.gear
        best_diff = float("inf")
        for gear, ratio in car_ratios.items():
            if gear < 1 or gear > 10:
                continue
            rpm_at_gear = ratio * speed
            if rpm_at_gear > td.engine_max_rpm * 0.95:
                continue
            diff = abs(rpm_at_gear - target_rpm)
            if diff < best_diff:
                best_diff = diff
                best_gear = gear
        return min(best_gear, td.gear)

    def _is_spinning_not_traction(self, td: Telemetry) -> bool:
        if td.rear_slip < 1.2:
            return False
        if td.rpm_pct < 0.65:
            return False
        if len(self._speed_history) < 10:
            return False
        recent = list(self._speed_history)[-10:]
        old = sum(recent[:3]) / 3
        new = sum(recent[-3:]) / 3
        return (new - old) < 0.5

    def _track_brake_down(
        self, td: Telemetry, now: float, brake_thr: float, lock_ms: int = 250
    ) -> bool:
        if not self._should_brake_downshift(td, brake_thr):
            return False
        if td.gear <= 1 or td.speed_kmh <= 25.0:
            return False
        # Project exit speed: under hard braking we keep slowing, so aim
        # the target gear at where we'll BE, not where we are. This makes
        # the braking phase finish all the downshifts before the throttle
        # is reapplied — no leftover downshift on corner exit.
        brake_margin = 0.20 * min(1.0, td.brake / 0.80)
        projected_speed = td.speed_kmh * (1.0 - brake_margin)
        target = self._target_gear_for_braking(td, speed_override=projected_speed)
        if target is not None and target >= td.gear:
            # Target says current gear is fine even projected forward, but
            # if RPM is dropping into lugging while braking hard, downshift.
            if not (td.rpm_pct < 0.50 and td.brake > 0.70):
                return False
        # Skip-gear in panic braking: target 3+ below AND brake > 80% AND gear >= 4
        if (target is not None and target <= td.gear - 3
                and td.brake > 0.80 and td.gear >= 4):
            if self._shift_down_double(td, lock_ms, target):
                self._no_upshift_until = now + 0.5
                return True
        if target is not None and target < td.gear - 1:
            sub = f"→{target}"
        elif target is None:
            sub = "no ratio data"
        else:
            sub = "panic brake"
        if not self._shift_down(td, lock_ms, "BRAKE DOWN", sub):
            return False
        self._no_upshift_until = now + 0.5
        return True

    def _track_out_of_band_kickdown(
        self, td: Telemetry, now: float, climb_only: bool = False
    ) -> bool:
        climbing = self._on_climb(td)
        # climb_only mode (Race / Dynamic-SPORT): only act on climbs, where
        # gravity kills RPM and there was no braking phase to pre-select
        # the gear. On the flat the braking phase already did the work.
        if climb_only and not climbing:
            return False
        # No hard brake recently → fast/light corner, require higher
        # throttle before kickdown. Avoids dropping a gear after a brief
        # brake-and-go that doesn't need it.
        had_hard_brake = (now - self._last_hard_brake_time) < 2.0
        throttle_threshold = 0.50 if had_hard_brake else 0.60
        if td.throttle < throttle_threshold:
            return False
        if td.gear <= 2:
            return False
        peak_torque = self._power_curve.peak_torque_rpm(td.car_ordinal)
        threshold = peak_torque - 0.10 if peak_torque is not None else 0.55
        if climbing:
            threshold += 0.08
        if td.rpm_pct >= threshold:
            return False
        if not self._shift_down(
            td, 400, "BAND DOWN", "climb" if climbing else "out of band"
        ):
            return False
        self._no_upshift_until = now + 0.8
        return True

    def _track_upshift_in_band(
        self, td: Telemetry, now: float, offset: float, min_throttle: float = 0.05
    ) -> bool:
        if td.throttle < min_throttle:
            return False
        if td.brake > 0.05:
            return False
        if now < self._no_upshift_until:
            return False
        if self._turbo_lag_block_upshift(td):
            return False
        if td.speed_kmh <= Cfg.MIN_SPEED_KMH:
            return False
        fallback = self._config.get("race_up_wot", 94) / 100
        target_pct = self._power_curve.optimal_upshift_rpm(
            td, fallback=fallback, offset=offset
        )
        if td.rpm_pct < target_pct:
            return False
        return self._shift_up(td, 300, "UPSHIFT", "in band")

    # ─── COMFORT ──────────────────────────────────────────────────────

    def _mode_comfort(self, td: Telemetry, now: float):
        thr = td.throttle
        brake_thr = self._config.get("brake_thr", 35) / 100
        kd_pedal = self._config.get("kickdown_pedal", 78) / 100
        kd_rpm = self._config.get("kickdown_rpm", 50) / 100
        coast_rpm = self._config.get("coast_down_rpm", 28) / 100

        if (
            td.current_rpm < Cfg.ANTI_STALL_RPM
            and td.gear > 1
            and thr < 0.10
            and td.speed_kmh < 20.0
        ):
            self._shift_down(td, 350, "ANTI-STALL", "engine save")
            return

        if (
            self._should_brake_downshift(td, brake_thr)
            and td.gear > 1
            and td.speed_kmh > 35.0
        ):
            self._shift_down(
                td,
                300,
                "BRAKE DOWN",
                "panic brake" if self._config.get("feat_brake_curve") else "",
            )
            self._no_upshift_until = now + 1.0
            return

        ramp = self._throttle_ramp_up()
        if (
            ramp > 0.50
            and thr > 0.80
            and td.rpm_pct < 0.65
            and td.gear > 2
            and td.speed_kmh > 40.0
            and now >= self._no_predictive_until
        ):
            self._shift_down(td, 450, "PREDICTIVE", "hard accel")
            self._no_upshift_until = now + 1.2
            return

        kd_thr = self._kickdown_pedal_threshold(td, kd_pedal)
        if thr >= kd_thr and td.rpm_pct < kd_rpm and td.gear > 2:
            self._shift_down(td, 500, "KICKDOWN", "demand power")
            self._no_upshift_until = now + 1.5
            return

        if self._wheelspin_upshift_now(td) and td.speed_kmh > 15.0:
            self._shift_up(td, 400, "WHEELSPIN", "traction save")
            return

        if self._should_engine_brake(td):
            self._shift_down(td, 600, "ENGINE BRAKE", "descent")
            self._no_upshift_until = now + 2.0
            return

        if (
            thr > 0.20
            and td.brake < 0.05
            and now >= self._no_upshift_until
            and not self._turbo_lag_block_upshift(td)
        ):
            up_pct = self._curve(
                thr,
                self._config.get("comfort_up_idle", 40) / 100,
                self._config.get("comfort_up_mid", 58) / 100,
                self._config.get("comfort_up_wot", 82) / 100,
            )
            if td.rpm_pct >= up_pct:
                self._shift_up(td, 350, "UPSHIFT", "accelerating")
                return

        if (
            thr > 0.05
            and thr < 0.55
            and td.brake < 0.05
            and td.gear >= 3
            and self._speed_stable(3.0)
            and td.rpm_pct > 0.30
            and abs(td.ang_vel_z) < 0.15
        ):
            self._shift_up(td, 2500, "CRUISE EFF", "saving fuel")
            return

        if (
            thr < 0.05
            and td.brake < 0.05
            and td.rpm_pct < coast_rpm
            and td.gear > 1
            and td.speed_kmh > 50.0
            and abs(td.ang_vel_z) < 0.20
        ):
            self._shift_down(td, 400, "COAST DOWN", "engine brake")
            return

        self._tcu_state = "CRUISING"
        self._tcu_state_sub = ""

    # ─── RACE ─────────────────────────────────────────────────────────

    def _mode_race(self, td: Telemetry, now: float):
        thr = td.throttle
        brake_thr = self._config.get("brake_thr", 35) / 100 * 0.6

        if (
            td.current_rpm < Cfg.ANTI_STALL_RPM
            and td.gear > 1
            and thr < 0.10
            and td.speed_kmh < 20.0
        ):
            self._shift_down(td, 350, "ANTI-STALL", "engine save")
            return

        blocker = self._blocked_by_transient()
        if blocker is not None:
            self._tcu_state = blocker
            self._tcu_state_sub = "holding decisions"
            return

        if self._track_brake_down(td, now, brake_thr, lock_ms=250):
            return

        if self._wheelspin_upshift_now(td) and td.speed_kmh > 15.0:
            self._shift_up(td, 400, "WHEELSPIN", "traction save")
            return

        # Downshift while accelerating ONLY on climbs — gravity kills RPM
        # and there was no braking phase to pre-select the gear. On the
        # flat the braking phase already finished all the downshifts.
        if self._track_out_of_band_kickdown(td, now, climb_only=True):
            return

        if self._track_upshift_in_band(td, now, offset=0.03):
            return

        self._tcu_state = "RACE"
        self._tcu_state_sub = "in band"

    # ─── DYNAMIC ──────────────────────────────────────────────────────

    def _mode_dynamic(self, td: Telemetry, now: float):
        if (
            td.current_rpm < Cfg.ANTI_STALL_RPM
            and td.gear > 1
            and td.throttle < 0.10
            and td.speed_kmh < 20.0
        ):
            self._shift_down(td, 350, "ANTI-STALL")
            return

        regime = self._drive_style.regime
        if regime == "SPORT":
            self._dynamic_sport(td, now)
        else:
            self._dynamic_cruise(td, now, adaptive=(regime == "ADAPTIVE"))

    def _dynamic_sport(self, td: Telemetry, now: float):
        brake_thr = self._config.get("brake_thr", 35) / 100 * 0.7

        blocker = self._blocked_by_transient()
        if blocker is not None:
            self._tcu_state = blocker
            self._tcu_state_sub = "sport — hold"
            return

        if self._track_brake_down(td, now, brake_thr, lock_ms=280):
            return
        if self._wheelspin_upshift_now(td) and td.speed_kmh > 15.0:
            self._shift_up(td, 400, "WHEELSPIN", "traction save")
            return
        # Climb-only downshift, same as Race.
        if self._track_out_of_band_kickdown(td, now, climb_only=True):
            return
        if self._track_upshift_in_band(td, now, offset=0.05):
            return

        self._tcu_state = "DYNAMIC"
        self._tcu_state_sub = "sport — in band"

    def _dynamic_cruise(self, td: Telemetry, now: float, adaptive: bool):
        thr = td.throttle
        brake_thr = self._config.get("brake_thr", 35) / 100 * 0.9
        kd_pedal = self._config.get("kickdown_pedal", 78) / 100
        kd_rpm = self._config.get("kickdown_rpm", 50) / 100

        if adaptive:
            blocker = self._blocked_by_transient()
            if blocker is not None:
                self._tcu_state = blocker
                self._tcu_state_sub = "adaptive — hold"
                return

        if (
            self._should_brake_downshift(td, brake_thr)
            and td.gear > 1
            and td.speed_kmh > 30.0
        ):
            self._shift_down(td, 280, "BRAKE DOWN")
            self._no_upshift_until = now + 0.8
            return

        ramp = self._throttle_ramp_up()
        if (
            ramp > 0.40
            and thr > 0.70
            and td.rpm_pct < 0.70
            and td.gear > 1
            and td.speed_kmh > 30.0
            and now >= self._no_predictive_until
        ):
            self._shift_down(td, 400, "PREDICTIVE", "stomp")
            self._no_upshift_until = now + 1.0
            return

        kd_thr = self._kickdown_pedal_threshold(td, kd_pedal)
        if thr >= kd_thr and td.rpm_pct < kd_rpm and td.gear > 2:
            self._shift_down(td, 500, "KICKDOWN")
            self._no_upshift_until = now + 1.5
            return

        if self._wheelspin_upshift_now(td) and td.speed_kmh > 15.0:
            self._shift_up(td, 400, "WHEELSPIN", "traction save")
            return

        if self._should_engine_brake(td):
            self._shift_down(td, 500, "ENGINE BRAKE", "descent")
            self._no_upshift_until = now + 1.5
            return

        if (
            thr > 0.20
            and td.brake < 0.05
            and now >= self._no_upshift_until
            and not self._turbo_lag_block_upshift(td)
        ):
            up_pct = self._curve(
                thr,
                self._config.get("dynamic_up_idle", 42) / 100,
                self._config.get("dynamic_up_mid", 58) / 100,
                self._config.get("dynamic_up_wot", 82) / 100,
            )
            if td.rpm_pct >= up_pct:
                self._shift_up(td, 350, "UPSHIFT", "cruise")
                return

        if (
            not adaptive
            and thr < 0.05
            and td.brake < 0.05
            and td.rpm_pct < 0.28
            and td.gear > 1
            and td.speed_kmh > 50.0
            and abs(td.ang_vel_z) < 0.20
        ):
            self._shift_down(td, 400, "COAST DOWN")
            return

        self._tcu_state = "CRUISING"
        self._tcu_state_sub = "adaptive" if adaptive else "relaxed"

    # ─── DRIFT ────────────────────────────────────────────────────────

    def _mode_drift(self, td: Telemetry, now: float):
        if td.speed_kmh < 30.0:
            self._tcu_state = "DRIFT"
            self._tcu_state_sub = "low speed"
            return
        if td.rpm_pct < 0.20 and td.gear > 1:
            self._shift_down(td, 350, "DRIFT HOLD", "save engine")
            return
        if td.rpm_pct < self._config.get("drift_down", 65) / 100 and td.gear > 1:
            self._shift_down(td, 300, "DRIFT HOLD", "rpm low")
            return
        if td.rpm_pct >= self._config.get("drift_up", 92) / 100:
            self._shift_up(td, 300, "DRIFT HOLD", "limiter")
            return
        self._tcu_state = "DRIFT HOLD"
        self._tcu_state_sub = "in power band"

    # ─── OFFROAD ──────────────────────────────────────────────────────

    def _mode_offroad(self, td: Telemetry, now: float):
        thr = td.throttle
        brake_thr = self._config.get("brake_thr", 35) / 100

        if (
            td.current_rpm < Cfg.ANTI_STALL_RPM * 1.2
            and td.gear > 1
            and thr < 0.10
            and td.speed_kmh < 25.0
        ):
            self._shift_down(td, 400, "ANTI-STALL", "save engine")
            return

        blocker = self._blocked_by_transient()
        if blocker is not None:
            self._tcu_state = blocker
            self._tcu_state_sub = "offroad — hold"
            return

        if self._track_brake_down(td, now, brake_thr, lock_ms=300):
            return

        if (
            self._wheelspin_upshift_now(td)
            and td.speed_kmh > 15.0
            and not self._is_spinning_not_traction(td)
        ):
            self._shift_up(td, 400, "WHEELSPIN", "lose grip")
            return

        down_rpm = self._config.get("offroad_down_rpm", 55) / 100
        if thr >= 0.40 and td.rpm_pct < down_rpm and td.gear > 1 and td.speed_kmh > 8.0:
            self._shift_down(td, 450, "TORQUE DOWN", "climbing")
            self._no_upshift_until = now + 1.5
            return

        if self._track_out_of_band_kickdown(td, now):
            return

        if self._track_upshift_in_band(td, now, offset=0.07, min_throttle=0.20):
            return

        self._tcu_state = "OFFROAD"
        self._tcu_state_sub = "torque ready"

