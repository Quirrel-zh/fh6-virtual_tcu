/**
 * Electron main process for Virtual TCU.
 *
 * Responsibilities:
 *   - Spawn the bundled Python backend (VirtualTCU.exe --backend-only) and
 *     manage its lifecycle (start, restart, kill on quit).
 *   - Wait for the backend to print a READY marker on stdout, then create the
 *     settings window (local light-themed Vue UI).
 *   - Open the read-only dashboard in the user's default browser
 *     (http://127.0.0.1:8765) when requested.
 *   - Create an optional always-on-top frameless HUD window that connects to
 *     the same WebSocket.
 *   - Wire up auto-update via electron-updater + GitHub Releases.
 */

import type { ChildProcess } from 'node:child_process'
import type { BackendEndpoints } from './backend-config'
import { exec, spawn } from 'node:child_process'
import { existsSync } from 'node:fs'
import { join } from 'node:path'
import { PassThrough } from 'node:stream'
import { electronApp, is, optimizer } from '@electron-toolkit/utils'
import { app, BrowserWindow, ipcMain, Menu, nativeImage, shell, Tray } from 'electron'
import { autoUpdater } from 'electron-updater'
import { endpointsFromHttpUrl, parseWebUiUrl, resolveBackendEndpoints } from './backend-config'

const READY_MARKER = '[backend-ready]'

let backendEndpoints: BackendEndpoints = resolveBackendEndpoints()
let backendDataCwd = ''

let settingsWindow: BrowserWindow | null = null
let hudWindow: BrowserWindow | null = null
let tray: Tray | null = null
let backend: ChildProcess | null = null
let backendPid: number | null = null
let backendReady = false
let isQuitting = false

// ----- Backend spawn ---------------------------------------------------------

function resolveBackendCommand(): { cmd: string; args: string[]; cwd: string } {
  // Packaged: extraResources copies dist/VirtualTCU/ to resources/backend/.
  const packagedExe = join(process.resourcesPath, 'backend', 'VirtualTCU.exe')
  if (app.isPackaged && existsSync(packagedExe)) {
    return {
      cmd: packagedExe,
      args: ['--backend-only'],
      cwd: join(process.resourcesPath, 'backend'),
    }
  }

  // Dev: use live Python backend so dashboard changes in virtual_tcu/web/dist
  // are picked up after `pnpm build:dashboard`. Set TCU_USE_FROZEN_BACKEND=1 to
  // test against dist/VirtualTCU/VirtualTCU.exe instead.
  if (!is.dev || process.env.TCU_USE_FROZEN_BACKEND === '1') {
    const devExe = join(__dirname, '..', '..', '..', '..', 'dist', 'VirtualTCU', 'VirtualTCU.exe')
    if (existsSync(devExe)) {
      return {
        cmd: devExe,
        args: ['--backend-only'],
        cwd: join(__dirname, '..', '..', '..', '..', 'dist', 'VirtualTCU'),
      }
    }
  }

  return {
    cmd: 'python',
    args: ['-m', 'virtual_tcu', '--backend-only'],
    cwd: join(__dirname, '..', '..', '..', '..'),
  }
}

