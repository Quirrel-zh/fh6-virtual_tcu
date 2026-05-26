<script setup lang="ts">
import type { TelemetrySnapshot } from '@virtual-tcu/shared/types/telemetry'
import { toRefs } from 'vue'
import { useDashboardChart } from './dashboard-chart'

const props = defineProps<{
  telemetry: TelemetrySnapshot | null
}>()

const { telemetry } = toRefs(props)
const { canvasRef, legend } = useDashboardChart(() => telemetry.value ?? null)
</script>

<template>
  <div class="flex h-full min-h-0 flex-col overflow-hidden rounded-lg border border-tcu-border bg-tcu-bg-1">
    <div class="flex shrink-0 items-center justify-between border-b border-tcu-border px-3 py-2">
      <span class="text-[10px] uppercase tracking-widest text-tcu-txt-dim">Live Telemetry</span>
      <div class="flex flex-wrap items-center gap-x-3 gap-y-1">
        <div
          v-for="item in legend"
          :key="item.key"
          class="flex items-center gap-1.5 text-[10px] tabular-nums"
        >
          <span class="h-2 w-2 rounded-full" :style="{ background: item.color }" />
          <span class="text-tcu-txt-dim">{{ item.label }}</span>
          <span class="font-bold text-white">{{ item.value }}</span>
        </div>
      </div>
    </div>
    <canvas ref="canvasRef" class="block min-h-0 w-full flex-1" />
  </div>
</template>
