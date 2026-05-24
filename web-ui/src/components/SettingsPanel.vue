<script setup>
  import { computed, toRefs } from 'vue'
  import {
    FEATURE_TOGGLES,
    HOTKEY_FIELDS,
    SETTING_GROUPS,
    SHIFT_KEY_FIELDS,
  } from '@/config/settings'
  import { useNetworkSettings } from './network-settings'
  import {
    actionBtn,
    actionBtnCompact,
    actionBtnDanger,
    col,
    hotkeyInput,
    sectionTitle,
    statRow,
    tabActive,
    tabBase,
    toggleRow,
  } from '@/styles/ui'
  import ConfigTextInput from './ConfigTextInput.vue'
  import { TAB_IDS, useSettingsPanel } from './settings-panel'
  import SettingSlider from './SettingSlider.vue'
  import ToggleSwitch from './ToggleSwitch.vue'

  const props = defineProps({
    config: { type: Object, required: true },
    telemetry: { type: Object, default: null },
    sessionStats: { type: Object, default: null },
    shiftHistory: { type: Array, default: () => [] },
    watchdogStuck: { type: Boolean, default: false },
    visibleTabs: { type: Array, default: () => TAB_IDS },
    initialTab: { type: String, default: '' },
    hideTabBar: { type: Boolean, default: false },
  })
  const emit = defineEmits(['setConfig', 'applyNetwork', 'resetConfig', 'exportProfile', 'openImport'])

  const { config, telemetry, sessionStats, shiftHistory, watchdogStuck, visibleTabs } =
    toRefs(props)

  const { activeTab, slidersFor, statsRows, historyItems, configValue, configBool, sliderDef } =
    useSettingsPanel(
      () => config.value,
      () => telemetry.value,
      () => sessionStats.value,
      () => shiftHistory.value,
    )

  if (props.initialTab && (props.visibleTabs ?? TAB_IDS).includes(props.initialTab)) {
    activeTab.value = props.initialTab
  }
  else if (props.visibleTabs?.length && !props.visibleTabs.includes(activeTab.value)) {
    activeTab.value = props.visibleTabs[0]
  }

  const extrasSliders = computed(() => slidersFor('extras'))

  const {
    draftHost: networkDraftHost,
    draftWebPort: networkDraftWebPort,
    draftUdpPort: networkDraftUdpPort,
    dirty: networkDirty,
    applyError: networkApplyError,
    validate: validateNetwork,
  } = useNetworkSettings(() => config.value)

  function applyNetworkSettings() {
    const parsed = validateNetwork()
    if (parsed)
      emit('applyNetwork', parsed.host, parsed.webPort, parsed.udpPort)
  }
</script>

