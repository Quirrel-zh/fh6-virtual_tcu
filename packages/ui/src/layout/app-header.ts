import type { Ref } from 'vue'
import { computed } from 'vue'

export const headerProps = {
  mode: { type: String, required: true },
  connected: { type: Boolean, required: true },
  live: { type: Boolean, required: true },
} as const

export function useHeaderConnectionKey(connected: Ref<boolean>, live: Ref<boolean>) {
  return computed(() => {
    if (!connected.value)
      return 'connection.disconnected'
    return live.value ? 'connection.live' : 'connection.standby'
  })
}

export function connectionDotClass(connected: boolean, live: boolean) {
  if (!connected)
    return 'offline'
  return live ? 'live' : ''
}
