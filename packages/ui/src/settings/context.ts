import type { SliderDef } from '@virtual-tcu/shared/config/settings'
import type { InjectionKey, Ref } from 'vue'

export interface StatsRows {
  duration: string
  total: number
  upshifts: number
  downshifts: number
  kickdowns: number
  brakeDowns: number
  predictives: number
  launches: number
  peakRpm: number
  peakSpeed: number
  peakGLat: string
  peakGLon: string
  peakPower: number
  avgThr: number
  cars: number
  calib: boolean | undefined
  powerLearned: boolean | undefined
}

export interface ShiftHistoryItem {
  action: string
  gear: number
  reason: string
  rule: string
  ts: number
  rpm_pct: number
  throttle: number
  brake: number
}

export interface SettingsContext {
  t: (key: string, params?: Record<string, unknown>) => string
  locale: Ref<string>
  store: {
    connected: Ref<boolean>
    live: Ref<boolean>
    mode: Ref<string>
    config: Record<string, unknown>
    telemetry: Ref<Record<string, unknown> | null>
    sessionStats: Ref<Record<string, unknown> | null>
    shiftHistory: Ref<Array<Record<string, unknown>>>
    logStatus: Ref<{ recording: boolean; packets: number; size_kb: number } | null>
    packetsTotal: Ref<number>
    webUrls: Ref<{ local?: string; lan?: string; udp_port?: number } | null>
    modal: { open: boolean; title: string; text: string; readOnly: boolean; mode: string }
    setMode: (id: string) => void
    setConfig: (key: string, value: unknown) => void
    resetConfig: () => void
    send: (msg: Record<string, unknown>) => void
    closeModal: () => void
    confirmModal: () => void
    openModal: (mode: string, title: string, text: string) => void
  }
  driveModes: Array<{ id: string; i18nKey: string }>
  featureToggles: Array<{ key: string; i18nKey: string }>
  hotkeyFields: Array<{ key: string; i18nKey: string; placeholder: string }>
  shiftKeyFields: Array<{ key: string; i18nKey: string; placeholder: string }>
  outputModeOptions: ReadonlyArray<{ value: string; i18nKey: string }>
  gamepadButtonOptions: ReadonlyArray<{ value: string; label: string }>
  gamepadButtonFields: ReadonlyArray<{ key: string; i18nKey: string; placeholder: string }>
  settingsSliders: Ref<SliderDef[]>
  advancedSliders: Ref<SliderDef[]>
  statusLabel: Ref<{ text: string; kind: 'success' | 'warning' | 'error' }>
  statsRows: Ref<StatsRows | null>
  historyItems: Ref<ShiftHistoryItem[]>
  dashboardUrl: Ref<string>
  lanUrl: Ref<string | null>
  udpPort: Ref<number>
  configNumber: (key: string) => number
  configBool: (key: string) => boolean
  configText: (key: string) => string
  sliderUnit: (s: SliderDef) => string
  networkDraftHost: Ref<string>
  networkDraftWebPort: Ref<string>
  networkDraftUdpPort: Ref<string>
  networkDirty: Ref<boolean>
  networkApplyError: Ref<string>
  networkApplyOk: Ref<boolean>
  networkApplying: Ref<boolean>
  applyNetworkSettings: () => void
  onLogStart: (mode: 'events' | 'all') => void
  onLogStop: () => void
  onExportProfile: () => void
  onOpenImport: () => void
  openDashboard: () => void
  restartBackend: () => void
  toggleHud: () => void
  openGithub: () => void
  updater: {
    state: Ref<{ kind: string; version?: string; percent?: number; message?: string }>
    currentVersion: Ref<string>
    check: () => void
    install: () => void
  }
}

export const settingsContextKey: InjectionKey<SettingsContext> = Symbol('settings-context')
