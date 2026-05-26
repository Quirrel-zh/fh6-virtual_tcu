import type { LogStatus, TelemetrySnapshot } from '@virtual-tcu/shared/types/telemetry'
import type { Ref } from 'vue'
import { computed } from 'vue'

export function useModeSidebar(
  telemetry: Ref<TelemetrySnapshot | null>,
  logStatus: Ref<LogStatus | null>,
) {
  const calibClass = computed(() => (telemetry.value?.calibrated ? 'calibrated' : 'learning'))

  const sportIndex = computed(() => (telemetry.value?.drive_style_index ?? 0).toFixed(2))
  const sportBarWidth = computed(
    () => `${((telemetry.value?.drive_style_index ?? 0) * 100).toFixed(0)}%`,
  )
  const sportRegime = computed(() => telemetry.value?.drive_style_regime || 'CRUISE')

  const hasTorque = computed(() => telemetry.value?.peak_torque_rpm_pct != null)
  const hasPower = computed(() => telemetry.value?.peak_power_rpm_pct != null)

  const peakTorqueText = computed(() => {
    const p = telemetry.value?.peak_torque_rpm_pct
    return p == null ? '' : `${Math.round(p * 100)}% RPM`
  })

  const peakPowerText = computed(() => {
    const p = telemetry.value?.peak_power_rpm_pct
    return p == null ? '' : `${Math.round(p * 100)}% RPM`
  })

  const peakRpm = computed(() => Math.round(telemetry.value?.peak_rpm ?? 0))
  const peakG = computed(() => (telemetry.value?.peak_g ?? 0).toFixed(2))

  const logMode = computed(() =>
    logStatus.value?.mode === 'off' ? '—' : (logStatus.value?.mode ?? '—'),
  )
  const logSize = computed(() => `${logStatus.value?.size_kb ?? 0} KB`)

  return {
    calibClass,
    sportIndex,
    sportBarWidth,
    sportRegime,
    hasTorque,
    hasPower,
    peakTorqueText,
    peakPowerText,
    peakRpm,
    peakG,
    logMode,
    logSize,
  }
}
