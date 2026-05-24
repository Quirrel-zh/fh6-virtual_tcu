import socket
import select
import threading
import time
from typing import Optional

from virtual_tcu.config.constants import Cfg
from virtual_tcu.telemetry.logger import TelemetryLogger
from virtual_tcu.telemetry.model import Telemetry
from virtual_tcu.telemetry.parser import parse_fh6_packet


class TelemetryReceiver:
    def __init__(self, logger: TelemetryLogger, on_packet=None, config=None):
        self._sock: Optional[socket.socket] = None
        self._running = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._latest: Optional[Telemetry] = None
        self._latest_raw: Optional[bytes] = None
        self._lock = threading.Lock()
        self._logger = logger
        self.on_packet = on_packet
        self._config = config
        self.packets_total = 0
        self.last_recv_time = 0.0
        self.error_msg = ""
        self._bound_port = 0

    def _resolve_port(self) -> int:
        if self._config is not None:
            return int(self._config.get("udp_port", Cfg.UDP_PORT))
        return Cfg.UDP_PORT

    @property
    def bound_port(self) -> int:
        return self._bound_port

    def start(self) -> bool:
        if self._running.is_set():
            self.stop()

        port = self._resolve_port()
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Intentionally NOT setting SO_REUSEADDR: on Windows it acts like
            # SO_REUSEPORT for UDP, letting a second instance silently bind to
            # the same port while only one socket actually receives packets.
            # That produced confusing "disconnected in UI but auto-shift still
            # works" reports. Hard-fail instead so the user sees a real error.
            self._sock.bind((Cfg.UDP_IP, port))
        except OSError as e:
            self.error_msg = str(e)
            self._bound_port = 0
            return False

        self._bound_port = port
        self._running.set()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="UDP_Receiver")
        self._thread.start()
        print(f"  [OK] UDP telemetry on :{port}")
        return True

    def restart(self) -> bool:
        self.stop()
        return self.start()

    def stop(self):
        self._running.clear()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    def _loop(self):
        while self._running.is_set():
            try:
                if self._sock is None:
                    break

                ready = select.select([self._sock], [], [], 0.5)
                if not ready[0]:
                    continue

                raw, _ = self._sock.recvfrom(1024)
                td = parse_fh6_packet(raw)

                if td is not None:
                    now = time.time()
                    with self._lock:
                        self.packets_total += 1
                        self.last_recv_time = now
                        self._latest = td
                        self._latest_raw = raw

                    self._logger.write_packet(raw)
                    if self.on_packet:
                        self.on_packet(td, raw)

            except OSError:
                if not self._running.is_set():
                    break
                time.sleep(0.01)
            except Exception as e:
                print(f"[UDP] Error in receiver loop: {e}")
                time.sleep(0.01)

    def latest(self) -> Optional[Telemetry]:
        with self._lock:
            return self._latest

    def latest_raw(self) -> Optional[bytes]:
        with self._lock:
            return self._latest_raw

    @property
    def is_live(self) -> bool:
        with self._lock:
            return (time.time() - self.last_recv_time) < 2.5
