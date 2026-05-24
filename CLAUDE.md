# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Virtual TCU is a Windows-only external adaptive transmission controller for Forza Horizon 6. It reads real-time UDP telemetry from the game, makes shift decisions based on driving conditions, and injects keyboard inputs (E=upshift, Q=downshift) to control the in-game transmission.

## Running

### Release (Windows installer — recommended)

Download `VirtualTCU-*-win64.exe` from GitHub Releases and install. Launches as a tray app with:

- **Main dashboard** — Vue UI loaded inside an Electron `BrowserWindow` from the bundled Python backend at `http://127.0.0.1:8765`.
- **Floating HUD** — frameless, transparent, always-on-top mini overlay (gear / mode / RPM / speed). Toggle via tray menu.
- **Auto-update** — `electron-updater` polls GitHub Releases on launch; updates Electron + Python backend together as one package.

Run the installer as Administrator if hotkeys / key injection don't fire (the `keyboard` library requires elevated privileges on some systems).

`VirtualTCU-Backend-*-win64.zip` is also published for users who want the Python backend alone (no Electron, no auto-update, no HUD; opens the dashboard in the default browser).

### From source — Electron shell + Python backend

```bash
# 1. Build the Vue dashboard (one-time, also rebuild after web-ui changes)
cd web-ui && npm install && npm run build

# 2. Install Python deps
pip install -r requirements.txt

# 3. Install Electron deps and launch
cd electron && npm install && npm run dev
```

`electron/src/main/index.ts` spawns `python -m virtual_tcu --backend-only` (or the PyInstaller exe at `dist/VirtualTCU/VirtualTCU.exe` if it exists), waits for the `[backend-ready]` marker on stdout, then opens the main window pointing at `http://127.0.0.1:8765`.

### From source — Python only (no Electron)

```bash
python -m virtual_tcu
# or (backward compatible)
python virtual_tcu.py
```

Opens the dashboard in the system browser. No floating HUD, no auto-update.

### Packaging (maintainers)

```bash
# 1. Vue dashboard → virtual_tcu/web/dist/
cd web-ui && npm ci && npm run build && cd ..

# 2. Python backend → dist/VirtualTCU/VirtualTCU.exe (PyInstaller onedir)
pip install -r requirements.txt pyinstaller
pyinstaller virtual_tcu.spec --noconfirm

# 3. Electron shell → electron/release/VirtualTCU-<version>-win64.exe
cd electron && npm ci && npm run package
```

`electron-builder.yml` copies `dist/VirtualTCU/` into the installer as `resources/backend/`, so the final `.exe` is fully self-contained.

Push a tag `v*` (e.g. `v12.0.1`) to trigger `.github/workflows/release.yml`, which runs all three steps and publishes both the Electron installer and the backend-only zip.

## Dependencies

```bash
pip install -r requirements.txt
```

- `keyboard` — required, global hotkey registration and virtual key injection
- `aiohttp` — optional, enables the web UI (runs headless without it)
- `pypresence` — optional, Discord Rich Presence integration

## Architecture

Two top-level pieces:

1. **Electron shell** (`electron/`) — main process, preload scripts, frameless HUD renderer, auto-updater. Spawns the Python backend as a child process and renders the existing Vue dashboard in a `BrowserWindow`.
2. **Python backend** (`virtual_tcu/`) — telemetry receiver, shift logic, web/WebSocket server. Runs standalone (browser UI) or under Electron (`--backend-only`).

```
virtual_tcu/             # Python backend
  app.py                 # main(), hotkeys, async loop, --backend-only flag
  deps.py                # optional imports (keyboard, aiohttp, winsound)
  config/                # Cfg, DEFAULTS, ConfigStore
  telemetry/             # Telemetry model, FH6 parser, UDP receiver, replay logger
  input/                 # VirtualKeyboard (E/Q injection)
  storage/               # ProfileStore (per-car JSON)
  core/                  # Mode enum
  detectors/             # Reverse hold, airtime, yaw transient
  learning/              # Gear ratios, power curve, rev limiter, drive style
  state/                 # Shift history, session stats, graph buffer, watchdog
  logic/tcu.py           # TCULogic — shift rules and drive modes
  web/                   # WebServer + bundled dist/ assets
  integrations/          # Discord RPC

electron/                # Electron shell
  electron.vite.config.ts
  electron-builder.yml   # bundles ../dist/VirtualTCU as resources/backend
  src/
    main/index.ts        # spawn backend, lifecycle, tray, IPC, autoUpdater
    preload/main.ts      # exposes window.tcu API to the dashboard
    preload/hud.ts       # exposes window.hud API to the HUD
    hud-renderer/        # Vue 3 frameless transparent overlay
      index.html
      main.ts
      HudApp.vue

web-ui/                  # Vue 3 dashboard (loaded by main BrowserWindow at :8765)
```

