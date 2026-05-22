@echo off
cd /d "%~dp0VirtualTCU"
if not exist "VirtualTCU.exe" (
  echo VirtualTCU.exe not found. Extract the full zip and run this from the release folder.
  pause
  exit /b 1
)
VirtualTCU.exe
if errorlevel 1 pause
