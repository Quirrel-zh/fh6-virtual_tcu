import type { SessionStats, ShiftHistoryItem, TelemetrySnapshot } from '@virtual-tcu/shared/types/telemetry'
import { useSettingsPanel } from './settings-panel'

export function useStatsHistoryPanel(
  telemetry: () => TelemetrySnapshot | null,
  sessionStats: () => SessionStats | null,
  shiftHistory: () => ShiftHistoryItem[],
) {
  const { statsRows, historyItems } = useSettingsPanel(
    () => ({}),
    telemetry,
    sessionStats,
    shiftHistory,
  )

  return { statsRows, historyItems }
}
