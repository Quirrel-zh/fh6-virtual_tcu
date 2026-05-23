import type { ConfigMap } from '@/types/ws'
import { ref, watch } from 'vue'

export function normalizeConfigText(value: string): string {
  return value.trim().toLowerCase()
}

export function useConfigTextInput(
  config: () => ConfigMap,
  configKey: () => string,
  onCommit: (key: string, value: string) => void,
) {
  const draft = ref('')
  let focused = false

  watch(
    () => config()[configKey()],
    (value) => {
      if (!focused)
        draft.value = String(value ?? '')
    },
    { immediate: true },
  )

  function onFocus() {
    focused = true
  }

  function onInput(event: Event) {
    const el = event.target
    if (el instanceof HTMLInputElement)
      draft.value = el.value
  }

  function commit() {
    focused = false
    onCommit(configKey(), normalizeConfigText(draft.value))
  }

  return { draft, onFocus, onInput, commit }
}
