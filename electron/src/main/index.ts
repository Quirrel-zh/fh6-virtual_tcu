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

import { app, BrowserWindow, ipcMain, Menu, shell, Tray, nativeImage } from 'electron'
import { autoUpdater } from 'electron-updater'
import { spawn, ChildProcess } from 'node:child_process'
import { existsSync } from 'node:fs'
import { join } from 'node:path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import { endpointsFromHttpUrl, parseWebUiUrl, resolveBackendEndpoints, type BackendEndpoints } from './backend-config'

const READY_MARKER = '[backend-ready]'

let backendEndpoints: BackendEndpoints = resolveBackendEndpoints()
let backendDataCwd = ''

let settingsWindow: BrowserWindow | null = null
let hudWindow: BrowserWindow | null = null
let tray: Tray | null = null
let backend: ChildProcess | null = null
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

  // Dev: use live Python backend so web-ui changes in virtual_tcu/web/dist
  // are picked up after `npm run build`. Set TCU_USE_FROZEN_BACKEND=1 to
  // test against dist/VirtualTCU/VirtualTCU.exe instead.
  if (!is.dev || process.env['TCU_USE_FROZEN_BACKEND'] === '1') {
    const devExe = join(__dirname, '..', '..', '..', 'dist', 'VirtualTCU', 'VirtualTCU.exe')
    if (existsSync(devExe)) {
      return {
        cmd: devExe,
        args: ['--backend-only'],
        cwd: join(__dirname, '..', '..', '..', 'dist', 'VirtualTCU'),
      }
    }
  }

  return {
    cmd: 'python',
    args: ['-m', 'virtual_tcu', '--backend-only'],
    cwd: join(__dirname, '..', '..', '..'),
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

    backend.stdout?.on('data', (chunk: Buffer) => {
      const text = chunk.toString('utf-8')
      process.stdout.write(`[backend] ${text}`)
      const parsedUrl = parseWebUiUrl(text)
      if (parsedUrl)
        backendEndpoints = endpointsFromHttpUrl(parsedUrl, resolveBackendEndpoints(backendDataCwd))
      if (!settled && text.includes(READY_MARKER)) {
        settled = true
        backendReady = true
        if (!parsedUrl)
          backendEndpoints = resolveBackendEndpoints(backendDataCwd)
        clearTimeout(timeout)
        broadcastBackendReady()
        resolveStart()
      }
    })
    backend.stderr?.on('data', (chunk: Buffer) => {
      process.stderr.write(`[backend!] ${chunk.toString('utf-8')}`)
    })
    backend.on('exit', (code, signal) => {
      console.log(`[backend] exited code=${code} signal=${signal}`)
      backend = null
      backendReady = false
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

function stopBackend(): void {
  if (!backend) return
  try {
    backend.kill()
  } catch (err) {
    console.warn('[backend] kill failed:', err)
  }
  backend = null
  backendReady = false
}

// ----- Windows ---------------------------------------------------------------

function settingsPagePath(): string {
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    return `${process.env['ELECTRON_RENDERER_URL']}/settings-renderer/index.html`
  }
  return join(__dirname, '..', 'renderer', 'settings-renderer', 'index.html')
}

function hudPagePath(): string {
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    return `${process.env['ELECTRON_RENDERER_URL']}/hud-renderer/index.html`
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
      sandbox: false,
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

  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    settingsWindow.loadURL(settingsPagePath())
  } else {
    settingsWindow.loadFile(settingsPagePath())
  }

  settingsWindow.webContents.on('did-finish-load', () => {
    if (backendReady)
      broadcastBackendReady()
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
      sandbox: false,
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

  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    hudWindow.loadURL(hudPagePath())
  } else {
    hudWindow.loadFile(hudPagePath())
  }
}

// ----- Tray ------------------------------------------------------------------

function createTray() {
  // Using an empty image keeps things working without bundling an icon yet.
  // Replace with `nativeImage.createFromPath(join(__dirname, '..', 'icon.png'))`
  // when you ship one.
  const icon = nativeImage.createEmpty()
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
    { label: 'Restart Backend', click: async () => { stopBackend(); await startBackend() } },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => { isQuitting = true; app.quit() },
    },
  ])
  tray.setContextMenu(menu)
  tray.on('click', () => { createSettingsWindow() })
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
    if (typeof url !== 'string' || !/^https?:\/\//i.test(url))
      return
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

function broadcastUpdater(payload: { kind: string, info?: unknown, error?: string }) {
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
})

app.on('window-all-closed', () => {
  // Stay alive in tray on Windows; explicit quit happens via tray menu.
  if (process.platform !== 'win32') {
    isQuitting = true
    app.quit()
  }
})
