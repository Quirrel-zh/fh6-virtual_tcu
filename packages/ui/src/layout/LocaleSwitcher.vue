<script setup lang="ts">
import { localeOptions, onLocaleChange } from './locale-switcher'
</script>

<template>
  <label class="flex items-center gap-2 text-xs text-tcu-txt-muted">
    <span class="text-tcu-txt-dim">{{ $t('locale.label') }}</span>
    <select
      class="rounded-md border border-tcu-border bg-tcu-bg-2 px-2 py-1 text-xs text-tcu-txt"
      :value="$i18n.locale"
      @change="onLocaleChange"
    >
      <option v-for="opt in localeOptions" :key="opt.value" :value="opt.value">
        {{ $t(opt.labelKey) }}
      </option>
    </select>
  </label>
</template>
