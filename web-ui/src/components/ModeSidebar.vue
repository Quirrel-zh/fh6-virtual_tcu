<script setup>
  import { toRefs } from 'vue'
  import { DRIVE_MODES } from '@/config/modes'
  import {
    actionBtn,
    actionBtnDanger,
    actionBtnPrimary,
    badgeCalibrated,
    badgeLearning,
    cardSm,
    col,
    sectionTitle,
  } from '@/styles/ui'
  import { modeBtnClass, REGIME_PILL } from '@/utils/mode-colors'
  import { useModeSidebar } from './mode-sidebar'

  const props = defineProps({
    mode: { type: String, required: true },
    shiftCount: { type: Number, required: true },
    packetsTotal: { type: Number, required: true },
    telemetry: { type: Object, default: null },
    logStatus: { type: Object, default: null },
    interactive: { type: Boolean, default: true },
  })
  const emit = defineEmits(['setMode', 'logStart', 'logStop'])

  const { telemetry, logStatus, interactive } = toRefs(props)
  const {
    sportIndex,
    sportBarWidth,
    sportRegime,
    hasTorque,
    hasPower,
    peakTorqueText,
    peakPowerText,
    peakRpm,
    peakG,
    logMode,
    logSize,
  } = useModeSidebar(telemetry, logStatus)

  const isCalibrated = () => !!telemetry.value?.calibrated
  const isRecording = () => !!logStatus.value?.recording
</script>

