import type { ConfigMap } from '../types/ws'
import { computed, ref, watch } from 'vue'

export function isValidBindHost(host: string): boolean {
  const h = host.trim()
  if (h === '0.0.0.0' || h === '127.0.0.1')
    return true
  const parts = h.split('.')
  if (parts.length !== 4)
    return false
  return parts.every((p) => {
    const n = Number(p)
    return Number.isInteger(n) && n >= 0 && n <= 255
  })
}

export function isValidUdpPort(port: number): boolean {
  return Number.isInteger(port) && port >= 1 && port <= 65535
}

export function isValidWebPort(port: number): boolean {
  return Number.isInteger(port) && port >= 1024 && port <= 65535
}

export function useNetworkSettings(config: () => ConfigMap) {
  const draftHost = ref('')
  const draftWebPort = ref('')
  const draftUdpPort = ref('')
  const applyError = ref('')
  const applyOk = ref(false)

  function syncFromConfig() {
    draftHost.value = String(config().web_host ?? '127.0.0.1')
    draftWebPort.value = String(config().web_port ?? 8765)
    draftUdpPort.value = String(config().udp_port ?? 5555)
    applyError.value = ''
    applyOk.value = false
  }

  watch(config, syncFromConfig, { immediate: true, deep: true })

  const dirty = computed(() =>
    draftHost.value.trim() !== String(config().web_host ?? '')
    || String(draftWebPort.value).trim() !== String(config().web_port ?? '')
    || String(draftUdpPort.value).trim() !== String(config().udp_port ?? ''),
  )

  function validate(): { host: string, webPort: number, udpPort: number } | null {
    const host = draftHost.value.trim()
    const webPort = Number(draftWebPort.value.trim())
    const udpPort = Number(draftUdpPort.value.trim())
    if (!isValidBindHost(host)) {
      applyError.value = 'invalidHost'
      return null
    }
    if (!isValidWebPort(webPort)) {
      applyError.value = 'invalidPort'
      return null
    }
    if (!isValidUdpPort(udpPort)) {
      applyError.value = 'invalidUdpPort'
      return null
    }
    applyError.value = ''
    return { host, webPort, udpPort }
  }

  function markApplyResult(ok: boolean, error = '') {
    applyOk.value = ok
    applyError.value = error
    if (ok)
      syncFromConfig()
  }

  return {
    draftHost,
    draftWebPort,
    draftUdpPort,
    dirty,
    applyError,
    applyOk,
    syncFromConfig,
    validate,
    markApplyResult,
  }
}