### Process layout (release build)

```
VirtualTCU.exe (Electron main process)
├─ spawns: resources/backend/VirtualTCU.exe --backend-only
│           └─ aiohttp serves /assets, /, /ws on 127.0.0.1:8765
├─ main BrowserWindow → loadURL("http://127.0.0.1:8765")  → Vue dashboard
└─ HUD BrowserWindow  → loadFile(out/renderer/index.html) → Vue HUD
                        (connects to ws://127.0.0.1:8765/ws independently)
```

The Electron main process waits for the `[backend-ready]` marker on the backend's stdout before showing windows; on backend exit it broadcasts `backend:exit` IPC so renderers can show a banner and the tray "Restart Backend" entry can re-spawn.

### Core Data Flow

1. **TelemetryReceiver** — UDP socket on port 5555, parses FH6's 324-byte packet into a `Telemetry` dataclass
2. **TCULogic.process()** — runs at 60Hz in the async loop, evaluates shift rules against current telemetry
3. **VirtualKeyboard** — fires E/Q keypresses in daemon threads with configurable hold duration
4. **WebServer** — aiohttp app serves `web/dist/` and broadcasts state over WebSocket at 30Hz

### Learning Systems (per-car, runtime only — not persisted)

- **GearRatioCalibrator** — learns rpm/kmh ratio per gear from telemetry samples; enables projected-RPM calculations for over-rev protection and target gear selection
- **PowerCurveDetector** — fits a parabola to (rpm_fraction, torque) samples; derives peak torque/power RPM analytically for optimal upshift points
- **RevLimiterDetector** — detects the real fuel-cut RPM (often below Forza's reported max) by identifying the sawtooth oscillation pattern at WOT
- **DriveStyleTracker** — continuous 0→1 sport index with asymmetric time constants (fast rise, slow decay); drives Dynamic mode's CRUISE/ADAPTIVE/SPORT regime selection

### Drive Modes

Each mode is a method on `TCULogic` (`_mode_comfort`, `_mode_dynamic`, `_mode_race`, `_mode_drift`, `_mode_offroad`). They share common building blocks: `_track_brake_down`, `_track_upshift_in_band`, `_track_out_of_band_kickdown`, and safety guards (anti-stall, over-rev, cornering lock, airtime lock, transient lock).

### Configuration

Paths are resolved in `virtual_tcu/paths.py`:

- **Dev** — config/profiles/logs in the current working directory
- **Frozen (PyInstaller)** — `VirtualTCU.exe` directory for writable data (`tcu_config.json`, `logs/`, etc.); `%APPDATA%/VirtualTCU/` fallback if install dir is read-only; `sys._MEIPASS/virtual_tcu/web/dist` for UI assets

- `tcu_config.json` — all tunable parameters (shift points, feature toggles, hotkeys). Auto-created with defaults on first run. Editable live via web UI.
- `tcu_profiles.json` — per-car profile storage (keyed by car_ordinal)
- `logs/` — gzipped telemetry replay logs (binary format with `TCULOG01` magic header)

### Web UI

Vue 3 + TypeScript app in `web-ui/` using Tailwind CSS 4, vue-i18n (en + zh-CN). Path alias `@` → `web-ui/src/`.

```bash
cd web-ui
npm install
npm run dev          # port 5173, proxies /ws → localhost:8765
npm run build        # vue-tsc --noEmit + vite build → virtual_tcu/web/dist/
npm run lint         # eslint (flat config, @antfu/eslint-config)
npm run format       # prettier + prettier-plugin-tailwindcss
npm run typecheck    # vue-tsc --noEmit
```

If `dist/` is absent, `/` returns HTTP 503 with build/download instructions.

WebSocket messages: `telemetry`, `state`, `config_reset`, `log_status`. Settings use `set_config` and persist immediately.

## Key Constants

- UDP port: 5555 (class `Cfg` in `config/constants.py`)
- Web UI port: 8765
- Shift keys: E (up), Q (down) — `input/keyboard.py`
- Packet size: 324 bytes (FH6 "Car Dash" format)
- Hotkeys: F9 (cycle mode), F8 (toggle log) — configurable

## Platform Constraint

Windows-only. `main()` exits immediately on non-win32 platforms. The `keyboard` library requires elevated privileges for global key injection on some systems.
