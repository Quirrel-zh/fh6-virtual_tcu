import argparse
import asyncio
import sys
import time
import webbrowser
import keyboard

from virtual_tcu import paths
from virtual_tcu.config.constants import Cfg
from virtual_tcu.config.web_bind import format_startup_urls, web_urls
from virtual_tcu.config.store import ConfigStore
from virtual_tcu.deps import AIOHTTP_OK
from virtual_tcu.input.keyboard import VirtualKeyboard
from virtual_tcu.logic.tcu import TCULogic
from virtual_tcu.storage.profiles import ProfileStore
from virtual_tcu.telemetry.logger import TelemetryLogger
from virtual_tcu.telemetry.receiver import TelemetryReceiver
from virtual_tcu.web.server import WebServer

# Marker the Electron shell waits for on stdout before showing the main window.
BACKEND_READY_MARKER = "[backend-ready]"


async def headless_loop():
    print("  [.] Running headless (no aiohttp). Press Ctrl+C to stop.")
    stop_event = asyncio.Event()
    await stop_event.wait()


async def main_async(receiver, tcu, config, logger, *, backend_only: bool = False):
    if not AIOHTTP_OK:
        await headless_loop()
        return

    server = WebServer(receiver, tcu, config, logger)
    await server.start()
    urls = format_startup_urls(config)
    print(f"  [OK] Web UI at {urls[0]}" + (f", {urls[1]}" if len(urls) > 1 else ""))
    url = web_urls(config)["local"]
    await asyncio.sleep(0.5)

    if backend_only:
        # Electron shell drives the UI; skip browser-open and last-run marker
        # so the standalone exe can be relaunched without flicker.
        print(BACKEND_READY_MARKER, flush=True)
    else:
        marker = paths.last_run_marker()
        should_open = True
        if marker.exists():
            try:
                if (time.time() - marker.stat().st_mtime) < 30:
                    should_open = False
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

    try:
        stop_event = asyncio.Event()
        await stop_event.wait()
    finally:
        await server.stop()


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
            logger.stop()
        else:
            logger.start("events")

    bindings = [
        (config.get("hotkey_cycle_mode", "f9"), "cycle_mode", lambda: tcu.cycle_mode()),
        (config.get("hotkey_toggle_log", "f8"), "toggle_log", toggle_log),
    ]

    for key, name, fn in bindings:
        if key:
            try:
                keyboard.add_hotkey(key, make_debounced(name, fn))
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

    parser = argparse.ArgumentParser(prog="virtual_tcu", add_help=True)
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="Run as a headless backend (no auto-open browser); used by the Electron shell.",
    )
    args, _unknown = parser.parse_known_args()

    banner()

    config = ConfigStore()
    profiles = ProfileStore()
    logger = TelemetryLogger()
    kb = VirtualKeyboard(config)
    tcu = TCULogic(kb, profiles, config, logger)
    setup_hotkeys(tcu, config, logger)

    receiver = TelemetryReceiver(logger, on_packet=tcu.process, config=config)
    if not receiver.start():
        from virtual_tcu.bootstrap import report_fatal
        report_fatal(
            f"UDP port {config.get('udp_port', Cfg.UDP_PORT)} bind failed. {receiver.error_msg}"
        )

    # AIOHTTP Windows Event Loop Exception Fix
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(
            main_async(receiver, tcu, config, logger, backend_only=args.backend_only)
        )
    except KeyboardInterrupt:
        print("\n  Shutting down...")
    finally:
        logger.stop()
        receiver.stop()
        kb.shutdown()
        tcu.shutdown()

if __name__ == "__main__":
    main()
