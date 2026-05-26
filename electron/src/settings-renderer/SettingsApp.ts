import type { SliderDef } from '@virtual-tcu/shared/config/settings'
import type { AppLocale } from '@virtual-tcu/shared/i18n'
import { useNetworkSettings } from '@virtual-tcu/shared/composables/useNetworkSettings'
import { useTcuStore } from '@virtual-tcu/shared/composables/useTcuStore'
import { DRIVE_MODES } from '@virtual-tcu/shared/config/modes'
import {
  FEATURE_TOGGLES,
  HOTKEY_FIELDS,
  SETTING_SLIDERS,
  SHIFT_KEY_FIELDS,
} from '@virtual-tcu/shared/config/settings'
import { setAppLocale } from '@virtual-tcu/shared/i18n'
import { formatDuration, sliderUnit } from '@virtual-tcu/shared/utils/format'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUpdater } from './useUpdater'

export const GITHUB_REPO_URL = 'https://github.com/Forza-Love/fh6-virtual_tcu'

export type SettingsTabKey = 'overview' | 'config' | 'advanced' | 'stats' | 'history' | 'about'

export function useSettingsApp() {
  const { t, locale } = useI18n()
  const activeTab = ref<SettingsTabKey>('overview')
  const store = useTcuStore()

  const tabs: { key: SettingsTabKey; i18nKey: string }[] = [
    { key: 'overview', i18nKey: 'overview' },
    { key: 'config', i18nKey: 'config' },
    { key: 'advanced', i18nKey: 'advanced' },
    { key: 'stats', i18nKey: 'stats' },
    { key: 'history', i18nKey: 'history' },
    { key: 'about', i18nKey: 'about' },
  ]

  const localeOptions = [
    { label: 'English', value: 'en' },
    { label: '简体中文', value: 'zh-CN' },
  ]

  const driveModes = DRIVE_MODES
  const featureToggles = FEATURE_TOGGLES
  const hotkeyFields = HOTKEY_FIELDS
  const shiftKeyFields = SHIFT_KEY_FIELDS
  const network = useNetworkSettings(() => store.config)

  const settingsSliders = computed<SliderDef[]>(() =>
    SETTING_SLIDERS.filter((s) => (s.panel ?? 'settings') === 'settings'),
  )
  const advancedSliders = computed<SliderDef[]>(() =>
    SETTING_SLIDERS.filter((s) => s.panel === 'extras'),
  )

  const statusLabel = computed(() => {
    if (!store.connected.value)
      return { text: t('connection.disconnected'), kind: 'error' as const }
    if (store.live.value) return { text: t('connection.live'), kind: 'success' as const }
    return { text: t('connection.standby'), kind: 'warning' as const }
  })

  const statsRows = computed(() => {
    const s = store.sessionStats.value
    const tel = store.telemetry.value
    if (!s) return null
    return {
      duration: formatDuration(s.duration_s || 0),
      total: s.upshifts + s.downshifts,
      upshifts: s.upshifts,
      downshifts: s.downshifts,
      kickdowns: s.kickdowns,
      brakeDowns: s.brake_downs,
      predictives: s.predictives,
      launches: s.launches,
      peakRpm: Math.round(s.peak_rpm),
      peakSpeed: Math.round(s.peak_speed),
      peakGLat: s.peak_g_lat.toFixed(2),
      peakGLon: s.peak_g_lon.toFixed(2),
      peakPower: Math.round(s.peak_power_kw),
      avgThr: Math.round(s.avg_throttle),
      cars: s.cars_driven,
      calib: tel?.calibrated,
      powerLearned: tel?.power_curve_learned,
    }
  })

  const historyItems = computed(() => [...store.shiftHistory.value].reverse())

  const dashboardUrl = computed(() => store.webUrls.value?.local ?? 'http://127.0.0.1:8765')
  const lanUrl = computed(() => store.webUrls.value?.lan ?? null)
  const udpPort = computed(() =>
    Number(store.config.udp_port ?? store.webUrls.value?.udp_port ?? 5555),
  )

  function configNumber(key: string): number {
    const v = store.config[key]
    if (typeof v === 'number') return v
    if (typeof v === 'boolean') return v ? 1 : 0
    return Number(v) || 0
  }
  function configBool(key: string): boolean {
    return !!store.config[key]
  }
  function configText(key: string): string {
    return String(store.config[key] ?? '')
  }

  const networkApplying = ref(false)
  let applyTimeoutHandle: ReturnType<typeof setTimeout> | null = null

  function clearApplyTimeout() {
    if (applyTimeoutHandle !== null) {
      clearTimeout(applyTimeoutHandle)
      applyTimeoutHandle = null
    }
  }

  function applyNetworkSettings() {
    const parsed = network.validate()
    if (!parsed) return
    networkApplying.value = true
    network.applyOk.value = false
    network.applyError.value = ''
    store.applyNetwork(parsed.host, parsed.webPort, parsed.udpPort)
    // Failsafe: if backend never responds (e.g. WS dropped without reconnect),
    // surface a generic failure after 6s so the button doesn't spin forever.
    clearApplyTimeout()
    applyTimeoutHandle = setTimeout(() => {
      if (networkApplying.value) {
        networkApplying.value = false
        network.markApplyResult(false, 'bindFailed')
      }
    }, 6000)
  }

  function setLocale(value: AppLocale) {
    locale.value = value
    setAppLocale(value)
  }

  function onLogStart(mode: 'events' | 'all') {
    store.send({ type: 'log_start', mode })
  }

  function onLogStop() {
    store.send({ type: 'log_stop' })
  }

  function onExportProfile() {
    store.send({ type: 'export_profile' })
  }

  function onOpenImport() {
    store.openModal('import', t('modal.importTitle'), '')
  }

  function openDashboard() {
    window.tcu?.openDashboard()
  }

  function toggleHud() {
    window.tcu?.toggleHud()
  }

  function openGithub() {
    void window.tcu?.openExternal(GITHUB_REPO_URL)
  }

  watch(
    () => store.webBindStatus.value,
    (status) => {
      if (!status) return
      clearApplyTimeout()
      networkApplying.value = false
      // The store handler already updated config / webUrls / WS URL from the
      // network_changed payload, so markApplyResult() is enough to refresh the
      // drafts and surface the green "applied" badge. Do NOT window.reload()
      // here: the cached backendEndpoints in the main process may still point
      // at the previous bind, and a fresh load would race the WS reconnect and
      // briefly render `config = {}` (which then falls back to the hard-coded
      // defaults in syncFromConfig() — that's where the "everything reset to
      // default" report came from).
      if (status.ok) network.markApplyResult(true)
      else network.markApplyResult(false, status.error ?? 'bindFailed')
      store.webBindStatus.value = null
    },
  )

  watch(
    () => store.connected.value,
    (connected, wasConnected) => {
      if (connected && !wasConnected) network.syncFromConfig()
    },
  )

  const updater = useUpdater()

  return {
    t,
    locale,
    activeTab,
    tabs,
    localeOptions,
    driveModes,
    featureToggles,
    hotkeyFields,
    shiftKeyFields,
    networkDraftHost: network.draftHost,
    networkDraftWebPort: network.draftWebPort,
    networkDraftUdpPort: network.draftUdpPort,
    networkDirty: network.dirty,
    networkApplyError: network.applyError,
    networkApplyOk: network.applyOk,
    networkApplying,
    applyNetworkSettings,
    settingsSliders,
    advancedSliders,
    statusLabel,
    statsRows,
    historyItems,
    dashboardUrl,
    lanUrl,
    udpPort,
    sliderUnit,
    configNumber,
    configBool,
    configText,
    setLocale,
    onLogStart,
    onLogStop,
    onExportProfile,
    onOpenImport,
    openDashboard,
    toggleHud,
    openGithub,
    updater,
    store,
  }
}
