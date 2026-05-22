import threading
import time
from typing import Set

from virtual_tcu.telemetry.model import Telemetry


class SessionStats:
    def __init__(self):
        self.start_time = time.time()
        self.upshifts = 0
        self.downshifts = 0
        self.kickdowns = 0
        self.brake_downs = 0
        self.predictives = 0
        self.launches = 0
        self.peak_rpm = 0.0
        self.peak_g_lat = 0.0
        self.peak_g_lon = 0.0
        self.peak_speed = 0.0
        self.peak_power_kw = 0.0
        self.throttle_avg_sum = 0.0
        self.throttle_avg_n = 0
        self.cars_driven: Set[int] = set()
        self._lock = threading.Lock()

    def record_shift(self, action: str, reason: str = ""):
        with self._lock:
            if action == "UP":
                self.upshifts += 1
            elif action == "DOWN":
                self.downshifts += 1
            if "KICKDOWN" in reason:
                self.kickdowns += 1
            elif "BRAKE" in reason:
                self.brake_downs += 1
            elif "PREDICTIVE" in reason:
                self.predictives += 1
            elif "LAUNCH" in reason:
                self.launches += 1

    def update_peaks(self, td: Telemetry, g_lat: float, g_lon: float, power_kw: float):
        with self._lock:
            if td.current_rpm > self.peak_rpm:
                self.peak_rpm = td.current_rpm
            if abs(g_lat) > self.peak_g_lat:
                self.peak_g_lat = abs(g_lat)
            if abs(g_lon) > self.peak_g_lon:
                self.peak_g_lon = abs(g_lon)
            if td.speed_kmh > self.peak_speed:
                self.peak_speed = td.speed_kmh
            if power_kw > self.peak_power_kw:
                self.peak_power_kw = power_kw
            self.throttle_avg_sum += td.throttle
            self.throttle_avg_n += 1
            if td.car_ordinal > 0:
                self.cars_driven.add(td.car_ordinal)

    def snapshot(self) -> dict:
        with self._lock:
            duration = time.time() - self.start_time
            avg_thr = (
                self.throttle_avg_sum / self.throttle_avg_n
                if self.throttle_avg_n
                else 0.0
            )
            return {
                "duration_s": duration,
                "upshifts": self.upshifts,
                "downshifts": self.downshifts,
                "kickdowns": self.kickdowns,
                "brake_downs": self.brake_downs,
                "predictives": self.predictives,
                "launches": self.launches,
                "peak_rpm": self.peak_rpm,
                "peak_g_lat": self.peak_g_lat,
                "peak_g_lon": self.peak_g_lon,
                "peak_speed": self.peak_speed,
                "peak_power_kw": self.peak_power_kw,
                "avg_throttle": avg_thr * 100,
                "cars_driven": len(self.cars_driven),
            }

