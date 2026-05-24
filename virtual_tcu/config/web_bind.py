"""Web UI bind address helpers."""

from __future__ import annotations

import socket
from typing import Dict, List, Optional, Tuple

from virtual_tcu.config.constants import Cfg


def valid_bind_host(host: str) -> bool:
    host = host.strip()
    if host in ("0.0.0.0", "127.0.0.1"):
        return True
    parts = host.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False


def resolve_bind(config) -> Tuple[str, int]:
    host = str(config.get("web_host", Cfg.WEB_HOST)).strip()
    if not valid_bind_host(host):
        host = Cfg.WEB_HOST
    port = int(config.get("web_port", Cfg.WEB_PORT))
    port = max(1024, min(65535, port))
    return host, port


def client_host(bind_host: str) -> str:
    return "127.0.0.1" if bind_host in ("0.0.0.0", "::") else bind_host


def local_lan_ip() -> Optional[str]:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return None


def web_urls(config) -> Dict[str, object]:
    bind_host, port = resolve_bind(config)
    local = f"http://127.0.0.1:{port}"
    urls: Dict[str, object] = {
        "bind_host": bind_host,
        "port": port,
        "local": local,
    }
    if bind_host == "0.0.0.0":
        lan_ip = local_lan_ip()
        if lan_ip:
            urls["lan"] = f"http://{lan_ip}:{port}"
    elif bind_host not in ("127.0.0.1",):
        urls["lan"] = f"http://{bind_host}:{port}"
    return urls


def format_startup_urls(config) -> List[str]:
    info = web_urls(config)
    port = info["port"]
    bind_host = info["bind_host"]
    lines = [str(info["local"])]
    lan = info.get("lan")
    if lan and lan != info["local"]:
        lines.append(f"{lan} (LAN)")
    elif bind_host == "0.0.0.0":
        lines.append(f"0.0.0.0:{port} (all interfaces)")
    return lines


def network_status(config) -> Dict[str, object]:
    urls = web_urls(config)
    urls["udp_port"] = int(config.get("udp_port", Cfg.UDP_PORT))
    return urls


def bind_error_hint(exc: OSError) -> str:
    winerr = getattr(exc, "winerror", None)
    if exc.errno in (98, 10048) or winerr in (10048, 10013):
        return (
            "port already in use — quit other Virtual TCU instances "
            "or choose another port in settings"
        )
    if winerr == 10013:
        return "access denied — try 127.0.0.1 or run as Administrator"
    return str(exc)
