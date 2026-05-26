import type { TelemetrySnapshot } from '@virtual-tcu/shared/types/telemetry'
import type { Ref } from 'vue'
import { computed } from 'vue'

export function useDashboardPanel(telemetry: Ref<TelemetrySnapshot | null>) {
  const t = computed(() => (telemetry.value || {}) as Partial<TelemetrySnapshot>)
  const speed = computed(() => Math.round(t.value.speed_kmh || 0))
  const rpm = computed(() => Math.round(t.value.rpm || 0))
  const rpmMax = computed(() => Math.round(t.value.rpm_max || 8000))
  const rpmPct = computed(() => t.value.rpm_pct || 0)
  const powerKw = computed(() => Math.round(t.value.power_kw || 0))
  const torqueNm = computed(() => Math.round(t.value.torque_nm || 0))
  const turboBar = computed(() => (t.value.turbo_bar || 0).toFixed(2))

  const throttle = computed(() => (t.value.throttle || 0) * 100)
  const brake = computed(() => (t.value.brake || 0) * 100)
  const clutch = computed(() => (t.value.clutch_raw ? (t.value.clutch_raw / 255) * 100 : 0))

  const gLat = computed(() => t.value.g_lat || 0)
  const gLon = computed(() => t.value.g_lon || 0)
  const gripUsage = computed(() => (t.value.grip_usage || 0) * 100)

  const state = computed(() => t.value.tcu_state || 'STANDBY')
  const subState = computed(() => t.value.tcu_state_sub || 'AWAITING TELEMETRY')
  const attitude = computed(() => t.value.attitude || 'NEUTRAL')
  const hint = computed(() => t.value.shift_hint || '')

  const isAirborne = computed(() => t.value.airborne || false)
  const isYawLocked = computed(() => t.value.yaw_transient || false)

  const gear = computed(() => {
    const g = t.value.gear
    if (g === 0) return 'R'
    if (g === 11) return 'N'
    return g || '-'
  })

  const gDotStyle = computed(() => {
    const maxG = 1.5
    const x = Math.max(-maxG, Math.min(maxG, gLat.value))
    const y = Math.max(-maxG, Math.min(maxG, gLon.value))
    const px = 50 + (x / maxG) * 50
    const py = 50 - (y / maxG) * 50
    return { left: `${px}%`, top: `${py}%` }
  })

  return {
    t,
    speed,
    rpm,
    rpmMax,
    rpmPct,
    powerKw,
    torqueNm,
    turboBar,
    throttle,
    brake,
    clutch,
    gLat,
    gLon,
    gripUsage,
    state,
    subState,
    attitude,
    hint,
    isAirborne,
    isYawLocked,
    gear,
    gDotStyle,
  }
}

export function getLedColor(index: number, pct: number) {
  const totalLeds = 20
  const threshold = index / totalLeds

  if (pct < threshold) return 'bg-tcu-bg-3 shadow-none'

  if (index > 17) return 'bg-blue-500 shadow-[0_0_12px_rgba(59,130,246,0.9)]'
  if (index > 13) return 'bg-red-500 shadow-[0_0_12px_rgba(239,68,68,0.9)]'
  if (index > 8) return 'bg-yellow-400 shadow-[0_0_10px_rgba(250,204,21,0.8)]'
  return 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.8)]'
}
