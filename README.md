# Virtual TCU v12.0 — Forza Horizon 6

**English | [简体中文](README.zh-CN.md)**

> This project is maintained for the [**Forza Mods**](https://discord.gg/forzamods) Discord community by **Insightful**.

An external adaptive transmission controller for *Forza Horizon 6*. It reads real-time UDP telemetry from the game, decides when to shift based on driving style, throttle, RPM, speed, and brake input, and injects keyboard keys (**E** = upshift, **Q** = downshift).

After launch, open **http://127.0.0.1:8765** in your browser for the live dashboard and settings (English / 简体中文 UI).

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

**F9** (global hotkey, works while Forza is in focus) cycles through modes. Hotkeys can be changed in the Web UI settings.

---

## Requirements

| Item | Requirement |
|------|-------------|
| OS | **Windows 10 / 11** only |

### Option A — Download release (no Python / Node)

1. Open **[GitHub Releases](https://github.com/Quirrel-zh/fh6-virtual_tcu/releases)** and download the latest `VirtualTCU-*-win64.zip`.
2. Extract anywhere (e.g. `C:\Games\VirtualTCU\`).
3. Run **`VirtualTCU.exe`** as **Administrator** (required for global key injection).
4. Open **http://127.0.0.1:8765** in your browser.

Settings, profiles, and logs are stored under **`%APPDATA%\VirtualTCU\`** (`tcu_config.json`, `tcu_profiles.json`, `logs\`).

### Option B — Run from source (developers)

| Item | Requirement |
|------|-------------|
| Python | **3.10+** — [Download](https://www.python.org/downloads/) — check **Add Python to PATH** during install |
| Node.js | Only needed to develop or rebuild the Web UI (18+ recommended) |

### Install Python dependencies

Run in an **Administrator** Command Prompt (`keyboard` needs elevated privileges for global key injection):

```bash
pip install -r requirements.txt
```

- `keyboard` — required (hotkeys + virtual key injection)
- `aiohttp` — optional; without it the Web UI will not start (core TCU can still run headless)
- `pypresence` — optional Discord Rich Presence

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

## How to Run

### Release build (recommended for players)

See **Option A** under [Requirements](#requirements). No install step — extract the zip and run `VirtualTCU.exe` as Administrator.

### From source (developers)

1. Open Command Prompt as **Administrator** (recommended for reliable shift injection).
2. Go to the project folder and start:

   ```bash
   cd path\to\virtualTCU
   python -m virtual_tcu
   ```

   Legacy entry point also works: `python virtual_tcu.py`

3. Open **http://127.0.0.1:8765** in your browser.
4. Launch FH6 and start a race — the dashboard goes live once telemetry is received.
5. Press **Q** in the terminal window to quit.

### First run or after frontend changes

Build the Web UI before running (or use a GitHub Release zip that already includes `dist/`):

```bash
cd web-ui
npm install
npm run build
```

Output goes to `virtual_tcu/web/dist/`. Without a build, the backend serves HTTP **503** with instructions instead of the dashboard.

Frontend development: see [web-ui/README.md](web-ui/README.md).

---

## Web Dashboard

When connected, the browser shows:

- **Gear / speed / RPM** — color-coded tach bar (green → yellow → orange → red)
- **Throttle / brake** — pedal percentages
- **TCU state** — cruising, kickdown, engine braking, etc.
- **Turbo / engine** — boost (bar), power (kW), torque (Nm)
- **Stats & shift history** — session data and learning progress
- **Settings** — live tuning saved to `tcu_config.json`; per-car profile export/import

Switch UI language in the page header (English / 简体中文).

---

## Project Layout (brief)

```
virtualTCU/
├── virtual_tcu.py          # entry → virtual_tcu.app
├── virtual_tcu/            # Python package
│   ├── logic/tcu.py        # shift logic & drive modes
│   ├── telemetry/          # FH6 UDP parser
│   ├── web/                # Web server + dist assets
│   └── ...
├── web-ui/                 # Vue 3 + Tailwind v4 frontend
├── tcu_config.json         # tunables (dev: project cwd; release: %APPDATA%\VirtualTCU)
├── tcu_profiles.json       # per-car profiles (same locations as config)
└── logs/                   # optional telemetry replay logs (dev cwd / release APPDATA)
```

---

## Troubleshooting

### Dashboard shows offline / waiting for Forza

- Confirm **Data Out** is ON and port is **5555**.
- You must be **in a race** (no telemetry in menus).
- Restart Forza after changing Data Out settings.

### TCU does not shift / shifts have no effect in-game

- Verify Forza keyboard bindings: Shift Up = **E**, Shift Down = **Q**.
- Run CMD as **Administrator**, then start `python -m virtual_tcu`.

### F9 does not change modes

- Another app may have registered F9 (Discord overlay, MSI Afterburner, etc.). Close overlays and try again.

### Wrong gear or speed shows 0

- Calibrated for **FH6 Car Dash (324-byte)** packets only. Not compatible with FH5 or Forza Motorsport.

---

## Notes

- Works with any FH6 car — max RPM comes from telemetry so shift points auto-calibrate per car.
- **Reverse protection** — no automatic shifts in reverse.
- **Low-speed protection** — no automatic shifts below ~12 km/h to avoid jerky stops.
- Only sends **E** / **Q** keyboard events; does not modify controller or other inputs.

---

## Tested On

- Windows 11
- Steam edition of Forza Horizon 6
- Xbox Elite Series 2 controller

Telemetry based on the reverse-engineered FH6 **324-byte Car Dash** packet (confirmed via live diagnostics).