function startBackend(): Promise<void> {
  return new Promise((resolveStart, rejectStart) => {
    if (backend) {
      resolveStart()
      return
    }

    const { cmd, args, cwd } = resolveBackendCommand()
    backendDataCwd = cwd
    console.log(`[backend] spawn: ${cmd} ${args.join(' ')}`)

    try {
      backend = spawn(cmd, args, {
        cwd,
        windowsHide: true,
        stdio: ['ignore', 'pipe', 'pipe'],
      })
      backendPid = backend.pid ?? null
    } catch (err) {
      rejectStart(err)
      return
    }

    let settled = false
    const timeout = setTimeout(() => {
      if (!settled) {
        settled = true
        rejectStart(new Error('Backend did not become ready within 30s'))
      }
    }, 30_000)

    // Pipe backend stdout through a PassThrough so we can both forward it
    // (async, respects backpressure) AND listen for the READY_MARKER.
    // Use line-buffered parsing — 'data' fires on arbitrary chunk boundaries,
    // and the marker could be split across two chunks.  We split on \n, carry
    // the trailing partial across events, and check each complete line.
    const stdoutPass = new PassThrough()
    backend.stdout?.pipe(stdoutPass).pipe(process.stdout)
    let _lineBuf = ''
    stdoutPass.on('data', (chunk: Buffer) => {
      const raw = _lineBuf + chunk.toString('utf-8')
      const lines = raw.split('\n')
      // The last element is either a partial line or '' (if the chunk ended
      // with \n).  Keep it for the next chunk.
      _lineBuf = lines.pop() ?? ''
      for (const line of lines) {
        if (line.length === 0) continue
        const parsedUrl = parseWebUiUrl(line)
        if (parsedUrl)
          backendEndpoints = endpointsFromHttpUrl(
            parsedUrl,
            resolveBackendEndpoints(backendDataCwd),
          )
        if (!settled && line.includes(READY_MARKER)) {
          settled = true
          backendReady = true
          if (!parsedUrl) backendEndpoints = resolveBackendEndpoints(backendDataCwd)
          clearTimeout(timeout)
          broadcastBackendReady()
          resolveStart()
        }
      }
    })
    // Pipe stderr directly — no marker detection needed.
    backend.stderr?.pipe(process.stderr)
    backend.on('exit', (code, signal) => {
      console.log(`[backend] exited code=${code} signal=${signal}`)
      // Only clear state if this is still the current backend (PID guard
      // prevents a late exit event from the old process wiping a new one).
      if (backend?.pid === backendPid) {
        backend = null
        backendReady = false
      }
      if (!settled) {
        settled = true
        clearTimeout(timeout)
        rejectStart(new Error(`Backend exited before ready (code ${code})`))
      }
      if (!isQuitting) {
        settingsWindow?.webContents.send('backend:exit', { code, signal })
        hudWindow?.webContents.send('backend:exit', { code, signal })
      }
    })
    backend.on('error', (err) => {
      console.error('[backend] spawn error:', err)
      if (!settled) {
        settled = true
        clearTimeout(timeout)
        rejectStart(err)
      }
    })
  })
}

function stopBackend(): Promise<void> {
  return new Promise((resolve) => {
    const proc = backend
    const pid = backendPid
    if (!proc || pid == null) {
      backend = null
      backendPid = null
      backendReady = false
      resolve()
      return
    }

    // Capture before we null the refs — the exit handler will clear them
    // via the PID guard only if this pid still matches.
    backend = null
    backendPid = null
    backendReady = false

    let settled = false
    let forceTimeout: ReturnType<typeof setTimeout>
    const done = () => {
      if (settled) return
      settled = true
      clearTimeout(forceTimeout)
      resolve()
    }

    proc.once('exit', done)
    forceTimeout = setTimeout(() => {
      console.warn(`[backend] exit event did not fire for pid ${pid} — resolving anyway`)
      done()
    }, 5_000)

    if (process.platform === 'win32') {
      // /T = tree kill (children included), /F = force
      exec(`taskkill /F /T /PID ${pid}`, (err) => {
        if (err) {
          // taskkill returns non-zero if the process is already gone — that's fine.
          console.warn(`[backend] taskkill pid ${pid}: ${err.message}`)
        }
      })
    } else {
      // Negative pid kills the entire process group on POSIX.
      try {
        process.kill(-pid, 'SIGKILL')
      } catch {
        // Process already dead — expected.
      }
    }
  })
}

// ----- Windows ---------------------------------------------------------------

function settingsPagePath(): string {
  if (is.dev && process.env.ELECTRON_RENDERER_URL) {
    return `${process.env.ELECTRON_RENDERER_URL}/settings-renderer/index.html`
  }
  return join(__dirname, '..', 'renderer', 'settings-renderer', 'index.html')
}

function hudPagePath(): string {
  if (is.dev && process.env.ELECTRON_RENDERER_URL) {
    return `${process.env.ELECTRON_RENDERER_URL}/hud-renderer/index.html`
  }
  return join(__dirname, '..', 'renderer', 'hud-renderer', 'index.html')
}

