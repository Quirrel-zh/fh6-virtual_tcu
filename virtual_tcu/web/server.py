import asyncio
import json
import time
from pathlib import Path
from typing import Optional, Set

from virtual_tcu import paths
from virtual_tcu.config.constants import Cfg, DEFAULTS
from virtual_tcu.config.store import ConfigStore
from virtual_tcu.deps import AIOHTTP_OK, WSMsgType, web
from virtual_tcu.logic.tcu import TCULogic
from virtual_tcu.telemetry.logger import TelemetryLogger
from virtual_tcu.telemetry.receiver import TelemetryReceiver

_NO_UI_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Virtual TCU — Web UI unavailable</title>
</head>
<body>
  <h1>Web UI unavailable</h1>
  <p>Dashboard assets missing. Run UI build process.</p>
</body>
</html>
"""

def _dist_index() -> Optional[Path]:
    p = paths.web_dist_dir() / "index.html"
    return p if p.is_file() else None

def _dist_assets_dir() -> Optional[Path]:
    p = paths.web_dist_dir() / "assets"
    return p if p.is_dir() else None

class WebServer:
    def __init__(
        self,
        receiver: TelemetryReceiver,
        tcu: TCULogic,
        config: ConfigStore,
        logger: TelemetryLogger,
    ):
        self._recv = receiver
        self._tcu = tcu
        self._config = config
        self._logger = logger
        self._clients: Set = set()
        self._ui_available = _dist_index() is not None

    async def index(self, request):
        dist = _dist_index()
        if dist is not None:
            return web.FileResponse(dist)
        return web.Response(
            text=_NO_UI_HTML,
            content_type="text/html; charset=utf-8",
            status=503,
        )

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self._clients.add(ws)
        try:
            await ws.send_json(
                {
                    "type": "init",
                    "data": {
                        "mode": self._tcu.mode.value,
                        "live": self._recv.is_live,
                        "shift_count": self._tcu.shift_count,
                        "packets_total": self._recv.packets_total,
                        "config": self._config.data,
                        "defaults": DEFAULTS,
                        "log_status": self._logger.status,
                    },
                }
            )
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        if isinstance(data, dict):
                            await self._handle_client_msg(data, ws)
                    except Exception as e:
                        print(f"[WS] msg error: {e}")
                elif msg.type == WSMsgType.ERROR:
                    break
        finally:
            self._clients.discard(ws)
        return ws

    async def _handle_client_msg(self, msg: dict, ws):
        t = msg.get("type")
        if t == "set_mode":
            self._tcu.set_mode(msg.get("mode", ""))
        elif t == "set_config":
            key = msg.get("key", "")
            val = msg.get("value")
            self._config.set(key, val)
            if key in ("shift_key_up", "shift_key_down"):
                self._tcu.refresh_shift_keys()
        elif t == "reset_config":
            self._config.reset()
            self._tcu.refresh_shift_keys()
            await ws.send_json({"type": "config_reset", "data": self._config.data})
        elif t == "log_start":
            mode = msg.get("mode", "events")
            self._logger.start(mode)
            await ws.send_json({"type": "log_status", "data": self._logger.status})
        elif t == "log_stop":
            path = self._logger.stop()
            await ws.send_json(
                {"type": "log_status", "data": self._logger.status, "last_file": path}
            )
        elif t == "request_graph":
            await ws.send_json(
                {"type": "graph_data", "data": self._tcu.snapshot_graph()}
            )
        elif t == "export_profile":
            export = {
                "version": "v12.0.4",
                "exported_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "config": self._config.data,
            }
            await ws.send_json({"type": "profile_export", "data": export})
        elif t == "import_profile":
            try:
                imported = msg.get("data", {})
                if isinstance(imported, dict) and "config" in imported:
                    for k, v in imported["config"].items():
                        if k in DEFAULTS:
                            self._config.set(k, v)
                    self._tcu.refresh_shift_keys()
                    await ws.send_json(
                        {
                            "type": "profile_imported",
                            "ok": True,
                            "data": self._config.data,
                        }
                    )
                else:
                    await ws.send_json(
                        {
                            "type": "profile_imported",
                            "ok": False,
                            "error": "invalid format",
                        }
                    )
            except Exception as e:
                await ws.send_json(
                    {"type": "profile_imported", "ok": False, "error": str(e)}
                )

    async def broadcast_loop(self):
        tcu_interval = 1.0 / 60.0
        broadcast_every_n = 2
        tick = 0
        while True:
            await asyncio.sleep(tcu_interval)
            tick += 1
            
            if tick % broadcast_every_n != 0:
                continue
            if not self._clients:
                continue
                
            td = self._recv.latest()
            
            payload_tel = {"type": "telemetry", "data": self._tcu.snapshot(td)}
            payload_st = {
                "type": "state",
                "data": {
                    "mode": self._tcu.mode.value,
                    "live": self._recv.is_live,
                    "shift_count": self._tcu.shift_count,
                    "packets_total": self._recv.packets_total,
                },
            }
            
            dead = set()

            async def _send_safe(client_ws):
                try:
                    # Zombi soketlerin yayın hattını kitlemesini engelleyen 50ms agresif timeout
                    await asyncio.wait_for(client_ws.send_json(payload_tel), timeout=0.05)
                    await asyncio.wait_for(client_ws.send_json(payload_st), timeout=0.05)
                except Exception:
                    dead.add(client_ws)

            tasks = [_send_safe(client) for client in self._clients]
            if tasks:
                await asyncio.gather(*tasks)

            if dead:
                self._clients -= dead

    async def start(self):
        app = web.Application()
        assets = _dist_assets_dir()
        if assets is not None:
            app.router.add_static("/assets", assets)
        app.router.add_get("/", self.index)
        app.router.add_get("/ws", self.websocket_handler)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, Cfg.WEB_HOST, Cfg.WEB_PORT)
        await site.start()
        if self._ui_available:
            print(f"  [OK] Web UI (dist: {paths.web_dist_dir()})")
        else:
            print(f"  [!] Web UI assets missing ({paths.web_dist_dir()})")
        asyncio.create_task(self.broadcast_loop())

    async def stop(self):
        for ws in list(self._clients):
            await ws.close()