@echo off
REM Convenience launcher for local Electron dev.
REM Assumes:
REM   1. web-ui has been built once   (cd web-ui && npm install && npm run build)
REM      Dashboard at http://127.0.0.1:8765 is view-only; use Electron Settings for config.
REM   2. Python deps are installed    (pip install -r requirements.txt)
REM   3. Electron deps are installed  (cd electron && npm install)
REM
REM This script does NOT bundle the Python backend; the Electron main process
REM falls back to `python -m virtual_tcu --backend-only` when no PyInstaller
REM build exists at dist/VirtualTCU/VirtualTCU.exe.

cd /d "%~dp0\..\electron"
npm run dev
