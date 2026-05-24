import json
from pathlib import Path
from typing import Dict, Optional, Union

from virtual_tcu.config.constants import DEFAULTS
from virtual_tcu.config.web_bind import valid_bind_host
from virtual_tcu import paths

class ConfigStore:
    def __init__(self, path: Optional[Union[str, Path]] = None):
        self.path = Path(path) if path is not None else paths.config_file()
        self.data: Dict[str, float | bool] = dict(DEFAULTS)
        self.load()

    def load(self):
        if not self.path.exists():
            self.save()
            return
        try:
            stored = json.loads(self.path.read_text())
            new_keys_added = False
            for k, default_v in DEFAULTS.items():
                if k not in stored:
                    new_keys_added = True
                    continue
                v = stored[k]
                try:
                    if isinstance(default_v, str):
                        v = str(v)
                    elif isinstance(default_v, bool):
                        if isinstance(v, str):
                            v = v.strip().lower() in ("true", "1", "t", "y", "yes")
                        else:
                            v = bool(v)
                    elif isinstance(default_v, int):
                        v = int(float(v))
                    elif isinstance(default_v, float):
                        v = float(v)
                    self.data[k] = v
                except (TypeError, ValueError):
                    print(f"[Config] invalid value for {k!r}, using default")
            host = str(self.data.get("web_host", "")).strip()
            if not valid_bind_host(host):
                print(f"[Config] invalid web_host {host!r}, using default")
                self.data["web_host"] = DEFAULTS["web_host"]
                new_keys_added = True
            port = int(self.data.get("web_port", DEFAULTS["web_port"]))
            if port < 1024 or port > 65535:
                print(f"[Config] invalid web_port {port}, using default")
                self.data["web_port"] = DEFAULTS["web_port"]
                new_keys_added = True
            udp_port = int(self.data.get("udp_port", DEFAULTS["udp_port"]))
            if udp_port < 1 or udp_port > 65535:
                print(f"[Config] invalid udp_port {udp_port}, using default")
                self.data["udp_port"] = DEFAULTS["udp_port"]
                new_keys_added = True
            if new_keys_added:
                self.save()
                print(f"[Config] new settings added — file updated")
        except Exception as e:
            print(f"[Config] load failed, using defaults: {e}")
            try:
                self.path.rename(self.path.with_suffix(".json.corrupt"))
            except Exception:
                pass
            self.save()

    def save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.data, indent=2))
        except Exception as e:
            print(f"[Config] save failed: {e}")

    def reset(self):
        self.data = dict(DEFAULTS)
        self.save()

    def set_network(self, host: str, web_port, udp_port) -> tuple[bool, str]:
        host = str(host).strip()
        if not valid_bind_host(host):
            return False, "invalid_host"
        try:
            web_port = int(float(web_port))
            udp_port = int(float(udp_port))
        except (TypeError, ValueError):
            return False, "invalid_port"
        web_port = max(1024, min(65535, web_port))
        udp_port = max(1, min(65535, udp_port))
        self.data["web_host"] = host
        self.data["web_port"] = web_port
        self.data["udp_port"] = udp_port
        self.save()
        return True, ""

    def set_web_bind(self, host: str, port) -> tuple[bool, str]:
        udp = int(self.data.get("udp_port", DEFAULTS["udp_port"]))
        return self.set_network(host, port, udp)

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value):
        if key not in DEFAULTS:
            return
        try:
            default_v = DEFAULTS[key]
            if key in ("web_host", "web_port", "udp_port"):
                return
            elif isinstance(default_v, str):
                value = str(value).strip().lower()
                if not value and key.startswith("shift_key_"):
                    value = str(default_v)
                elif not value and key.startswith("hotkey_"):
                    value = str(default_v)
            elif isinstance(default_v, bool):
                if isinstance(value, str):
                    value = value.strip().lower() in ("true", "1", "t", "y", "yes")
                else:
                    value = bool(value)
            elif isinstance(default_v, int):
                value = int(float(value))
                if key == "web_port":
                    value = max(1024, min(65535, value))
                elif key == "udp_port":
                    value = max(1, min(65535, value))
                elif key not in ("launch_rpm",):
                    value = max(0, min(100, value))
                else:
                    value = max(1000, min(10000, value))
            elif isinstance(default_v, float):
                value = float(value)
            self.data[key] = value
            self.save()
        except (TypeError, ValueError) as e:
            print(f"[Config] set({key!r}, {value!r}) failed: {e}")

