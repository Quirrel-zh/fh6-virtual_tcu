/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface HudApi {
  getBackendInfo: () => Promise<{ url: string; wsUrl: string; ready: boolean }>
  close: () => Promise<void>
  setIgnoreMouse: (ignore: boolean) => Promise<void>
  onBackendExit: (cb: (info: unknown) => void) => () => void
}

declare global {
  interface Window {
    hud?: HudApi
    isElectron?: boolean
  }
}

export {}
