<script setup>
import { toRefs } from 'vue'
import { useI18n } from 'vue-i18n'
import { useGraph } from '@/composables/useGraph'
import { card, cardLabel, cardSm, col } from '@/styles/ui'
import { useDashboardPanel } from './dashboard-panel'

const props = defineProps({
  live: { type: Boolean, required: true },
  telemetry: { type: Object, default: null },
})
const { t: i18nT } = useI18n()
const { live, telemetry } = toRefs(props)
const gearLabels = () => ({
  reverse: i18nT('gear.reverse'),
  neutral: i18nT('gear.neutral'),
})
const {
  gearText,
  gearClass,
  gearShifting,
  tachStroke,
  decisionCtx,
  gDotStyle,
  attitudeClass,
  gripWidth,
  gripColor,
  showAirborne,
  showCorrecting,
} = useDashboardPanel(
  () => telemetry.value,
  () => live.value,
  gearLabels,
)
const { canvasRef: graphCanvasRef } = useGraph(() => telemetry.value)
</script>

<template>
  <div :class="col">
    <div v-if="live && telemetry" class="grid h-full grid-rows-[auto_1fr] gap-4">
      <div class="grid items-center gap-5 max-[700px]:grid-cols-1 grid-cols-[200px_1fr]">
        <div class="p-6 text-center" :class="[card]">
          <div :class="cardLabel">
            {{ $t('dashboard.gear') }}
          </div>
          <div
            class="font-mono text-8xl leading-none font-extrabold transition-transform duration-150 max-[700px]:text-6xl"
            :class="[gearClass, gearShifting && 'scale-[1.15]']"
          >
            {{ gearText }}
          </div>
        </div>
        <div class="flex h-full flex-col justify-center p-6" :class="[card]">
          <div :class="cardLabel">
            {{ $t('dashboard.speed') }}
          </div>
          <div class="font-mono text-7xl leading-none font-extrabold max-[700px]:text-5xl">
            <span>{{ Math.round(telemetry.speed_kmh) }}</span>
            <span class="ml-2 text-base font-normal text-tcu-txt-dim">{{ $t('dashboard.kmh') }}</span>
          </div>
        </div>
      </div>

      <div class="grid auto-rows-auto gap-4">
        <div class="flex items-center gap-6 p-5 max-[700px]:flex-col max-[700px]:items-stretch" :class="[card]">
          <div class="relative size-[200px] shrink-0 max-[700px]:size-[140px]">
            <svg class="size-full rotate-135" viewBox="0 0 200 200">
              <circle class="fill-none stroke-tcu-bg-3" cx="100" cy="100" r="85" stroke-width="12" stroke-dasharray="400 535" />
              <circle
                class="fill-none stroke-(length:--dash) transition-[stroke] duration-75"
                cx="100"
                cy="100"
                r="85"
                stroke-width="12"
                stroke-linecap="round"
                :stroke-dasharray="tachStroke.dasharray"
                :style="{ stroke: tachStroke.color, '--dash': tachStroke.dasharray }"
              />
            </svg>
            <div class="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
              <div class="font-mono text-4xl font-bold leading-none max-[700px]:text-2xl">
                {{ Math.round(telemetry.rpm) }}
              </div>
              <div class="mt-1 font-mono text-xs text-tcu-txt-dim">
                / {{ Math.round(telemetry.rpm_max) }}
              </div>
              <div class="mt-1.5 text-[10px] uppercase tracking-widest text-tcu-txt-dim">
                {{ $t('dashboard.rpm') }}
              </div>
            </div>
          </div>
          <div class="flex min-w-0 flex-1 flex-col gap-2">
            <div class="rounded-lg border border-tcu-border bg-linear-to-b from-tcu-bg-1 to-tcu-bg-2 p-3 text-xs">
              <div class="font-mono text-[11px] font-semibold uppercase tracking-wide text-accent">
                {{ telemetry.tcu_state || '—' }}
              </div>
              <div class="mt-0.5 text-tcu-txt-muted">
                {{ telemetry.tcu_state_sub || telemetry.shift_hint || $t('dashboard.awaiting') }}
              </div>
              <div class="mt-1 font-mono text-[10px] text-tcu-txt-dim">
                {{ decisionCtx }}
              </div>
            </div>
            <div class="p-2" :class="[cardSm]">
              <div class="mb-1.5 flex items-center justify-between text-[10px] uppercase tracking-widest text-tcu-txt-dim">
                <span>{{ $t('dashboard.liveTrace') }}</span>
                <span class="flex gap-3 text-[10px]">
                  <span class="flex items-center gap-1 text-accent">
                    <span class="inline-block h-0.5 w-2 bg-current" />{{ $t('dashboard.legendRpm') }}
                  </span>
                  <span class="flex items-center gap-1 text-accent-2">
                    <span class="inline-block h-0.5 w-2 bg-current" />{{ $t('dashboard.legendThr') }}
                  </span>
                  <span class="flex items-center gap-1 text-danger">
                    <span class="inline-block h-0.5 w-2 bg-current" />{{ $t('dashboard.legendBrk') }}
                  </span>
                </span>
              </div>
              <canvas ref="graphCanvasRef" class="block h-20 w-full" />
            </div>
          </div>
        </div>

        <div class="grid gap-4 max-[700px]:grid-cols-1 grid-cols-2">
          <div :class="card">
            <div :class="cardLabel">
              {{ $t('dashboard.inputs') }}
            </div>
            <div class="mb-3 last:mb-0">
              <div class="mb-1 flex justify-between text-xs">
                <span class="text-tcu-txt-muted">{{ $t('dashboard.throttle') }}</span>
                <span class="font-mono text-tcu-txt">{{ Math.round(telemetry.throttle * 100) }}%</span>
              </div>
              <div class="h-1.5 overflow-hidden rounded-sm bg-tcu-bg-3">
                <div class="h-full rounded-sm bg-accent transition-[width] duration-75" :style="{ width: `${telemetry.throttle * 100}%` }" />
              </div>
            </div>
            <div>
              <div class="mb-1 flex justify-between text-xs">
                <span class="text-tcu-txt-muted">{{ $t('dashboard.brake') }}</span>
                <span class="font-mono text-tcu-txt">{{ Math.round(telemetry.brake * 100) }}%</span>
              </div>
              <div class="h-1.5 overflow-hidden rounded-sm bg-tcu-bg-3">
                <div class="h-full rounded-sm bg-danger transition-[width] duration-75" :style="{ width: `${telemetry.brake * 100}%` }" />
              </div>
            </div>
          </div>
          <div class="text-center" :class="[card]">
            <div :class="cardLabel">
              {{ $t('dashboard.tcuState') }}
            </div>
            <div class="mb-1.5 min-h-[18px]">
              <span v-if="showAirborne" class="mr-1 inline-block rounded-full bg-mode-dynamic/20 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-mode-dynamic">{{ $t('dashboard.airborne') }}</span>
              <span v-if="showCorrecting" class="inline-block rounded-full bg-warn/20 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-warn">{{ $t('dashboard.correcting') }}</span>
            </div>
            <div class="mt-1 text-lg font-semibold">
              {{ telemetry.tcu_state || '—' }}
            </div>
            <div class="mt-1.5 text-[11px] text-tcu-txt-dim">
              {{ telemetry.tcu_state_sub || $t('dashboard.awaiting') }}
            </div>
          </div>
        </div>

        <div class="grid gap-4 max-[700px]:grid-cols-2 grid-cols-4">
          <div v-for="(label, key) in { power: 'dashboard.power', torque: 'dashboard.torque', turbo: 'dashboard.turbo', drivetrain: 'dashboard.drivetrain' }" :key="key" class="rounded-lg border border-tcu-border bg-tcu-bg-1 px-3.5 py-3">
            <div class="text-[10px] uppercase tracking-widest text-tcu-txt-dim">
              {{ $t(label) }}
            </div>
            <div class="mt-1 font-mono text-xl font-semibold" :class="key === 'drivetrain' && 'pt-1.5 text-sm'">
              <template v-if="key === 'power'">
                {{ (telemetry.power_kw || 0).toFixed(0) }}<span class="ml-1 text-[11px] font-normal text-tcu-txt-dim">{{ $t('dashboard.kw') }}</span>
              </template>
              <template v-else-if="key === 'torque'">
                {{ (telemetry.torque_nm || 0).toFixed(0) }}<span class="ml-1 text-[11px] font-normal text-tcu-txt-dim">{{ $t('dashboard.nm') }}</span>
              </template>
              <template v-else-if="key === 'turbo'">
                {{ (telemetry.turbo_bar || 0).toFixed(2) }}<span class="ml-1 text-[11px] font-normal text-tcu-txt-dim">{{ $t('dashboard.bar') }}</span>
              </template>
              <template v-else>
                {{ telemetry.drivetrain || '—' }}
              </template>
            </div>
          </div>
        </div>

        <div class="grid gap-4 max-[700px]:grid-cols-1 grid-cols-2">
          <div :class="card">
            <div :class="cardLabel">
              {{ $t('dashboard.gforce') }}
            </div>
            <div class="relative mt-2 h-[130px] rounded-lg bg-tcu-bg-2">
              <div class="absolute top-1/2 right-0 left-0 h-px bg-white/10" />
              <div class="absolute top-0 bottom-0 left-1/2 w-px bg-white/10" />
              <div
                class="absolute size-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-accent-2 shadow-[0_0_10px_var(--color-accent-2)] transition-[left,top] duration-100"
                :style="gDotStyle"
              />
            </div>
            <div class="mt-2 flex justify-between text-[11px] text-tcu-txt-dim">
              <span>{{ $t('dashboard.lat') }}: <span class="font-mono text-tcu-txt">{{ (telemetry.g_lat || 0).toFixed(1) }}</span> g</span>
              <span>{{ $t('dashboard.lon') }}: <span class="font-mono text-tcu-txt">{{ (telemetry.g_lon || 0).toFixed(1) }}</span> g</span>
            </div>
          </div>
          <div class="px-4 py-4 text-center" :class="[card]">
            <div :class="cardLabel">
              {{ $t('dashboard.handling') }}
            </div>
            <div class="mt-1 text-[22px] font-bold" :class="attitudeClass">
              {{ telemetry.attitude || 'NEUTRAL' }}
            </div>
            <div class="mt-1 text-[11px] text-tcu-txt-dim">
              {{ telemetry.attitude_sub || '' }}
            </div>
            <div class="mt-3 h-1 overflow-hidden rounded-sm bg-tcu-bg-3">
              <div class="h-full transition-[width,background] duration-200" :style="{ width: gripWidth, background: gripColor }" />
            </div>
            <div class="mt-1.5 text-[10px] text-tcu-txt-dim">
              {{ telemetry.shift_hint || '' }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="p-8 text-center text-tcu-txt-muted" :class="[card]">
      <h2 class="mb-4 text-lg text-tcu-txt">
        {{ $t('offline.title') }}
      </h2>
      <p class="mb-4">
        {{ $t('offline.lead') }}
      </p>
      <ol class="mx-auto max-w-sm list-decimal pl-5 text-left text-sm leading-relaxed">
        <li>{{ $t('offline.step1') }}</li>
        <li>{{ $t('offline.step2') }}</li>
        <li>{{ $t('offline.step3') }}</li>
        <li>{{ $t('offline.step4') }}</li>
      </ol>
    </div>
  </div>
</template>