function createSettingsWindow() {
  if (settingsWindow) {
    settingsWindow.show()
    settingsWindow.focus()
    return
  }

  settingsWindow = new BrowserWindow({
    width: 1100,
    height: 760,
    minWidth: 880,
    minHeight: 600,
    show: false,
    autoHideMenuBar: true,
    backgroundColor: '#f4f6fa',
    title: 'Virtual TCU',
    webPreferences: {
      preload: join(__dirname, '..', 'preload', 'main.js'),
      sandbox: true,
      backgroundThrottling: false,
    },
  })

  settingsWindow.on('ready-to-show', () => {
    settingsWindow?.show()
  })

  settingsWindow.on('close', (e) => {
    if (!isQuitting) {
      e.preventDefault()
      settingsWindow?.hide()
    }
  })

  settingsWindow.on('closed', () => {
    settingsWindow = null
  })

  if (is.dev && process.env.ELECTRON_RENDERER_URL) {
    settingsWindow.loadURL(settingsPagePath())
  } else {
    settingsWindow.loadFile(settingsPagePath())
  }

  settingsWindow.webContents.on('did-finish-load', () => {
    if (backendReady) broadcastBackendReady()
  })
}

function broadcastBackendReady() {
  const payload = {
    url: backendEndpoints.url,
    wsUrl: backendEndpoints.wsUrl,
    lanUrl: backendEndpoints.lanUrl,
    ready: true,
  }
  settingsWindow?.webContents.send('backend:ready', payload)
  hudWindow?.webContents.send('backend:ready', payload)
}

function openDashboardInBrowser() {
  backendEndpoints = resolveBackendEndpoints(backendDataCwd)
  shell.openExternal(backendEndpoints.url).catch((err) => {
    console.warn('[app] open dashboard failed:', err)
  })
}

function createHudWindow() {
  if (hudWindow) {
    hudWindow.show()
    hudWindow.focus()
    return
  }

  hudWindow = new BrowserWindow({
    width: 280,
    height: 140,
    x: 24,
    y: 24,
    show: false,
    frame: false,
    transparent: true,
    resizable: true,
    movable: true,
    skipTaskbar: true,
    alwaysOnTop: true,
    hasShadow: false,
    fullscreenable: false,
    minimizable: false,
    maximizable: false,
    backgroundColor: '#00000000',
    webPreferences: {
      preload: join(__dirname, '..', 'preload', 'hud.js'),
      sandbox: true,
      backgroundThrottling: false,
    },
  })

  hudWindow.setAlwaysOnTop(true, 'screen-saver')
  hudWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true })

  hudWindow.on('ready-to-show', () => {
    hudWindow?.show()
  })

  hudWindow.on('closed', () => {
    hudWindow = null
  })

  if (is.dev && process.env.ELECTRON_RENDERER_URL) {
    hudWindow.loadURL(hudPagePath())
  } else {
    hudWindow.loadFile(hudPagePath())
  }
}

// ----- Tray ------------------------------------------------------------------

function createTray() {
  const iconPath = app.isPackaged
    ? join(process.resourcesPath, 'icon.ico')
    : join(__dirname, '..', '..', 'build', 'icon.ico')
  const icon = nativeImage.createFromPath(iconPath)
  tray = new Tray(icon)
  tray.setToolTip('Virtual TCU')

  const menu = Menu.buildFromTemplate([
    { label: 'Settings', click: () => createSettingsWindow() },
    { label: 'Open Dashboard in Browser', click: () => openDashboardInBrowser() },
    {
      label: 'Toggle HUD',
      click: () => {
        if (hudWindow && hudWindow.isVisible()) hudWindow.hide()
        else createHudWindow()
      },
    },
    { type: 'separator' },
    {
      label: 'Restart Backend',
      click: async () => {
        await stopBackend()
        // Windows may hold the port briefly after process exit (TIME_WAIT).
        if (process.platform === 'win32') {
          await new Promise((r) => setTimeout(r, 300))
        }
        await startBackend()
      },
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        isQuitting = true
        app.quit()
      },
    },
  ])
  tray.setContextMenu(menu)
  tray.on('click', () => {
    createSettingsWindow()
  })
}

// ----- IPC -------------------------------------------------------------------