<template>
  <div :class="col">
    <div v-if="!hideTabBar" class="border-tcu-border mb-4 flex gap-1 border-b">
      <button
        v-for="tab in visibleTabs"
        :key="tab"
        type="button"
        :class="[tabBase, activeTab === tab && tabActive]"
        @click="activeTab = tab"
      >
        {{ $t(`tabs.${tab}`) }}
      </button>
    </div>

    <div v-show="activeTab === 'settings'">
      <div
        v-if="watchdogStuck"
        class="border-warn bg-warn/15 text-warn mb-3 rounded-lg border px-3.5 py-2.5 text-sm before:font-bold before:content-['⚠_']"
      >
        {{ $t('settings.watchdog') }}
      </div>
      <h3 :class="sectionTitle">
        {{ $t('settings.features') }}
      </h3>
      <div v-for="f in FEATURE_TOGGLES" :key="f.key" :class="toggleRow">
        <span class="text-tcu-txt-muted text-sm">{{ $t(`settings.${f.i18nKey}`) }}</span>
        <ToggleSwitch
          :on="configBool(f.key)"
          @toggle="emit('setConfig', f.key, !configBool(f.key))"
        />
      </div>

      <template v-for="group in SETTING_GROUPS" :key="group.i18nKey">
        <h3 class="mt-5" :class="[sectionTitle]">
          {{ $t(`settings.${group.i18nKey}`) }}
        </h3>
        <p v-if="group.hintKey" class="text-tcu-txt-dim mb-1.5 text-[10px]">
          {{ $t(`settings.${group.hintKey}`) }}
        </p>
        <SettingSlider
          v-for="key in group.keys"
          :key="key"
          :label="$t(`settings.${sliderDef(key)?.i18nKey ?? key}`)"
          :config-key="key"
          :value="configValue(key)"
          :min="sliderDef(key)?.min ?? 0"
          :max="sliderDef(key)?.max ?? 100"
          :step="sliderDef(key)?.step ?? 1"
          :unit="sliderDef(key)?.unit"
          @input="emit('setConfig', key, $event)"
        />
      </template>

      <button
        type="button"
        class="mt-4"
        :class="[actionBtnDanger]"
        @click="
          () => {
            if (confirm($t('settings.resetConfirm'))) emit('resetConfig')
          }
        "
      >
        {{ $t('settings.reset') }}
      </button>
      <div class="text-tcu-txt-dim mt-1 text-center text-[10px]">
        {{ $t('settings.autosave') }}
      </div>
    </div>

    <div v-show="activeTab === 'stats'">
      <h3 :class="sectionTitle">
        {{ $t('stats.title') }}
      </h3>
      <template v-if="statsRows">
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.duration') }}</span
          ><span class="text-tcu-txt font-mono font-semibold">{{ statsRows.duration }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.totalShifts') }}</span
          ><span class="text-tcu-txt font-mono font-semibold">{{ statsRows.total }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.upshifts') }}</span
          ><span class="text-tcu-txt font-mono font-semibold">{{ statsRows.upshifts }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.downshifts') }}</span
          ><span class="text-tcu-txt font-mono font-semibold">{{ statsRows.downshifts }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.kickdowns') }}</span
          ><span class="text-tcu-txt font-mono font-semibold">{{ statsRows.kickdowns }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.brakeDowns') }}</span
          ><span class="text-tcu-txt font-mono font-semibold">{{ statsRows.brakeDowns }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.predictives') }}</span
          ><span class="text-tcu-txt font-mono font-semibold">{{ statsRows.predictives }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.launches') }}</span
          ><span class="text-tcu-txt font-mono font-semibold">{{ statsRows.launches }}</span>
        </div>
        <h3 class="mt-5" :class="[sectionTitle]">
          {{ $t('stats.performance') }}
        </h3>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.peakRpm') }}</span
          ><span class="text-tcu-txt font-mono font-semibold">{{ statsRows.peakRpm }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.peakSpeed') }}</span
          ><span class="text-tcu-txt font-mono font-semibold">{{ statsRows.peakSpeed }} km/h</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.peakGLat') }}</span
          ><span class="text-tcu-txt font-mono font-semibold">{{ statsRows.peakGLat }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.peakGLon') }}</span
          ><span class="text-tcu-txt font-mono font-semibold">{{ statsRows.peakGLon }}</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.peakPower') }}</span
          ><span class="text-tcu-txt font-mono font-semibold">{{ statsRows.peakPower }} kW</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.avgThrottle') }}</span
          ><span class="text-tcu-txt font-mono font-semibold">{{ statsRows.avgThr }}%</span>
        </div>
        <div :class="statRow">
          <span class="text-tcu-txt-dim">{{ $t('stats.carsDriven') }}</span
          ><span class="text-tcu-txt font-mono font-semibold">{{ statsRows.cars }}</span>
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
    </div>

    <div v-show="activeTab === 'history'">
      <h3 :class="sectionTitle">
        {{ $t('history.title') }}
      </h3>
      <div class="flex max-h-60 flex-col gap-1 overflow-y-auto">
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

    <div v-show="activeTab === 'extras'">
      <h3 :class="sectionTitle">
        {{ $t('extras.networkTitle') }}
      </h3>
      <p class="text-tcu-txt-dim mb-2 text-[11px] leading-snug">
        {{ $t('extras.networkHint') }}
      </p>
      <div class="grid grid-cols-[1fr_auto] items-center gap-2 py-1.5">
        <span class="text-tcu-txt-muted text-xs">{{ $t('extras.webHost') }}</span>
        <input
          v-model="networkDraftHost"
          type="text"
          :class="hotkeyInput"
          maxlength="15"
          placeholder="0.0.0.0"
          spellcheck="false"
          autocomplete="off"
        >
      </div>
      <div class="grid grid-cols-[1fr_auto] items-center gap-2 py-1.5">
        <span class="text-tcu-txt-muted text-xs">{{ $t('extras.webPort') }}</span>
        <input
          v-model="networkDraftWebPort"
          type="text"
          :class="hotkeyInput"
          maxlength="5"
          placeholder="8765"
          spellcheck="false"
          autocomplete="off"
        >
      </div>
      <div class="grid grid-cols-[1fr_auto] items-center gap-2 py-1.5">
        <span class="text-tcu-txt-muted text-xs">{{ $t('extras.udpPort') }}</span>
        <input
          v-model="networkDraftUdpPort"
          type="text"
          :class="hotkeyInput"
          maxlength="5"
          placeholder="5555"
          spellcheck="false"
          autocomplete="off"
        >
      </div>
      <p class="text-tcu-txt-dim mb-2 text-[10px] leading-snug">
        {{ $t('extras.udpPortHint') }}
      </p>
      <div class="mt-2 flex items-center gap-2">
        <button
          type="button"
          :class="[actionBtn, actionBtnCompact, !networkDirty && 'opacity-50']"
          :disabled="!networkDirty"
          @click="applyNetworkSettings"
        >
          {{ $t('extras.networkApply') }}
        </button>
        <span v-if="networkApplyError" class="text-warn text-[10px]">
          {{ $t(`extras.networkErrors.${networkApplyError}`) }}
        </span>
      </div>
      <h3 class="mt-6" :class="[sectionTitle]">
        {{ $t('extras.profileTitle') }}
      </h3>
      <p class="text-tcu-txt-dim mb-2 text-[11px] leading-snug">
        {{ $t('extras.profileHint') }}
      </p>
      <div class="mt-2 grid grid-cols-2 gap-1.5">
        <button type="button" :class="[actionBtn, actionBtnCompact]" @click="emit('exportProfile')">
          {{ $t('extras.export') }}
        </button>
        <button type="button" :class="[actionBtn, actionBtnCompact]" @click="emit('openImport')">
          {{ $t('extras.import') }}
        </button>
      </div>
      <h3 class="mt-6" :class="[sectionTitle]">
        {{ $t('extras.shiftKeys') }}
      </h3>
      <p class="text-tcu-txt-dim mb-2 text-[11px]">
        {{ $t('extras.shiftKeyHint') }}
      </p>
      <div
        v-for="h in SHIFT_KEY_FIELDS"
        :key="h.key"
        class="grid grid-cols-[1fr_auto] items-center gap-2 py-1.5"
      >
        <span class="text-tcu-txt-muted text-xs">{{ $t(`extras.${h.i18nKey}`) }}</span>
        <ConfigTextInput
          :config-key="h.key"
          :config="config"
          :placeholder="h.placeholder"
          @commit="(key, value) => emit('setConfig', key, value)"
        />
      </div>
      <h3 class="mt-6" :class="[sectionTitle]">
        {{ $t('extras.hotkeys') }}
      </h3>
      <p class="text-tcu-txt-dim mb-2 text-[11px]">
        {{ $t('extras.hotkeyHint') }}
      </p>
      <div
        v-for="h in HOTKEY_FIELDS"
        :key="h.key"
        class="grid grid-cols-[1fr_auto] items-center gap-2 py-1.5"
      >
        <span class="text-tcu-txt-muted text-xs">{{ $t(`extras.${h.i18nKey}`) }}</span>
        <ConfigTextInput
          :config-key="h.key"
          :config="config"
          :placeholder="h.placeholder"
          @commit="(key, value) => emit('setConfig', key, value)"
        />
      </div>
      <h3 class="mt-6" :class="[sectionTitle]">
        {{ $t('extras.fullTuning') }}
      </h3>
      <SettingSlider
        v-for="s in extrasSliders"
        :key="s.key"
        :label="$t(`settings.${s.i18nKey}`)"
        :config-key="s.key"
        :value="configValue(s.key)"
        :min="s.min"
        :max="s.max"
        :step="s.step ?? 1"
        :unit="s.unit"
        @input="emit('setConfig', s.key, $event)"
      />
    </div>
  </div>
</template>
