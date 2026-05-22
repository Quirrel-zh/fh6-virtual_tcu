import gzip
import struct
import threading
import time
from collections import deque
from pathlib import Path
from typing import Deque, Optional

from virtual_tcu.config.constants import Cfg
from virtual_tcu import paths

LOG_MAGIC = b"TCULOG01"


class TelemetryLogger:
    """Records UDP packets to gzip log. Modes: events (pre-event buffer
    + post-event tail), all (every packet). Auto-stops at LOG_MAX_MB."""

    def __init__(self):
        self._lock = threading.Lock()
        self._mode = "off"
        self._gz = None
        self._path: Optional[Path] = None
        self._start_time = 0.0
        self._packets_logged = 0
        self._bytes_written = 0
        self._buffer: Deque[tuple] = deque(maxlen=60)
        self._post_event_remaining = 0

    @property
    def is_recording(self) -> bool:
        return self._gz is not None

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def status(self) -> dict:
        return {
            "mode": self._mode,
            "recording": self.is_recording,
            "packets": self._packets_logged,
            "size_kb": self._bytes_written // 1024,
            "file": self._path.name if self._path else None,
        }

    def start(self, mode: str) -> bool:
        if self.is_recording:
            self.stop()
        if mode not in ("events", "all"):
            return False
        ts = time.strftime("%Y%m%d_%H%M%S")
        path = paths.log_dir() / f"{Cfg.LOG_FILE_PREFIX}_{ts}.bin.gz"
        with self._lock:
            try:
                gz = gzip.open(path, "wb", compresslevel=6)
                gz.write(LOG_MAGIC)
                self._gz = gz
                self._path = path
                self._mode = mode
                self._start_time = time.time()
                self._packets_logged = 0
                self._bytes_written = len(LOG_MAGIC)
                self._buffer.clear()
                self._post_event_remaining = 0
                return True
            except Exception as e:
                print(f"[Logger] start failed: {e}")
                self._gz = None
                return False

    def stop(self) -> Optional[str]:
        with self._lock:
            if self._gz is None:
                return None
            try:
                self._gz.close()
            except Exception:
                pass
            p = str(self._path) if self._path else None
            self._gz = None
            self._mode = "off"
            return p

    def mark_event(self):
        with self._lock:
            if self._gz is None or self._mode != "events":
                return
            for buf_ms, buf_raw in self._buffer:
                self._write_record_locked(buf_ms, buf_raw)
            self._buffer.clear()
            self._post_event_remaining = 30

    def write_packet(self, raw: bytes):
        with self._lock:
            if self._gz is None or not raw:
                return
            if self._bytes_written >= Cfg.LOG_MAX_MB * 1024 * 1024:
                pass
            else:
                rel_ms = int((time.time() - self._start_time) * 1000)
                if self._mode == "all":
                    self._write_record_locked(rel_ms, raw)
                    return
                self._buffer.append((rel_ms, raw))
                if self._post_event_remaining > 0:
                    self._write_record_locked(rel_ms, raw)
                    self._post_event_remaining -= 1
                return
        self.stop()

    def _write_record_locked(self, rel_ms: int, raw: bytes):
        try:
            header = struct.pack("<IH", rel_ms, len(raw))
            self._gz.write(header)
            self._gz.write(raw)
            self._bytes_written += 6 + len(raw)
            self._packets_logged += 1
        except Exception as e:
            print(f"[Logger] write error: {e}")
            try:
                self._gz.close()
            except:
                pass
            self._gz = None
            self._mode = "off"

