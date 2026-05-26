<script setup lang="ts">
import type { SessionStats, ShiftHistoryItem, TelemetrySnapshot } from '@virtual-tcu/shared/types/telemetry'
import { ref, toRefs } from 'vue'
import { col, sectionTitle, statRow, tabActive, tabBase } from '../styles/ui'
import { useStatsHistoryPanel } from './stats-history-panel'

const props = withDefaults(defineProps<{
  telemetry?: TelemetrySnapshot | null
  sessionStats?: SessionStats | null
  shiftHistory?: ShiftHistoryItem[]
}>(), {
  telemetry: null,
  sessionStats: null,
  shiftHistory: () => [],
})

const { telemetry, sessionStats, shiftHistory } = toRefs(props)
const activeTab = ref('stats')

const { statsRows, historyItems } = useStatsHistoryPanel(
  () => telemetry.value,
  () => sessionStats.value,
  () => shiftHistory.value,
)
</script>

<template>
  <div :class="col">
    <div class="border-tcu-border mb-4 flex gap-1 border-b">
      <button
        type="button"
        :class="[tabBase, activeTab === 'stats' && tabActive]"
        @click="activeTab = 'stats'"
      >
        {{ $t('tabs.stats') }}
      </button>
      <button
        type="button"
        :class="[tabBase, activeTab === 'history' && tabActive]"
        @click="activeTab = 'history'"
      >
        {{ $t('tabs.history') }}
      </button>
    </div>

    <div v-show="activeTab === 'stats'">
      <h3 :class="sectionTitle">
        {{ $t('stats.title') }}
      </h3>
      <template v-if="statsRows">
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.duration') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{ statsRows.duration }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.totalShifts') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{ statsRows.total }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.upshifts') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{ statsRows.upshifts }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.downshifts') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{ statsRows.downshifts }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.kickdowns') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{ statsRows.kickdowns }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.brakeDowns') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{ statsRows.brakeDowns }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.predictives') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{ statsRows.predictives }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.launches') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{ statsRows.launches }}</span>
        </div>
        <h3 class="mt-5" :class="[sectionTitle]">
          {{ $t('stats.performance') }}
        </h3>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.peakRpm') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{ statsRows.peakRpm }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.peakSpeed') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{ statsRows.peakSpeed }} km/h</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.peakGLat') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{ statsRows.peakGLat }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.peakGLon') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{ statsRows.peakGLon }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.peakPower') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{ statsRows.peakPower }} kW</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.avgThrottle') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{ statsRows.avgThr }}%</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.carsDriven') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{ statsRows.cars }}</span>
        </div>
        <h3 class="mt-5" :class="[sectionTitle]">
          {{ $t('stats.learning') }}
        </h3>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.gearRatios') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{
            statsRows.calib ? $t('stats.learned') : $t('stats.learningStatus')
          }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.powerCurve') }}</span>
          <span class="text-tcu-txt font-mono font-semibold">{{
            statsRows.powerLearned ? $t('stats.learned') : $t('stats.learningStatus')
          }}</span>
        </div>
      </template>
      <div v-else class="text-tcu-txt-dim py-5 text-center text-xs">
        {{ $t('connection.standby') }}
      </div>
    </div>

    <div v-show="activeTab === 'history'">
      <h3 :class="sectionTitle">
        {{ $t('history.title') }}
      </h3>
      <div class="flex max-h-[calc(100vh-280px)] flex-col gap-1 overflow-y-auto">
        <div v-if="historyItems.length === 0" class="text-tcu-txt-dim py-5 text-center text-xs">
          {{ $t('history.empty') }}
        </div>
        <div
          v-for="(h, i) in historyItems"
          :key="i"
          class="border-tcu-border bg-tcu-bg-1 grid grid-cols-[auto_auto_1fr_auto] items-center gap-2.5 rounded-md border px-2.5 py-1.5 font-mono text-[11px]"
        >
          <span class="text-sm font-bold" :class="h.action === 'UP' ? 'text-accent' : 'text-warn'">
            {{ h.action === 'UP' ? '↑' : '↓' }}
          </span>
          <span class="text-tcu-txt-muted">gear {{ h.gear }}</span>
          <span class="text-tcu-txt-dim text-[10px] tracking-wide uppercase">{{
            h.reason || h.rule
          }}</span>
          <span class="text-tcu-txt-dim text-right text-[10px]">
            {{ new Date(h.ts * 1000).toTimeString().slice(0, 8) }} · {{ h.rpm_pct }}% ·
            {{ h.throttle }}%T {{ h.brake }}%B
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
