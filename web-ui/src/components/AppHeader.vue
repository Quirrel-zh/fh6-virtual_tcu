<script setup>
import { toRefs } from 'vue'
import { MODE_PILL } from '@/utils/mode-colors'
import { connectionDotClass, headerProps, useHeaderConnectionKey } from './app-header'
import LocaleSwitcher from './LocaleSwitcher.vue'

const props = defineProps(headerProps)
const { connected, live, mode } = toRefs(props)
const connectionKey = useHeaderConnectionKey(connected, live)
const appVersion = `v${__APP_VERSION__}`
</script>

<template>
  <header
    class="flex items-center justify-between border-b border-tcu-border bg-linear-to-b from-tcu-bg-1 to-tcu-bg-0 px-6 py-3.5 max-[700px]:px-3.5"
  >
    <div class="text-xl font-bold tracking-tight">
      {{ $t('app.title') }}
      <span class="ml-2 text-sm font-normal text-tcu-txt-dim">{{ appVersion }}</span>
      <span
        class="ml-3.5 inline-block rounded-full border px-3 py-1 text-[11px] font-bold tracking-widest max-[700px]:hidden"
        :class="MODE_PILL[mode] ?? MODE_PILL.COMFORT"
      >
        {{ mode }}
      </span>
    </div>
    <div class="flex items-center gap-5">
      <LocaleSwitcher />
      <div class="flex items-center gap-2 text-sm text-tcu-txt-muted">
        <span>{{ $t(connectionKey) }}</span>
        <span
          class="size-2 rounded-full transition-colors"
          :class="[
            connectionDotClass(connected, live) === 'live' && 'bg-accent shadow-[0_0_8px_var(--color-accent)]',
            connectionDotClass(connected, live) === 'offline' && 'bg-danger',
            connectionDotClass(connected, live) === '' && 'bg-tcu-txt-dim',
          ]"
        />
      </div>
    </div>
  </header>
</template>
