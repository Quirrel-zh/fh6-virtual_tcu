/**
 * Preload for the HUD window. Exposes the backend WS URL plus a few
 * window-control helpers (close, ignore-mouse for click-through mode).
 */

import { contextBridge, ipcRenderer } from 'electron'

const api = {
  getBackendInfo: () => ipcRenderer.invoke('app:get-backend-info'),
  onBackendReady: (cb: (info: { wsUrl?: string }) => void) => {
    const listener = (_: unknown, info: { wsUrl?: string }) => cb(info)
    ipcRenderer.on('backend:ready', listener)
    return () => ipcRenderer.removeListener('backend:ready', listener)
  },
  close: () => ipcRenderer.invoke('hud:close'),
  setIgnoreMouse: (ignore: boolean) => ipcRenderer.invoke('hud:set-ignore-mouse', ignore),
  onBackendExit: (cb: (info: unknown) => void) => {
    const listener = (_: unknown, info: unknown) => cb(info)
    ipcRenderer.on('backend:exit', listener)
    return () => ipcRenderer.removeListener('backend:exit', listener)
  },
}

try {
  contextBridge.exposeInMainWorld('hud', api)
  contextBridge.exposeInMainWorld('isElectron', true)
} catch (err) {
  console.error('[preload/hud] expose failed:', err)
}

export type HudApi = typeof api
