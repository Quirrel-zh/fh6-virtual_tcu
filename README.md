# Virtual TCU v12.0 — Forza Horizon 6

**English | [简体中文](README.zh-CN.md)**

> This project is maintained for the [**Forza Mods**](https://discord.gg/forzamods) Discord community by **Insightful**.

An external adaptive transmission controller for *Forza Horizon 6*. It reads real-time UDP telemetry from the game, decides when to shift based on driving style, throttle, RPM, speed, and brake input, and injects keyboard keys (**E** = upshift, **Q** = downshift).

After launch, open **http://127.0.0.1:8765** in your browser for the live dashboard and settings (English / 简体中文 UI).

---

## Quick start

| I want to… | Use |
|------------|-----|
| Play — no Python / Node install | [Download & use (Release)](#download--use-release) |
| Develop or run from this repo | [Run from source](#run-from-source) |
| Change the Vue UI | [web-ui/README.md](web-ui/README.md) |

**Platform:** Windows 10 / 11 only. Run as **Administrator** (required for global key injection).

---

## Download & use (Release)

### 1. Download

Open **[GitHub Releases](https://github.com/Quirrel-zh/fh6-virtual_tcu/releases)** and download the latest `VirtualTCU-*-win64.zip`.

### 2. Extract

Extract the **entire** zip to any folder (e.g. `C:\Games\VirtualTCU\`). Do **not** run the exe from inside the zip preview.

```
VirtualTCU-12.0.x-win64/
├── Launch VirtualTCU.bat    ← optional launcher (recommended)
└── VirtualTCU/
    ├── VirtualTCU.exe
    └── _internal/           ← required; do not delete or move exe alone
```

### 3. Start

Right-click **`Launch VirtualTCU.bat`** or **`VirtualTCU\VirtualTCU.exe`** → **Run as administrator**.

A console window opens. The browser may auto-open **http://127.0.0.1:8765**; if not, open it manually.

### 4. Play

Configure FH6 once ([in-game setup](#forza-horizon-6--in-game-setup-one-time)), start a race, and the dashboard should go **live** when telemetry arrives.

### 5. Quit

Focus the **console window** and press **`Ctrl + C`**, then close the window.  
(**Do not** use **Q** — that is the in-game downshift key.)

### Where Release data is stored

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

### Telemetry recording (sidebar)

1. In the Web UI sidebar, click **Start logging (events)** or **Start logging (all)**.
2. Drive in FH6 (must be in a race with Data Out enabled).
3. Click **Stop** when done — the file is finalized on stop.

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
| Node.js | 18+ | Only for building / editing the Web UI |

### One-time setup

Open **Administrator** Command Prompt or PowerShell:

```bash
cd path\to\virtualTCU
pip install -r requirements.txt
```

```bash
cd web-ui
npm install
npm run build
cd ..
```

`npm run build` writes the dashboard to `virtual_tcu/web/dist/`. Without it, the backend returns HTTP **503** instead of the UI.

### Start the backend

```bash
cd path\to\virtualTCU
python -m virtual_tcu
```

(`python virtual_tcu.py` also works.)

Open **http://127.0.0.1:8765**, launch FH6, enter a race. Quit with **`Ctrl + C`** in the terminal.

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

### Build a Release zip locally (maintainers)

```bash
cd web-ui && npm run build && cd ..
pip install pyinstaller
pyinstaller virtual_tcu.spec --noconfirm
```

Output: `dist/VirtualTCU/` — same layout as the GitHub Release. Push a `v*` tag to trigger CI.

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

**F9** (global hotkey, works while Forza is in focus) cycles through modes. **F8** toggles logging. Both can be changed in the Web UI settings.

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

---

## Web Dashboard

When connected, the browser shows:

- **Gear / speed / RPM** — color-coded tach bar (green → yellow → orange → red)
- **Throttle / brake** — pedal percentages
- **TCU state** — cruising, kickdown, engine braking, etc.
- **Turbo / engine** — boost (bar), power (kW), torque (Nm)
- **Stats & shift history** — session data and learning progress
- **Settings** — live tuning; per-car profile export/import
- **Logger** — start/stop telemetry replay recording

Switch UI language in the page header (English / 简体中文).

---

## Project layout (brief)

```
virtualTCU/
├── virtual_tcu.py          # entry → virtual_tcu.app
├── virtual_tcu/            # Python package
├── web-ui/                 # Vue 3 + Tailwind v4 frontend
├── packaging/              # Launch VirtualTCU.bat (bundled in Release zip)
├── virtual_tcu.spec        # PyInstaller spec
└── .github/workflows/      # Release CI
```

---

## Troubleshooting

### Release exe flashes and closes

- Extract the **full** zip — exe needs `_internal/` beside it.
- Close other TCU instances (`python -m virtual_tcu` or another `VirtualTCU.exe`) — ports **5555** / **8765** are single-use.
- Run from cmd: `cd path\to\VirtualTCU` then `VirtualTCU.exe` (failed builds pause with an error).
- Check **`crash.log`** in the data folder shown at startup (exe dir or `%APPDATA%\VirtualTCU\`).

### Recording started but no log file found

- Release logs are in **`VirtualTCU\logs\`** next to the exe (or `%APPDATA%\VirtualTCU\logs\` if fallback).
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
