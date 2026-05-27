; Custom NSIS hooks for VirtualTCU.
;
; Ensures the Electron shell AND the bundled Python backend (both named
; VirtualTCU.exe) are fully terminated before file removal, with retries
; for lingering file locks.

!macro _tcuForceKillProcesses
  DetailPrint "Stopping Virtual TCU processes..."
  ; KILL_PROCESS (force=1) kills every process whose image path is under $INSTDIR,
  ; covering both the Electron shell and resources/backend/VirtualTCU.exe.
  !insertmacro KILL_PROCESS "${APP_EXECUTABLE_FILENAME}" 1
  Sleep 1500
  ; Fallback when PowerShell is unavailable or paths differ.
  nsExec::ExecToLog 'taskkill /F /T /IM "${APP_EXECUTABLE_FILENAME}"'
  Pop $0
  Sleep 1000
!macroend

!macro customUnInstall
  !insertmacro _tcuForceKillProcesses
!macroend

!macro customRemoveFiles
  DetailPrint "Removing Virtual TCU installation files..."
  SetOutPath $TEMP

  StrCpy $R9 0
  remove_loop:
    IntOp $R9 $R9 + 1
    !insertmacro _tcuForceKillProcesses
    RMDir /r "$INSTDIR"
    IfFileExists "$INSTDIR\${APP_EXECUTABLE_FILENAME}" 0 remove_done
    DetailPrint "Files still locked (attempt $R9/8)..."
    IntCmp $R9 8 remove_warn remove_loop remove_done

  remove_warn:
    MessageBox MB_OK|MB_ICONEXCLAMATION \
      "Some Virtual TCU files could not be removed because the app is still running.$\r$\n$\r$\nPlease quit Virtual TCU from the tray (or end all VirtualTCU.exe tasks in Task Manager), then delete the folder manually:$\r$\n$INSTDIR"
    Goto remove_done

  remove_done:
!macroend
