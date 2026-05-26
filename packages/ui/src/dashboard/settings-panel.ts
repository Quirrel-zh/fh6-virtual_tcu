import type {
  SessionStats,
  ShiftHistoryItem,
  TelemetrySnapshot,
} from '@virtual-tcu/shared/types/telemetry'
import type { ConfigMap } from '@virtual-tcu/shared/types/ws'
import { SETTING_SLIDERS } from '@virtual-tcu/shared/config/settings'
import { formatDuration, sliderUnit } from '@virtual-tcu/shared/utils/format'
import { computed, ref } from 'vue'

export const TAB_IDS = ['settings', 'stats', 'history', 'extras'] as const
export const CONFIG_TAB_IDS = ['settings', 'extras'] as const

export function hotkeyInputValue(event: Event): string {
  const el = event.target
  if (el instanceof HTMLInputElement) return el.value.trim().toLowerCase()
  return ''
}
export type TabId = (typeof TAB_IDS)[number]

function isShiftHistoryItem(h: unknown): h is ShiftHistoryItem {
  return (
    !!h &&
    typeof h === 'object' &&
    'action' in h &&
    typeof (h as ShiftHistoryItem).action === 'string'
  )
}

export function useSettingsPanel(
  config: () => ConfigMap,
  telemetry: () => TelemetrySnapshot | null,
  sessionStats: () => SessionStats | null,
  shiftHistory: () => ShiftHistoryItem[],
) {
  const activeTab = ref<TabId>('settings')

  const slidersFor = (panel: 'settings' | 'extras') =>
    SETTING_SLIDERS.filter((s) => (s.panel ?? 'settings') === panel)

  const statsRows = computed(() => {
    const s = sessionStats()
    const t = telemetry()
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
      calib: t?.calibrated,
      powerLearned: t?.power_curve_learned,
    }
  })

  const historyItems = computed(() => [...shiftHistory()].reverse().filter(isShiftHistoryItem))

  function configValue(key: string) {
    const v = config()[key]
    if (typeof v === 'number') return v
    if (typeof v === 'boolean') return v ? 1 : 0
    return Number(v) || 0
  }

  function configBool(key: string) {
    return !!config()[key]
  }

  function configText(key: string) {
    return String(config()[key] ?? '')
  }

  function sliderDef(key: string) {
    return SETTING_SLIDERS.find((s) => s.key === key)
  }

  return {
    activeTab,
    slidersFor,
    statsRows,
    historyItems,
    configValue,
    configBool,
    configText,
    sliderDef,
  }
}

export { sliderUnit }