<template>
  <div :class="col">
    <h3 :class="sectionTitle">
      {{ $t('modes.title') }}
    </h3>
    <template v-if="interactive">
      <button
        v-for="m in DRIVE_MODES"
        :key="m.id"
        type="button"
        :class="modeBtnClass(m.id, mode === m.id)"
        @click="emit('setMode', m.id)"
      >
        <span class="font-medium">{{ $t(`modes.${m.i18nKey}.name`) }}</span>
        <span
          class="bg-tcu-bg-3 text-tcu-txt-dim rounded px-1.5 py-0.5 text-[10px] tracking-wide uppercase"
          :class="mode === m.id && 'bg-white/5 text-current'"
        >
          {{ $t(`modes.${m.i18nKey}.tag`) }}
        </span>
      </button>
    </template>
    <template v-else>
      <div
        v-for="m in DRIVE_MODES"
        :key="m.id"
        class="flex items-center justify-between rounded-md border px-3 py-2.5 text-sm"
        :class="
          mode === m.id
            ? modeBtnClass(m.id, true)
            : 'border-tcu-border bg-tcu-bg-1 text-tcu-txt-dim opacity-60'
        "
      >
        <span class="font-medium">{{ $t(`modes.${m.i18nKey}.name`) }}</span>
        <span class="text-[10px] tracking-wide uppercase">{{ $t(`modes.${m.i18nKey}.tag`) }}</span>
      </div>
    </template>
    <div class="bg-tcu-bg-1 text-tcu-txt-dim mt-3 rounded-md p-2.5 text-center text-xs">
      {{ $t('modes.hotkeyHintBefore') }}<kbd>F9</kbd><br />{{ $t('modes.hotkeyHintAfter') }}
    </div>

    <h3 class="mt-6" :class="[sectionTitle]">
      {{ $t('calibration.title') }}
    </h3>
    <div :class="cardSm">
      <div class="text-tcu-txt-dim mb-1.5 text-[11px]">
        {{ $t('calibration.currentCar') }}
      </div>
      <span :class="isCalibrated() ? badgeCalibrated : badgeLearning">
        {{ isCalibrated() ? $t('calibration.calibrated') : $t('calibration.learning') }}
      </span>
      <div class="text-tcu-txt-dim mt-2 text-[11px] leading-snug">
        {{ $t('calibration.hint') }}
      </div>
    </div>

    <h3 class="mt-6" :class="[sectionTitle]">
      {{ $t('driveStyle.title') }}
    </h3>
    <div class="mt-2.5" :class="[cardSm]">
      <div
        class="text-tcu-txt-dim mb-1.5 flex items-baseline justify-between text-[11px] tracking-widest uppercase"
      >
        <span>{{ $t('driveStyle.sportIndex') }}</span>
        <span class="text-tcu-txt font-mono text-xs font-semibold">{{ sportIndex }}</span>
      </div>
      <div class="bg-tcu-bg-3 relative h-1.5 overflow-hidden rounded-sm">
        <div
          class="from-mode-comfort via-mode-dynamic to-mode-race h-full rounded-sm bg-linear-to-r transition-[width] duration-150"
          :style="{ width: sportBarWidth }"
        />
        <div class="bg-tcu-txt-dim/40 absolute top-[-2px] bottom-[-2px] left-[30%] w-0.5" />
        <div class="bg-tcu-txt-dim/40 absolute top-[-2px] bottom-[-2px] left-[55%] w-0.5" />
      </div>
      <div
        class="text-tcu-txt-dim mt-2 flex items-baseline justify-between text-[11px] tracking-widest uppercase"
      >
        <span>{{ $t('driveStyle.regime') }}</span>
        <span
          class="rounded-full px-2.5 py-0.5 text-[10px] font-bold tracking-wide uppercase"
          :class="REGIME_PILL[sportRegime] ?? REGIME_PILL.CRUISE"
        >
          {{ sportRegime }}
        </span>
      </div>
      <div class="text-tcu-txt-dim mt-1.5 text-[10px] leading-snug">
        {{ $t('driveStyle.hint') }}
      </div>
    </div>

    <h3 class="mt-6" :class="[sectionTitle]">
      {{ $t('powerBand.title') }}
    </h3>
    <div class="text-tcu-txt-muted mt-2.5 text-[11px]" :class="[cardSm]">
      <div class="flex justify-between py-0.5">
        <span class="text-tcu-txt-dim">{{ $t('powerBand.peakTorque') }}</span>
        <span
          class="text-tcu-txt font-mono font-semibold"
          :class="!hasTorque && 'text-warn font-normal'"
        >
          {{ hasTorque ? peakTorqueText : $t('powerBand.learning') }}
        </span>
      </div>
      <div class="flex justify-between py-0.5">
        <span class="text-tcu-txt-dim">{{ $t('powerBand.peakPower') }}</span>
        <span
          class="text-tcu-txt font-mono font-semibold"
          :class="!hasPower && 'text-warn font-normal'"
        >
          {{ hasPower ? peakPowerText : $t('powerBand.learning') }}
        </span>
      </div>
      <div class="text-tcu-txt-dim mt-1.5 text-[10px] leading-snug">
        {{ $t('powerBand.hint') }}
      </div>
    </div>

    <h3 class="mt-6" :class="[sectionTitle]">
      {{ $t('logger.title') }}
    </h3>
    <div class="bg-tcu-bg-1 text-tcu-txt-muted mb-2 rounded-md p-2.5 text-xs">
      <div class="mb-1 flex justify-between">
        <span>{{ $t('logger.status') }}:</span>
        <span :class="isRecording() && 'text-danger font-semibold before:content-[\'\u25CF_\']'">
          {{ isRecording() ? $t('logger.recording') : $t('logger.stopped') }}
        </span>
      </div>
      <div class="mb-1 flex justify-between">
        <span>{{ $t('logger.mode') }}:</span><span>{{ logMode }}</span>
      </div>
      <div class="mb-1 flex justify-between">
        <span>{{ $t('logger.packets') }}:</span><span>{{ logStatus?.packets ?? 0 }}</span>
      </div>
      <div class="flex justify-between">
        <span>{{ $t('logger.size') }}:</span><span>{{ logSize }}</span>
      </div>
    </div>
    <button
      v-if="interactive"
      type="button"
      :class="actionBtnPrimary"
      :disabled="logStatus?.recording"
      @click="emit('logStart', 'events')"
    >
      {{ $t('logger.startEvents') }}
    </button>
    <button
      v-if="interactive"
      type="button"
      :class="actionBtn"
      :disabled="logStatus?.recording"
      @click="emit('logStart', 'all')"
    >
      {{ $t('logger.startAll') }}
    </button>
    <button
      v-if="interactive"
      type="button"
      :class="actionBtnDanger"
      :disabled="!logStatus?.recording"
      @click="emit('logStop')"
    >
      {{ $t('logger.stop') }}
    </button>
    <div v-if="!interactive" class="text-tcu-txt-dim text-[10px] leading-snug">
      {{ $t('logger.viewOnlyHint') }}
    </div>
    <div v-if="interactive" class="text-tcu-txt-dim mt-1 text-[10px] leading-snug">
      {{ $t('logger.hint') }}
    </div>

    <h3 class="mt-6" :class="[sectionTitle]">
      {{ $t('session.title') }}
    </h3>
    <div class="grid grid-cols-2 gap-2">
      <div class="bg-tcu-bg-1 rounded-md p-2.5">
        <div class="text-tcu-txt-dim text-[10px] uppercase">{{ $t('session.shifts') }}</div>
        <div class="mt-0.5 font-mono text-base font-semibold">{{ shiftCount }}</div>
      </div>
      <div class="bg-tcu-bg-1 rounded-md p-2.5">
        <div class="text-tcu-txt-dim text-[10px] uppercase">{{ $t('session.packets') }}</div>
        <div class="mt-0.5 font-mono text-base font-semibold">{{ packetsTotal }}</div>
      </div>
      <div class="bg-tcu-bg-1 rounded-md p-2.5">
        <div class="text-tcu-txt-dim text-[10px] uppercase">{{ $t('session.peakRpm') }}</div>
        <div class="mt-0.5 font-mono text-base font-semibold">{{ peakRpm }}</div>
      </div>
      <div class="bg-tcu-bg-1 rounded-md p-2.5">
        <div class="text-tcu-txt-dim text-[10px] uppercase">{{ $t('session.peakG') }}</div>
        <div class="mt-0.5 font-mono text-base font-semibold">{{ peakG }}</div>
      </div>
    </div>
  </div>
</template>
