import { onMounted, onUnmounted, ref } from 'vue'
import type { UpdaterStatus } from '../preload/main'

export type UpdaterState =
  | { kind: 'idle' }
  | { kind: 'checking' }
  | { kind: 'available', version: string }
  | { kind: 'not-available' }
  | { kind: 'progress', percent: number }
  | { kind: 'downloaded', version: string }
  | { kind: 'error', message: string }

export function useUpdater() {
  const state = ref<UpdaterState>({ kind: 'idle' })
  const currentVersion = ref<string>('')
  let unsubscribe: (() => void) | null = null

  onMounted(async () => {
    if (!window.tcu) return
    currentVersion.value = await window.tcu.getAppVersion()
    unsubscribe = window.tcu.onUpdaterStatus((status: UpdaterStatus) => {
      switch (status.kind) {
        case 'checking':
          state.value = { kind: 'checking' }
          break
        case 'available':
          state.value = { kind: 'available', version: status.info?.version ?? '' }
          break
        case 'not-available':
          state.value = { kind: 'not-available' }
          break
        case 'progress':
          state.value = { kind: 'progress', percent: Math.round(status.info?.percent ?? 0) }
          break
        case 'downloaded':
          state.value = { kind: 'downloaded', version: status.info?.version ?? '' }
          break
        case 'error':
          state.value = { kind: 'error', message: status.error ?? 'Unknown error' }
          break
      }
    })
  })

  onUnmounted(() => unsubscribe?.())

  async function check() {
    state.value = { kind: 'checking' }
    const r = await window.tcu?.checkForUpdates()
    if (r && !r.ok && r.error)
      state.value = { kind: 'error', message: r.error }
  }

  function install() {
    window.tcu?.quitAndInstallUpdate()
  }

  return { state, currentVersion, check, install }
}