function registerIpc() {
  ipcMain.handle('app:get-backend-info', () => ({
    url: backendEndpoints.url,
    wsUrl: backendEndpoints.wsUrl,
    lanUrl: backendEndpoints.lanUrl,
    ready: backendReady,
  }))

  ipcMain.handle('app:open-dashboard', () => {
    openDashboardInBrowser()
  })

  ipcMain.handle('app:open-external', (_e, url: unknown) => {
    if (typeof url !== 'string' || !/^https?:\/\//i.test(url)) return
    shell.openExternal(url).catch((err) => {
      console.error('[main] openExternal failed:', err)
    })
  })

  ipcMain.handle('app:open-settings', () => {
    createSettingsWindow()
  })

  ipcMain.handle('hud:toggle', () => {
    if (hudWindow && hudWindow.isVisible()) hudWindow.hide()
    else createHudWindow()
  })

  ipcMain.handle('hud:close', () => {
    hudWindow?.close()
    hudWindow = null
  })

  ipcMain.handle('hud:set-ignore-mouse', (_e, ignore: boolean) => {
    hudWindow?.setIgnoreMouseEvents(ignore, { forward: true })
  })

  ipcMain.handle('app:restart-backend', async () => {
    await stopBackend()
    if (process.platform === 'win32') {
      await new Promise((r) => setTimeout(r, 300))
    }
    await startBackend()
  })

  ipcMain.handle('updater:check', async () => {
    if (!app.isPackaged) {
      return {
        ok: false,
        error: 'Auto-update is only available in packaged builds',
        currentVersion: app.getVersion(),
      }
    }
    try {
      const r = await autoUpdater.checkForUpdates()
      return {
        ok: true,
        info: r?.updateInfo ?? null,
        currentVersion: app.getVersion(),
      }
    } catch (err) {
      return {
        ok: false,
        error: (err as Error).message,
        currentVersion: app.getVersion(),
      }
    }
  })

  ipcMain.handle('updater:quit-and-install', () => {
    autoUpdater.quitAndInstall()
  })

  ipcMain.handle('app:get-version', () => app.getVersion())
}

// ----- Auto-update -----------------------------------------------------------

function broadcastUpdater(payload: { kind: string; info?: unknown; error?: string }) {
  settingsWindow?.webContents.send('updater:status', payload)
}

function setupAutoUpdater() {
  autoUpdater.autoDownload = true
  autoUpdater.autoInstallOnAppQuit = true

  autoUpdater.on('checking-for-update', () => {
    broadcastUpdater({ kind: 'checking' })
  })
  autoUpdater.on('update-not-available', (info) => {
    broadcastUpdater({ kind: 'not-available', info })
  })
  autoUpdater.on('error', (err) => {
    console.warn('[updater]', err.message)
    broadcastUpdater({ kind: 'error', error: err.message })
  })
  autoUpdater.on('update-available', (info) => {
    console.log('[updater] update available:', info.version)
    broadcastUpdater({ kind: 'available', info })
  })
  autoUpdater.on('download-progress', (progress) => {
    broadcastUpdater({ kind: 'progress', info: progress })
  })
  autoUpdater.on('update-downloaded', (info) => {
    console.log('[updater] update downloaded:', info.version)
    broadcastUpdater({ kind: 'downloaded', info })
  })

  if (app.isPackaged) {
    setTimeout(() => {
      autoUpdater.checkForUpdates().catch(() => {})
    }, 8_000)
  }
}

// ----- Lifecycle -------------------------------------------------------------

const gotLock = app.requestSingleInstanceLock()
if (!gotLock) {
  app.quit()
} else {
  app.on('second-instance', () => {
    createSettingsWindow()
  })

  app.whenReady().then(async () => {
    electronApp.setAppUserModelId('com.virtualtcu.app')
    app.on('browser-window-created', (_, w) => optimizer.watchWindowShortcuts(w))

    registerIpc()
    createTray()

    try {
      await startBackend()
    } catch (err) {
      console.error('Backend failed to start:', err)
    }

    createSettingsWindow()
    setupAutoUpdater()

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) createSettingsWindow()
    })
  })
}

app.on('before-quit', () => {
  isQuitting = true
  stopBackend()
  tray?.destroy()
  tray = null
})

app.on('window-all-closed', () => {
  // Stay alive in tray on Windows; explicit quit happens via tray menu.
  if (process.platform !== 'win32') {
    isQuitting = true
    tray?.destroy()
    tray = null
    app.quit()
  }
})
