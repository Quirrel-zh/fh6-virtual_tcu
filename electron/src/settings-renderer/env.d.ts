/// <reference types="vite/client" />

import type { TcuMainApi, UpdaterCheckResult, UpdaterStatus } from '../preload/main'

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<object, object, unknown>
  export default component
}

declare global {
  const __APP_VERSION__: string
  interface Window {
    tcu?: TcuMainApi
    isElectron?: boolean
  }
}

export type { UpdaterCheckResult, UpdaterStatus }
export {}
