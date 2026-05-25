import type { LogStatus, ShiftHistoryItem, TelemetrySnapshot } from '../types/telemetry'
import type { DriveMode, WsInbound } from '../types/ws'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { TcuWsClient } from '../api/ws-client'

const client = new TcuWsClient()

/** Read-only WebSocket store for the browser dashboard (no config writes). */
export function useTcuViewStore() {
  const connected = ref(false)
  const live = ref(false)
  const mode = ref<DriveMode>('COMFORT')
  const shiftCount = ref(0)
  const packetsTotal = ref(0)
  const telemetry = ref<TelemetrySnapshot | null>(null)
  const logStatus = ref<LogStatus | null>(null)
  const shiftHistory = ref<ShiftHistoryItem[]>([])
  const watchdogStuck = ref(false)

  function handle(msg: WsInbound) {
    switch (msg.type) {
      case 'init':
        mode.value = msg.data.mode
        live.value = msg.data.live
        shiftCount.value = msg.data.shift_count
        packetsTotal.value = msg.data.packets_total
        logStatus.value = msg.data.log_status
        connected.value = true
        break
      case 'telemetry':
        telemetry.value = msg.data
        if (msg.data.shift_history) shiftHistory.value = msg.data.shift_history
        if (msg.data.log_status) logStatus.value = msg.data.log_status
        watchdogStuck.value = !!msg.data.watchdog_stuck
        break
      case 'state':
        if (msg.data.mode) mode.value = msg.data.mode
        if (msg.data.live !== undefined) live.value = msg.data.live
        if (msg.data.shift_count !== undefined) shiftCount.value = msg.data.shift_count
        if (msg.data.packets_total !== undefined) packetsTotal.value = msg.data.packets_total
        break
      case 'log_status':
        logStatus.value = msg.data
        break
    }
  }

  const sessionStats = computed(() => telemetry.value?.session_stats ?? null)

  const connectionLabel = computed(() => {
    if (!connected.value) return 'disconnected'
    return live.value ? 'live' : 'standby'
  })

  onMounted(() => {
    client.onMessage(handle)
    client.onConnectionChange((open) => {
      if (!open) {
        connected.value = false
        live.value = false
      }
    })
    client.connect()
  })

  onUnmounted(() => {
    client.disconnect()
  })

  return {
    connected,
    live,
    mode,
    shiftCount,
    packetsTotal,
    telemetry,
    logStatus,
    shiftHistory,
    watchdogStuck,
    sessionStats,
    connectionLabel,
  }
}
