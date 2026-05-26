import type { TelemetrySnapshot } from '@virtual-tcu/shared/types/telemetry'
import { gearDisplay } from '@virtual-tcu/shared/utils/format'
import { computed, ref, watch } from 'vue'

const TACH_CIRCUMFERENCE = 2 * Math.PI * 85
const TACH_ARC = TACH_CIRCUMFERENCE * 0.75

export function useDashboardPanel(
  telemetry: () => TelemetrySnapshot | null,
  live: () => boolean,
  gearLabels: () => { reverse: string; neutral: string },
) {
  const gearShifting = ref(false)

  const t = computed(telemetry)
  const gearText = computed(() => {
    const td = t.value
    if (!td) return 'N'
    return gearDisplay(td.gear, gearLabels())
  })

  const gearClass = computed(() => {
    const g = t.value?.gear
    if (g === 0) return 'text-warn'
    if (g === -1) return 'text-tcu-txt-dim'
    return 'text-accent'
  })

  watch(gearText, (n, o) => {
    if (o !== undefined && n !== o) {
      gearShifting.value = true
      setTimeout(() => {
        gearShifting.value = false
      }, 150)
    }
  })

  const tachStroke = computed(() => {
    const pct = Math.max(0, Math.min(1, t.value?.rpm_pct || 0))
    return {
      dasharray: `${TACH_ARC * pct} ${TACH_CIRCUMFERENCE}`,
      color: tachColor(pct),
    }
  })

  const decisionCtx = computed(() => {
    const td = t.value
    if (!td) return ''
    return `g${td.gear} · ${Math.round((td.rpm_pct || 0) * 100)}% rpm · ${Math.round((td.throttle || 0) * 100)}% thr · ${Math.round((td.brake || 0) * 100)}% brk`
  })

  const gDotStyle = computed(() => {
    const gLat = t.value?.g_lat || 0
    const gLon = t.value?.g_lon || 0
    return {
      left: `${50 + Math.max(-50, Math.min(50, gLat * 25))}%`,
      top: `${50 - Math.max(-50, Math.min(50, gLon * 25))}%`,
    }
  })

  const attitudeClass = computed(() => {
    const key = (t.value?.attitude || 'NEUTRAL').toUpperCase()
    return (
      {
        NEUTRAL: 'text-accent',
        UNDER: 'text-accent-2',
        OVER: 'text-warn',
        SPIN: 'text-danger',
      }[key] ?? 'text-accent'
    )
  })
  const gripWidth = computed(() => `${(t.value?.grip_usage || 0) * 100}%`)
  const gripColor = computed(() =>
    (t.value?.grip_usage || 0) > 0.85 ? 'var(--danger)' : 'var(--accent)',
  )

  const showAirborne = computed(() => !!t.value?.airborne)
  const showCorrecting = computed(() => !!t.value?.yaw_transient)

  return {
    t,
    live: computed(live),
    gearText,
    gearClass,
    gearShifting,
    tachStroke,
    decisionCtx,
    gDotStyle,
    attitudeClass,
    gripWidth,
    gripColor,
    showAirborne,
    showCorrecting,
  }
}

function tachColor(pct: number) {
  if (pct >= 0.93) return '#ef4444'
  if (pct >= 0.8) return '#fb923c'
  if (pct >= 0.65) return '#fbbf24'
  return '#4ade80'
}
