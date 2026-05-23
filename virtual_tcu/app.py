import asyncio
import sys
import time
import webbrowser

import keyboard

from virtual_tcu import paths
from virtual_tcu.config.constants import Cfg
from virtual_tcu.config.store import ConfigStore
from virtual_tcu.deps import AIOHTTP_OK
from virtual_tcu.input.keyboard import VirtualKeyboard
from virtual_tcu.logic.tcu import TCULogic
from virtual_tcu.storage.profiles import ProfileStore
from virtual_tcu.telemetry.logger import TelemetryLogger
from virtual_tcu.telemetry.receiver import TelemetryReceiver
from virtual_tcu.web.server import WebServer

async def headless_loop(receiver, tcu):
    print("  [.] Running headless (no aiohttp). Press Ctrl+C to stop.")
    last_packet_id = -1
    while True:
        await asyncio.sleep(1.0 / 60.0)
        td = receiver.latest()
        current_id = receiver.packets_total
        if td is not None and receiver.is_live and current_id != last_packet_id:
            tcu.process(td, receiver.latest_raw())
            last_packet_id = current_id


async def main_async(receiver, tcu, config, logger):
    if not AIOHTTP_OK:
        await headless_loop(receiver, tcu)
        return

    server = WebServer(receiver, tcu, config, logger)
    await server.start()
    url = f"http://{Cfg.WEB_HOST}:{Cfg.WEB_PORT}"
    print(f"  [OK] Web UI at {url}")
    await asyncio.sleep(0.5)
    marker = paths.last_run_marker()
    should_open = True
    if marker.exists():
        try:
            age = time.time() - marker.stat().st_mtime
            if age < 30:
                should_open = False
                print(
                    f"  [.] Skipping browser auto-open (recent restart, "
                    f"open {url} manually)"
                )
        except Exception:
            pass
    if should_open:
        try:
            webbrowser.open(url)
        except:
            pass
    try:
        marker.touch()
    except Exception:
        pass
    while True:
        await asyncio.sleep(3600)


def setup_hotkeys(tcu: TCULogic, config: ConfigStore, logger: TelemetryLogger):
    last_press = {}

    def make_debounced(name, fn):
        def wrapped():
            now = time.time()
            if (now - last_press.get(name, 0.0)) < 0.4:
                return
            last_press[name] = now
            try:
                fn()
            except Exception as e:
                print(f"  [hotkey {name}] {e}")

        return wrapped

    def toggle_log():
        if logger.is_recording:
            p = logger.stop()
            print(f"  [Log] stopped: {p}")
        else:
            logger.start("events")
            print(f"  [Log] started events mode")

    bindings = [
        (config.get("hotkey_cycle_mode", "f9"), "cycle_mode", lambda: tcu.cycle_mode()),
        (config.get("hotkey_toggle_log", "f8"), "toggle_log", toggle_log),
    ]

    for key, name, fn in bindings:
        if not key:
            continue
        try:
            keyboard.add_hotkey(key, make_debounced(name, fn))
            print(f"  [OK] hotkey {key.upper()} → {name}")
        except Exception as e:
            print(f"  [!] hotkey {key} failed: {e}")


def banner():
    from virtual_tcu import __version__

    print("=" * 66)
    print(f"  VIRTUAL TCU v{__version__}  —  FH6")
    print("=" * 66)


def main():
    if sys.platform != "win32":
        print("[ERROR] Windows only.")
        sys.exit(1)

    banner()

    config = ConfigStore()
    print(f"  [OK] Config: {config.path}")

    profiles = ProfileStore()
    print(f"  [OK] Profiles: {len(profiles.data)} cars loaded ({profiles.path})")

    logger = TelemetryLogger()
    print(f"  [OK] Logger ready ({paths.log_dir()})")

    receiver = TelemetryReceiver(logger)
    if not receiver.start():
        from virtual_tcu.bootstrap import report_fatal

        report_fatal(
            f"UDP port {Cfg.UDP_PORT} bind failed: {receiver.error_msg}\n"
            "  Close other Virtual TCU / python instances, or change the port in config."
        )
    print(f"  [OK] UDP listening on 0.0.0.0:{Cfg.UDP_PORT}")

    kb = VirtualKeyboard(config)
    tcu = TCULogic(kb, profiles, config, logger)
    setup_hotkeys(tcu, config, logger)

    print("=" * 66)
    print(f"  Open: http://{Cfg.WEB_HOST}:{Cfg.WEB_PORT}")
    print("=" * 66)

    try:
        asyncio.run(main_async(receiver, tcu, config, logger))
    except KeyboardInterrupt:
        print("\n  Shutting down...")
    except OSError as e:
        from virtual_tcu.bootstrap import report_fatal

        report_fatal(
            f"Web UI port {Cfg.WEB_PORT} unavailable: {e}\n"
            "  Close other apps using this port (another Virtual TCU instance?).",
            exc=e,
        )
    except Exception as e:
        from virtual_tcu.bootstrap import report_fatal

        report_fatal("Unexpected error while running.", exc=e)
    finally:
        logger.stop()
        receiver.stop()
        if tcu._discord_rpc is not None:
            tcu._discord_rpc.close()


if __name__ == "__main__":
    main()
