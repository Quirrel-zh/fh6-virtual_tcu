import { computed, onMounted, onUnmounted, ref } from 'vue'

type DriveMode = 'COMFORT' | 'DYNAMIC' | 'RACE' | 'DRIFT' | 'OFFROAD' | 'MANUAL'

interface TelemetrySnapshot {
  gear?: number
  speed_kmh?: number
  rpm?: number
  rpm_max?: number
  rpm_pct?: number
  throttle?: number
  brake?: number
  tcu_state?: string
  shift_hint?: string
}

export function useHudApp() {
  const connected = ref(false)
  const live = ref(false)
  const mode = ref<DriveMode>('COMFORT')
  const telemetry = ref<TelemetrySnapshot>({})
  const clickThrough = ref(false)

  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let cleanupBackendExit: (() => void) | null = null
  let cleanupBackendReady: (() => void) | null = null
  let mouseEventsIgnored = false

  const gearLabel = computed(() => {
    const g = telemetry.value.gear
    if (g === 0) return 'R'
    if (g === 11) return 'N'
    return g != null ? String(g) : '-'
  })

  const speed = computed(() => Math.round(telemetry.value.speed_kmh ?? 0))
  const rpm = computed(() => Math.round(telemetry.value.rpm ?? 0))
  const rpmPct = computed(() => Math.max(0, Math.min(1, telemetry.value.rpm_pct ?? 0)))
  const tcuState = computed(() => telemetry.value.tcu_state ?? 'STANDBY')
  const hint = computed(() => telemetry.value.shift_hint ?? '')

  const modeColor = computed(() => {
    switch (mode.value) {
      case 'COMFORT': return '#0891b2'
      case 'DYNAMIC': return '#65a30d'
      case 'RACE': return '#e11d48'
      case 'DRIFT': return '#d97706'
      case 'OFFROAD': return '#ea580c'
      case 'MANUAL': return '#64748b'
      default: return '#64748b'
    }
  })

  const rpmBarColor = computed(() => {
    if (rpmPct.value > 0.92) return '#dc2626'
    if (rpmPct.value > 0.78) return '#d97706'
    return '#16a34a'
  })

  const gearColor = computed(() => {
    if (tcuState.value === 'SHIFTING') return '#7c3aed'
    if (gearLabel.value === 'R') return '#d97706'
    return '#111827'
  })

  const gearStyle = computed(() => {
    if (!clickThrough.value) return { color: gearColor.value }
    if (tcuState.value === 'SHIFTING') return { color: '#ddd6fe' }
    if (gearLabel.value === 'R') return { color: '#fde68a' }
    return { color: '#ffffff' }
  })

  async function connectWs() {
    const fallbackUrl = 'ws://127.0.0.1:8765/ws'
    let url = fallbackUrl
    try {
      if (window.hud) {
        const info = await window.hud.getBackendInfo()
        url = info.wsUrl || fallbackUrl
      }
    }
    catch {
      // use fallback
    }

    if (ws) {
      ws.close()
      ws = null
    }

    try {
      ws = new WebSocket(url)
    }
    catch (err) {
      console.warn('[hud] WS construct failed', err)
      scheduleReconnect()
      return
    }

    ws.onopen = () => {
      connected.value = true
    }
    ws.onclose = () => {
      connected.value = false
      live.value = false
      scheduleReconnect()
    }
    ws.onerror = () => {
      ws?.close()
    }
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data as string)
        switch (msg.type) {
          case 'init':
            if (msg.data?.mode) mode.value = msg.data.mode
            if (typeof msg.data?.live === 'boolean') live.value = msg.data.live
            break
          case 'telemetry':
            telemetry.value = msg.data ?? {}
            break
          case 'state':
            if (msg.data?.mode) mode.value = msg.data.mode
            if (typeof msg.data?.live === 'boolean') live.value = msg.data.live
            break
        }
      }
      catch {
        /* ignore */
      }
    }
  }

  function scheduleReconnect() {
    if (reconnectTimer) return
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null
      connectWs()
    }, 1500)
  }

  function close() {
    window.hud?.close()
  }

  function applyMouseIgnore(ignore: boolean) {
    if (mouseEventsIgnored === ignore) return
    mouseEventsIgnored = ignore
    window.hud?.setIgnoreMouse(ignore)
  }

  function syncClickThroughMouse(e: MouseEvent) {
    if (!clickThrough.value) {
      applyMouseIgnore(false)
      return
    }

    const el = document.elementFromPoint(e.clientX, e.clientY)
    applyMouseIgnore(!el?.closest('.interactive'))
  }

  function onMouseLeave() {
    if (clickThrough.value) applyMouseIgnore(true)
  }

  function toggleClickThrough(e: MouseEvent) {
    clickThrough.value = !clickThrough.value
    if (clickThrough.value) syncClickThroughMouse(e)
    else applyMouseIgnore(false)
  }

  onMounted(() => {
    void connectWs()
    if (window.hud) {
      cleanupBackendExit = window.hud.onBackendExit(() => {
        connected.value = false
        live.value = false
      })
      cleanupBackendReady = window.hud.onBackendReady(() => {
        if (reconnectTimer) {
          clearTimeout(reconnectTimer)
          reconnectTimer = null
        }
        void connectWs()
      })
    }
  })

  onUnmounted(() => {
    if (reconnectTimer) clearTimeout(reconnectTimer)
    ws?.close()
    ws = null
    cleanupBackendExit?.()
    cleanupBackendReady?.()
  })

  return {
    connected,
    live,
    mode,
    gearLabel,
    speed,
    rpm,
    rpmPct,
    tcuState,
    hint,
    modeColor,
    rpmBarColor,
    gearColor,
    gearStyle,
    clickThrough,
    close,
    toggleClickThrough,
    syncClickThroughMouse,
    onMouseLeave,
  }
}
