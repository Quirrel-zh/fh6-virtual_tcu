# Virtual TCU v13.0 — Forza Horizon 6

**English | [简体中文](README.zh-CN.md)**

> This project is maintained for the [**Forza Mods**](https://discord.gg/forzamods) Discord community by **Insightful**.

An external adaptive transmission controller for *Forza Horizon 6*. It reads real-time UDP telemetry from the game, decides when to shift based on driving style, throttle, RPM, speed, and brake input, and injects keyboard keys (**E** = upshift, **Q** = downshift).

**v13** ships as a Windows tray app (Electron) with a floating HUD and auto-update. The live telemetry dashboard runs in your browser at **http://127.0.0.1:8765** (English / 简体中文). A portable Python-only build is still available for users who prefer no Electron.

---

## Quick start

| I want to… | Use |
|------------|-----|
| Play — tray app, HUD overlay & auto-update | [Download Electron installer](#download--use-electron-installer) |
| Play — Python backend only, no Electron | [Download backend-only zip](#download--use-backend-only-zip) |
| Develop or run from this repo | [Run from source](#run-from-source) |
| Change the Vue UI | [web-ui/README.md](web-ui/README.md) |

**Platform:** Windows 10 / 11 only. Run as **Administrator** (required for global key injection).

---

## Download & use (Electron installer)

Recommended for most users. Single installer that bundles the Python backend, provides a **Settings** window for configuration, a **read-only browser dashboard** for live telemetry, an optional **HUD overlay**, and **auto-update**.

### 1. Download

Open **[GitHub Releases](https://github.com/Quirrel-zh/fh6-virtual_tcu/releases)** and download the latest `VirtualTCU-*-win64.exe`.

### 2. Install & launch

Run the installer (Administrator is requested on launch). It registers a Start Menu / desktop shortcut and creates a **system tray icon** on first start.

On launch the app:

1. Starts the bundled Python backend in the background.
2. Opens the **Settings** window (drive modes, tuning, network, stats, updater, etc.).
3. Keeps running in the tray when you close the Settings window.

**Tray menu:**

| Item | Action |
|------|--------|
| **Settings** | Open / focus the Settings window |
| **Open Dashboard in Browser** | Open the live telemetry dashboard (`http://127.0.0.1:8765`) |
| **Toggle HUD** | Show / hide the floating overlay (gear / mode / RPM / speed) |
| **Restart Backend** | Restart the Python backend without quitting the app |
| **Quit** | Exit completely |

Left-click the tray icon also opens **Settings**.

**Auto-update** checks GitHub Releases shortly after launch and downloads new versions in the background. The full Electron + Python bundle updates as one package (see **About** tab in Settings).

### 3. Play

Configure FH6 once ([in-game setup](#forza-horizon-6--in-game-setup-one-time)), then:

1. Open **Settings** → pick a drive mode and adjust options as needed.
2. Tray → **Open Dashboard in Browser** (or the button on the Settings **Overview** tab) for the live view.
3. Optionally tray → **Toggle HUD** for the in-game overlay.
4. Start a race — the dashboard and HUD go **live** when telemetry arrives.

### 4. Quit

Tray icon → **Quit**.

### Where Electron data is stored

The bundled backend saves config, profiles, and logs next to `VirtualTCU.exe` inside the install's `resources/backend/` folder (portable-style). If that folder is not writable (e.g. under `C:\Program Files\`), data falls back to **`%APPDATA%\VirtualTCU\`**.

| Item | Default (Electron) |
|------|---------------------|
| Settings | `resources\backend\tcu_config.json` or `%APPDATA%\VirtualTCU\tcu_config.json` |
| Per-car profiles | same folder / `tcu_profiles.json` |
| Telemetry replay logs | same folder / `logs\` |
| Crash log (if startup fails) | same folder / `crash.log` |

---

## Download & use (backend-only zip)

For users who want the original portable layout without Electron, HUD, or auto-update. The dashboard opens in your default browser and includes full settings (not view-only).

### 1. Download

`VirtualTCU-Backend-*-win64.zip` from **[GitHub Releases](https://github.com/Quirrel-zh/fh6-virtual_tcu/releases)**.

### 2. Extract

```
VirtualTCU-Backend-13.0.x-win64/
├── Launch VirtualTCU.bat    ← optional launcher (recommended)
└── VirtualTCU/
    ├── VirtualTCU.exe
    └── _internal/           ← required; do not delete or move exe alone
```

### 3. Start

Right-click **`Launch VirtualTCU.bat`** or **`VirtualTCU\VirtualTCU.exe`** → **Run as administrator**. A console opens; the browser may auto-open **http://127.0.0.1:8765**.

### 4. Quit

Focus the **console window** and press **`Ctrl + C`**, then close it. (**Do not** use **Q** — that's the in-game downshift key.)

### Where backend-only data is stored

Release builds save config, profiles, and logs **in the same folder as `VirtualTCU.exe`** (portable-style):

```
VirtualTCU/
├── VirtualTCU.exe
├── _internal/
├── tcu_config.json
├── tcu_profiles.json
├── logs/
│   └── tcu_replay_*.bin.gz
└── .tcu_last_run
```

If the install folder is not writable (e.g. `C:\Program Files\`), data falls back to **`%APPDATA%\VirtualTCU\`** (the console shows which path is used on startup).

| Item | Default (Release) |
|------|-------------------|
| Settings | `VirtualTCU\tcu_config.json` |
| Per-car profiles | `VirtualTCU\tcu_profiles.json` |
| Telemetry replay logs | `VirtualTCU\logs\` |
| Crash log (if startup fails) | same folder as above / `crash.log` |

### Telemetry recording

**Electron users:** start / stop logging from the **Settings** window (Overview or sidebar controls).

**Backend-only users:** use the Web UI sidebar — **Start logging (events)** or **Start logging (all)**, drive in FH6, then **Stop**.

| Mode | What it records |
|------|-----------------|
| **Events** | Shift moments + short buffer (~0.5 MB typical) |
| **All** | Every telemetry packet while recording (up to 10 MB auto-stop) |

Files are named `tcu_replay_YYYYMMDD_HHMMSS.bin.gz` (gzip binary replay, not plain `.log`).

---

## Run from source

For developers or anyone running from a git clone.

### Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.10+ | [Download](https://www.python.org/downloads/) — check **Add Python to PATH** |
| Node.js | 18+ | Required for Vue dashboard build and Electron shell |

### One-time setup

Open **Administrator** Command Prompt or PowerShell:

```bash
cd path\to\virtualTCU
pip install -r requirements.txt

cd web-ui
npm install
npm run build
cd ..
```

`npm run build` writes the dashboard to `virtual_tcu/web/dist/`. Without it, the backend returns HTTP **503** instead of the UI.

### Option A — Electron shell (recommended)

```bash
cd electron
npm install
npm run dev
```

Or from the repo root: `packaging\dev-electron.bat`

This launches the full Electron app, spawning `python -m virtual_tcu --backend-only` automatically. Re-runs reuse the PyInstaller exe at `dist/VirtualTCU/` if present (set `TCU_USE_FROZEN_BACKEND=1` to force it in dev).

### Option B — Python backend only (browser UI)

```bash
cd path\to\virtualTCU
python -m virtual_tcu
```

(`python virtual_tcu.py` also works.) Open **http://127.0.0.1:8765**, launch FH6, enter a race. Quit with **`Ctrl + C`**.

### Where source-run data is stored

When running from source, config / profiles / logs use the **project directory** (current working directory):

```
virtualTCU/
├── tcu_config.json
├── tcu_profiles.json
└── logs/
    └── tcu_replay_*.bin.gz
```

### Frontend dev (optional)

Terminal 1 — backend:

```bash
python -m virtual_tcu
```

Terminal 2 — Vite hot reload:

```bash
cd web-ui
npm run dev
```

Open **http://127.0.0.1:5173** (proxies WebSocket to port 8765). See [web-ui/README.md](web-ui/README.md).

### Build a Release locally (maintainers)

```bash
# 1. Vue dashboard
cd web-ui && npm ci && npm run build && cd ..

# 2. Python backend (PyInstaller onedir → dist/VirtualTCU/)
pip install pyinstaller
pyinstaller virtual_tcu.spec --noconfirm

# 3. Electron installer (NSIS → electron/release/VirtualTCU-*-win64.exe)
cd electron && npm ci && npm run package
```

Push a `v*` tag to trigger CI, which produces both the Electron installer (`VirtualTCU-*-win64.exe` + `latest.yml`) and the backend-only zip (`VirtualTCU-Backend-*-win64.zip`).

---

## Drive Modes

| Mode | Behavior |
|------|----------|
| **COMFORT** | Eco-friendly shifts, early upshifts, cruise efficiency at stable speeds |
| **DYNAMIC** | Audi-style: higher RPM hold, strict rev-matching downshifts |
| **RACE** | Track-focused: near-redline upshifts, aggressive engine braking |
| **DRIFT** | Holds RPM in the power band, reduces unwanted downshifts mid-slide |
| **OFFROAD** | Tuned for low grip and uneven terrain |
| **MANUAL** | TCU disabled — you shift yourself |

**F9** (global hotkey, works while Forza is in focus) cycles through modes. **F8** toggles logging. Both can be changed in Settings / the Web UI.

---

## Forza Horizon 6 — In-Game Setup (one-time)

### 1. Transmission

**Settings → Difficulty → Transmission → MANUAL (No Clutch)**

### 2. Keyboard shift bindings

**Settings → Controls → Keyboard**:

| Action | Key |
|--------|-----|
| Shift Up | **E** |
| Shift Down | **Q** |

> Controller or wheel paddle bindings can stay **active at the same time**. The TCU only injects **E** / **Q** and does not take over throttle, steering, or other axes.

### 3. Telemetry Data Out

**Settings → HUD and Gameplay → Data Out**:

| Option | Value |
|--------|-------|
| Data Out | **ON** |
| IP Address | `127.0.0.1` |
| Port | `5555` |
| Packet Format | **Car Dash** (324 bytes) |

> If you change the UDP port in Virtual TCU network settings, update FH6 to match.

---

## Desktop app (Electron)

| Window | Purpose |
|--------|---------|
| **Settings** | Full configuration — drive modes, sliders, hotkeys, network, stats, shift history, profile import/export, auto-update |
| **Browser dashboard** | Read-only live view — gear, RPM chart, G-meter, session stats (opened via tray or Settings) |
| **HUD overlay** | Minimal always-on-top overlay — gear, mode, RPM bar, speed, shift hint; supports click-through |

Closing the Settings window hides it; the app keeps running in the tray until you choose **Quit**.

---

## Web Dashboard

When connected, the browser dashboard shows:

- **Gear / speed / RPM** — large gear readout, 20-segment RPM LED bar
- **Live chart** — RPM, throttle, brake, and speed over time with shift markers
- **G-meter** — lateral / longitudinal G ball with grip usage
- **Pedals & inputs** — throttle, brake, clutch percentages
- **TCU state** — cruising, kickdown, engine braking, airborne / yaw locks, etc.
- **Turbo / engine** — boost (bar), power (kW), torque (Nm)
- **Stats & shift history** — session counters, peaks, and recent shift log (right panel)
- **Learning sidebar** — sport index, power-curve / ratio calibration status

In the **Electron** build the browser page is **view-only** (footer reminds you to use the desktop Settings app for configuration and logging). The **backend-only** build exposes full settings in the Web UI.

Switch UI language in the page header (English / 简体中文).

---

## Network settings

Available in the Electron **Settings** window and the backend-only Web UI:

| Setting | Default | Notes |
|---------|---------|-------|
| Web bind address | `127.0.0.1` | Set to `0.0.0.0` to allow LAN access from other devices on your network |
| Web port | `8765` | Dashboard HTTP / WebSocket port |
| UDP port | `5555` | Must match FH6 Data Out port |

Click **Apply** to save. The backend hot-reloads bindings; if the web port changes, reopen the dashboard at the new URL shown in Settings.

---

## Project layout (brief)

```
virtualTCU/
├── virtual_tcu.py          # entry → virtual_tcu.app
├── virtual_tcu/            # Python backend package
├── web-ui/                 # Vue 3 + Tailwind v4 dashboard (served at :8765)
├── electron/               # Electron shell (tray, Settings, HUD, auto-update)
│   ├── src/main/index.ts   # spawns backend, lifecycle, tray, IPC, autoUpdater
│   ├── src/settings-renderer/  # Settings window (Naive UI)
│   ├── src/hud-renderer/   # frameless transparent HUD overlay
│   ├── src/preload/        # main + hud preload scripts
│   └── electron-builder.yml
├── packaging/              # Launch VirtualTCU.bat, dev-electron.bat
├── virtual_tcu.spec        # PyInstaller spec (onedir → dist/VirtualTCU/)
└── .github/workflows/      # Release CI (Vue → PyInstaller → electron-builder)
```

---

## Troubleshooting

### Electron app starts but dashboard won't open

- Tray → **Open Dashboard in Browser**, or Settings → **Overview** → open dashboard.
- Confirm the backend is ready (Settings shows **live** / **standby**, not **disconnected**).
- Tray → **Restart Backend** if the backend crashed.

### Release exe flashes and closes (backend-only zip)

- Extract the **full** zip — exe needs `_internal/` beside it.
- Close other TCU instances (`python -m virtual_tcu` or another `VirtualTCU.exe`) — ports **5555** / **8765** are single-use per instance.
- Run from cmd: `cd path\to\VirtualTCU` then `VirtualTCU.exe` (failed builds pause with an error).
- Check **`crash.log`** in the data folder shown at startup (exe dir or `%APPDATA%\VirtualTCU\`).

### Port already in use

- Only one backend should run at a time. Quit other Virtual TCU instances or change ports in network settings.

### Recording started but no log file found

- Logs live in the backend data folder (`logs\` next to `VirtualTCU.exe` or `%APPDATA%\VirtualTCU\logs\`).
- Click **Stop** before looking — the gzip file is finalized on stop.
- Use **All** mode and drive in a race with Data Out ON; **Events** mode only writes meaningful data around shifts.
- Look for `tcu_replay_*.bin.gz`, not `.log`.

### Dashboard offline / waiting for Forza

- Data Out **ON**, port **5555**, **Car Dash** format.
- Must be **in a race** (no telemetry in menus).

### TCU does not shift

- Forza keyboard: Shift Up = **E**, Shift Down = **Q**.
- Run as **Administrator**.

### F9 / F8 hotkeys do nothing

- Close apps that may capture those keys (Discord overlay, MSI Afterburner, etc.).

### Wrong gear or speed

- FH6 **324-byte Car Dash** only — not FH5 or Forza Motorsport.

### Auto-update does nothing

- Auto-update only runs in the **packaged** Electron installer, not in `npm run dev`.
- Check the **About** tab in Settings for update status.

---

## Notes

- Works with any FH6 car — shift points auto-calibrate from telemetry max RPM.
- **Reverse protection** — no automatic shifts in reverse.
- **Low-speed protection** — no automatic shifts below ~12 km/h.
- Only sends **E** / **Q** keyboard events; does not modify controller inputs.

---

## Tested on

- Windows 11
- Steam edition of Forza Horizon 6
- Xbox Elite Series 2 controller

Telemetry based on the reverse-engineered FH6 **324-byte Car Dash** packet (confirmed via live diagnostics).
