<script setup lang="ts">
import { computed, h } from 'vue'
import {
  NBadge,
  NButton,
  NCard,
  NConfigProvider,
  NDivider,
  NEmpty,
  NFlex,
  NGrid,
  NGridItem,
  NIcon,
  NInput,
  NLayout,
  NLayoutContent,
  NLayoutHeader,
  NMessageProvider,
  NModal,
  NScrollbar,
  NSelect,
  NSlider,
  NSpace,
  NStatistic,
  NSwitch,
  NTabPane,
  NTabs,
  NTag,
  NText,
  darkTheme,
  lightTheme,
  zhCN,
  enUS,
  dateZhCN,
  dateEnUS,
} from 'naive-ui'
import {
  ArrowDownOutline,
  ArrowUpOutline,
  CloudDownloadOutline,
  EyeOutline,
  HelpCircleOutline,
  OpenOutline,
  LogoGithub,
  RefreshOutline,
  RocketOutline,
  SettingsOutline,
  SpeedometerOutline,
  StatsChartOutline,
  TimeOutline,
} from '@vicons/ionicons5'
import { useSettingsApp } from './SettingsApp'

const {
  t,
  locale,
  activeTab,
  tabs,
  localeOptions,
  driveModes,
  featureToggles,
  hotkeyFields,
  shiftKeyFields,
  networkDraftHost,
  networkDraftWebPort,
  networkDraftUdpPort,
  networkDirty,
  networkApplyError,
  networkApplyOk,
  networkApplying,
  applyNetworkSettings,
  settingsSliders,
  advancedSliders,
  statusLabel,
  statsRows,
  historyItems,
  dashboardUrl,
  lanUrl,
  udpPort,
  sliderUnit,
  configNumber,
  configBool,
  configText,
  setLocale,
  onLogStart,
  onLogStop,
  onExportProfile,
  onOpenImport,
  openDashboard,
  toggleHud,
  openGithub,
  updater,
  store,
} = useSettingsApp()

const buildVersion = __APP_VERSION__

const updaterStatusText = computed(() => {
  switch (updater.state.value.kind) {
    case 'idle':
      return t('updater.idle')
    case 'checking':
      return t('updater.checking')
    case 'available':
      return t('updater.available', { version: updater.state.value.version })
    case 'not-available':
      return t('updater.notAvailable')
    case 'progress':
      return t('updater.progress', { percent: updater.state.value.percent })
    case 'downloaded':
      return t('updater.downloaded', { version: updater.state.value.version })
    case 'error':
      return t('updater.error', { message: updater.state.value.message })
  }
  return ''
})

const updaterStatusType = computed(() => {
  switch (updater.state.value.kind) {
    case 'available':
    case 'downloaded':
      return 'success'
    case 'checking':
    case 'progress':
      return 'info'
    case 'not-available':
      return 'default'
    case 'error':
      return 'error'
    default:
      return 'default'
  }
})

const naiveLocale = computed(() => (locale.value === 'zh-CN' ? zhCN : enUS))
const naiveDateLocale = computed(() => (locale.value === 'zh-CN' ? dateZhCN : dateEnUS))

const themeOverrides = {
  common: {
    primaryColor: '#16a34a',
    primaryColorHover: '#15803d',
    primaryColorPressed: '#166534',
    primaryColorSuppl: '#15803d',
    borderRadius: '8px',
    fontWeightStrong: '600',
  },
}

const tabIcon = {
  overview: SpeedometerOutline,
  config: SettingsOutline,
  advanced: RocketOutline,
  stats: StatsChartOutline,
  history: TimeOutline,
  about: HelpCircleOutline,
} as const

function renderTabIcon(key: keyof typeof tabIcon) {
  return () => h(NIcon, { size: 16 }, { default: () => h(tabIcon[key]) })
}

function modeColor(id: string) {
  return ({
    COMFORT: '#2563eb',
    DYNAMIC: '#9333ea',
    RACE: '#16a34a',
    DRIFT: '#dc2626',
    OFFROAD: '#ea580c',
    MANUAL: '#64748b',
  } as Record<string, string>)[id] ?? '#64748b'
}

function statusType() {
  if (statusLabel.value.kind === 'success')
    return 'success'
  if (statusLabel.value.kind === 'warning')
    return 'warning'
  return 'error'
}

function shiftHistoryTimestamp(ts: number) {
  return new Date(ts * 1000).toTimeString().slice(0, 8)
}

function modeTagText(id: string, i18nKey: string) {
  return `${t(`modes.${i18nKey}.name`)} · ${t(`modes.${i18nKey}.tag`).toUpperCase()}`
}
</script>

<template>
  <NConfigProvider
    :theme="lightTheme"
    :theme-overrides="themeOverrides"
    :locale="naiveLocale"
    :date-locale="naiveDateLocale"
    style="height: 100%;"
  >
    <NMessageProvider>
      <NLayout style="height: 100%;" content-style="display: flex; flex-direction: column;">
        <NLayoutHeader bordered style="padding: 12px 20px;">
          <NFlex justify="space-between" align="center">
            <NFlex align="center" :size="16">
              <div class="brand-mark">
                TCU
              </div>
              <div>
                <div style="font-size: 15px; font-weight: 600;">
                  {{ t('app.title') }}
                </div>
                <div style="font-size: 11px; color: #64748b; letter-spacing: 0.05em;">
                  {{ t('app.subtitle') }} · v{{ updater.currentVersion.value || buildVersion }}
                </div>
              </div>
              <NDivider vertical />
              <NTag :type="statusType()" round size="small" :bordered="false">
                <template #icon>
                  <NBadge dot :type="statusType()" :processing="store.connected.value" />
                </template>
                {{ statusLabel.text }}
              </NTag>
              <NTag round size="small" :bordered="false" :color="{ color: '#f1f5f9', textColor: '#0f172a' }">
                {{ store.mode.value }}
              </NTag>
            </NFlex>

            <NFlex :size="8" align="center">
              <NSelect
                :value="locale"
                :options="localeOptions"
                size="small"
                style="width: 120px;"
                @update:value="(v) => setLocale(v)"
              />
              <NButton size="small" @click="toggleHud">
                <template #icon>
                  <NIcon :component="EyeOutline" />
                </template>
                {{ t('electronApp.toggleHud') }}
              </NButton>
              <NButton type="primary" size="small" @click="openDashboard">
                <template #icon>
                  <NIcon :component="OpenOutline" />
                </template>
                {{ t('electronApp.openDashboard') }}
              </NButton>
            </NFlex>
          </NFlex>
        </NLayoutHeader>

        <NLayoutContent style="flex: 1; min-height: 0;" content-style="padding: 0;">
          <NTabs
            :value="activeTab"
            type="line"
            size="medium"
            
            style="height: 100%;"
            pane-wrapper-style="padding: 20px 24px; height: 100%; overflow-x: hidden; overflow-y: auto;"
            pane-style="padding-top: 0;"
            tab-style="padding: 10px 16px;"
            @update:value="(v) => (activeTab = v)"
          >
            <NTabPane
              v-for="tab in tabs"
              :key="tab.key"
              :name="tab.key"
              :tab="t(`electronTabs.${tab.i18nKey}`)"
              display-directive="show:lazy"
            >
              <template #tab>
                <NFlex align="center" :size="6">
                  <NIcon :component="tabIcon[tab.key]" size="16" />
                  <span>{{ t(`electronTabs.${tab.i18nKey}`) }}</span>
                </NFlex>
              </template>

              <!-- Overview -->
              <template v-if="tab.key === 'overview'">
                <NGrid :cols="12" :x-gap="16" :y-gap="16" responsive="screen" item-responsive>
                  <NGridItem :span="6">
                    <NCard :title="t('modes.title')" size="small" :bordered="false">
                      <template #header-extra>
                        <NText depth="3" style="font-size: 11px;">
                          {{ t('modes.hotkeyHintBefore') }}<kbd>F9</kbd>
                        </NText>
                      </template>
                      <NGrid :cols="2" :x-gap="8" :y-gap="8">
                        <NGridItem v-for="m in driveModes" :key="m.id">
                          <NButton
                            block
                            :type="store.mode.value === m.id ? 'primary' : 'default'"
                            :secondary="store.mode.value !== m.id"
                            :color="store.mode.value === m.id ? modeColor(m.id) : undefined"
                            @click="store.setMode(m.id)"
                          >
                            {{ modeTagText(m.id, m.i18nKey) }}
                          </NButton>
                        </NGridItem>
                      </NGrid>
                    </NCard>
                  </NGridItem>

                  <NGridItem :span="6">
                    <NCard :title="t('electronApp.quickActionsTitle')" size="small" :bordered="false">
                      <NText depth="3" style="font-size: 12px;">
                        {{ t('electronApp.quickActionsHint') }}
                      </NText>
                      <NFlex :size="8" style="margin-top: 12px;">
                        <NButton type="primary" block size="large" @click="openDashboard">
                          <template #icon>
                            <NIcon :component="OpenOutline" />
                          </template>
                          {{ t('electronApp.openDashboard') }}
                        </NButton>
                        <NButton block size="large" @click="toggleHud">
                          <template #icon>
                            <NIcon :component="EyeOutline" />
                          </template>
                          {{ t('electronApp.toggleHud') }}
                        </NButton>
                      </NFlex>

                      <NDivider style="margin: 16px 0;" />

                      <div style="font-size: 11px; color: #64748b; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px;">
                        {{ t('electronApp.connectionTitle') }}
                      </div>
                      <NGrid :cols="2" :x-gap="12" :y-gap="6">
                        <NGridItem>
                          <NText depth="3">
                            {{ t('electronApp.dashboardUrl') }}
                          </NText>
                        </NGridItem>
                        <NGridItem>
                          <NText code style="font-family: ui-monospace, monospace; font-size: 12px;">
                            {{ dashboardUrl }}
                          </NText>
                        </NGridItem>
                        <NGridItem v-if="lanUrl">
                          <NText depth="3">
                            {{ t('electronApp.lanUrl') }}
                          </NText>
                        </NGridItem>
                        <NGridItem v-if="lanUrl">
                          <NText code style="font-family: ui-monospace, monospace; font-size: 12px;">
                            {{ lanUrl }}
                          </NText>
                        </NGridItem>
                        <NGridItem>
                          <NText depth="3">
                            {{ t('electronApp.udpPort') }}
                          </NText>
                        </NGridItem>
                        <NGridItem>
                          <NText code style="font-family: ui-monospace, monospace; font-size: 12px;">
                            {{ udpPort }}
                          </NText>
                        </NGridItem>
                        <NGridItem>
                          <NText depth="3">
                            {{ t('electronApp.telemetryPackets') }}
                          </NText>
                        </NGridItem>
                        <NGridItem>
                          <NText code style="font-family: ui-monospace, monospace; font-size: 12px;">
                            {{ store.packetsTotal.value }}
                          </NText>
                        </NGridItem>
                      </NGrid>
                    </NCard>
                  </NGridItem>

                  <NGridItem :span="6">
                    <NCard :title="t('calibration.title')" size="small" :bordered="false">
                      <NFlex align="center" :size="12">
                        <NTag :type="store.telemetry.value?.calibrated ? 'success' : 'warning'" :bordered="false" round>
                          {{ store.telemetry.value?.calibrated ? t('calibration.calibrated') : t('calibration.learning') }}
                        </NTag>
                        <NText depth="3" style="font-size: 12px;">
                          {{ t('calibration.hint') }}
                        </NText>
                      </NFlex>
                    </NCard>
                  </NGridItem>

                  <NGridItem :span="6">
                    <NCard :title="t('logger.title')" size="small" :bordered="false">
                      <NFlex justify="space-between" align="center" style="margin-bottom: 12px;">
                        <NTag :type="store.logStatus.value?.recording ? 'error' : 'default'" :bordered="false" round>
                          {{ store.logStatus.value?.recording ? t('logger.recording') : t('logger.stopped') }}
                        </NTag>
                        <NText depth="3" style="font-size: 11px; font-family: ui-monospace, monospace;">
                          {{ store.logStatus.value?.packets ?? 0 }} pkts ·
                          {{ store.logStatus.value?.size_kb ?? 0 }} KB
                        </NText>
                      </NFlex>
                      <NFlex :size="6">
                        <NButton type="primary" size="small" :disabled="store.logStatus.value?.recording" @click="onLogStart('events')">
                          {{ t('logger.startEvents') }}
                        </NButton>
                        <NButton size="small" :disabled="store.logStatus.value?.recording" @click="onLogStart('all')">
                          {{ t('logger.startAll') }}
                        </NButton>
                        <NButton size="small" type="error" ghost :disabled="!store.logStatus.value?.recording" @click="onLogStop">
                          {{ t('logger.stop') }}
                        </NButton>
                      </NFlex>
                      <NText depth="3" style="font-size: 11px; display: block; margin-top: 8px;">
                        {{ t('logger.hint') }}
                      </NText>
                    </NCard>
                  </NGridItem>
                </NGrid>
              </template>

              <!-- Config -->
              <template v-else-if="tab.key === 'config'">
                <NFlex vertical :size="16">
                  <NCard :title="t('settings.features')" size="small" :bordered="false">
                    <NGrid :cols="2" :x-gap="16" :y-gap="10" responsive="screen" item-responsive>
                      <NGridItem v-for="f in featureToggles" :key="f.key" :span="1">
                        <NFlex justify="space-between" align="center">
                          <NText>{{ t(`settings.${f.i18nKey}`) }}</NText>
                          <NSwitch
                            :value="configBool(f.key)"
                            @update:value="(v) => store.setConfig(f.key, v)"
                          />
                        </NFlex>
                      </NGridItem>
                    </NGrid>
                  </NCard>

                  <NCard :title="t('settings.title')" size="small" :bordered="false">
                    <NFlex vertical :size="14">
                      <div v-for="s in settingsSliders" :key="s.key">
                        <NFlex justify="space-between" align="center" style="margin-bottom: 4px;">
                          <NText>{{ t(`settings.${s.i18nKey}`) }}</NText>
                          <NText code style="font-family: ui-monospace, monospace;">
                            {{ configNumber(s.key) }}{{ sliderUnit(s) }}
                          </NText>
                        </NFlex>
                        <NSlider
                          :value="configNumber(s.key)"
                          :min="s.min"
                          :max="s.max"
                          :step="s.step ?? 1"
                          @update:value="(v) => store.setConfig(s.key, v)"
                        />
                      </div>
                    </NFlex>
                  </NCard>

                  <NCard size="small" :bordered="false">
                    <NFlex justify="space-between" align="center">
                      <NText depth="3" style="font-size: 12px;">
                        {{ t('settings.autosave') }}
                      </NText>
                      <NButton type="error" ghost size="small" @click="store.resetConfig">
                        <template #icon>
                          <NIcon :component="RefreshOutline" />
                        </template>
                        {{ t('settings.reset') }}
                      </NButton>
                    </NFlex>
                  </NCard>
                </NFlex>
              </template>

              <!-- Advanced -->
              <template v-else-if="tab.key === 'advanced'">
                <NFlex vertical :size="16">
                  <NCard :title="t('extras.networkTitle')" size="small" :bordered="false">
                    <NText depth="3" style="font-size: 12px; display: block; margin-bottom: 8px;">
                      {{ t('extras.networkHint') }}
                    </NText>
                    <NGrid :cols="2" :x-gap="16" :y-gap="10">
                      <NGridItem>
                        <NFlex justify="space-between" align="center" :size="8">
                          <NText>{{ t('extras.webHost') }}</NText>
                          <NInput
                            v-model:value="networkDraftHost"
                            placeholder="0.0.0.0"
                            maxlength="15"
                            size="small"
                            style="width: 120px; font-family: ui-monospace, monospace;"
                          />
                        </NFlex>
                      </NGridItem>
                      <NGridItem>
                        <NFlex justify="space-between" align="center" :size="8">
                          <NText>{{ t('extras.webPort') }}</NText>
                          <NInput
                            v-model:value="networkDraftWebPort"
                            placeholder="8765"
                            maxlength="5"
                            size="small"
                            style="width: 120px; font-family: ui-monospace, monospace;"
                          />
                        </NFlex>
                      </NGridItem>
                      <NGridItem>
                        <NFlex justify="space-between" align="center" :size="8">
                          <NText>{{ t('extras.udpPort') }}</NText>
                          <NInput
                            v-model:value="networkDraftUdpPort"
                            placeholder="5555"
                            maxlength="5"
                            size="small"
                            style="width: 120px; font-family: ui-monospace, monospace;"
                          />
                        </NFlex>
                      </NGridItem>
                    </NGrid>
                    <NText depth="3" style="font-size: 11px; display: block; margin-top: 8px;">
                      {{ t('extras.udpPortHint') }}
                    </NText>
                    <NFlex :size="8" align="center" style="margin-top: 12px;">
                      <NButton
                        type="primary"
                        size="small"
                        :disabled="!networkDirty || networkApplying"
                        :loading="networkApplying"
                        @click="applyNetworkSettings"
                      >
                        {{ t('extras.networkApply') }}
                      </NButton>
                      <NText v-if="networkApplyOk" depth="3" style="font-size: 12px; color: #16a34a;">
                        {{ t('extras.networkApplyOk') }}
                      </NText>
                      <NText v-else-if="networkApplyError" depth="3" style="font-size: 12px; color: #dc2626;">
                        {{ t(`extras.networkErrors.${networkApplyError}`) }}
                      </NText>
                    </NFlex>
                  </NCard>

                  <NCard :title="t('extras.profileTitle')" size="small" :bordered="false">
                    <NText depth="3" style="font-size: 12px; display: block; margin-bottom: 12px;">
                      {{ t('extras.profileHint') }}
                    </NText>
                    <NFlex :size="8">
                      <NButton @click="onExportProfile">
                        {{ t('extras.export') }}
                      </NButton>
                      <NButton @click="onOpenImport">
                        {{ t('extras.import') }}
                      </NButton>
                    </NFlex>
                  </NCard>

                  <NCard :title="t('extras.shiftKeys')" size="small" :bordered="false">
                    <NText depth="3" style="font-size: 12px; display: block; margin-bottom: 8px;">
                      {{ t('extras.shiftKeyHint') }}
                    </NText>
                    <NGrid :cols="2" :x-gap="16" :y-gap="10">
                      <NGridItem v-for="h in shiftKeyFields" :key="h.key">
                        <NFlex justify="space-between" align="center" :size="8">
                          <NText>{{ t(`extras.${h.i18nKey}`) }}</NText>
                          <NInput
                            :value="configText(h.key)"
                            :placeholder="h.placeholder"
                            size="small"
                            style="width: 100px; font-family: ui-monospace, monospace;"
                            @update:value="(v) => store.setConfig(h.key, v.trim().toLowerCase())"
                          />
                        </NFlex>
                      </NGridItem>
                    </NGrid>
                  </NCard>

                  <NCard :title="t('extras.hotkeys')" size="small" :bordered="false">
                    <NText depth="3" style="font-size: 12px; display: block; margin-bottom: 8px;">
                      {{ t('extras.hotkeyHint') }}
                    </NText>
                    <NGrid :cols="2" :x-gap="16" :y-gap="10">
                      <NGridItem v-for="h in hotkeyFields" :key="h.key">
                        <NFlex justify="space-between" align="center" :size="8">
                          <NText>{{ t(`extras.${h.i18nKey}`) }}</NText>
                          <NInput
                            :value="configText(h.key)"
                            :placeholder="h.placeholder"
                            size="small"
                            style="width: 100px; font-family: ui-monospace, monospace;"
                            @update:value="(v) => store.setConfig(h.key, v.trim().toLowerCase())"
                          />
                        </NFlex>
                      </NGridItem>
                    </NGrid>
                  </NCard>

                  <NCard :title="t('extras.fullTuning')" size="small" :bordered="false">
                    <NFlex vertical :size="14">
                      <div v-for="s in advancedSliders" :key="s.key">
                        <NFlex justify="space-between" align="center" style="margin-bottom: 4px;">
                          <NText>{{ t(`settings.${s.i18nKey}`) }}</NText>
                          <NText code style="font-family: ui-monospace, monospace;">
                            {{ configNumber(s.key) }}{{ sliderUnit(s) }}
                          </NText>
                        </NFlex>
                        <NSlider
                          :value="configNumber(s.key)"
                          :min="s.min"
                          :max="s.max"
                          :step="s.step ?? 1"
                          @update:value="(v) => store.setConfig(s.key, v)"
                        />
                      </div>
                    </NFlex>
                  </NCard>
                </NFlex>
              </template>

              <!-- Stats -->
              <template v-else-if="tab.key === 'stats'">
                <template v-if="statsRows">
                  <NGrid :cols="4" :x-gap="12" :y-gap="12" responsive="screen" item-responsive>
                    <NGridItem :span="1">
                      <NCard size="small" :bordered="false">
                        <NStatistic :label="t('stats.duration')" :value="statsRows.duration" />
                      </NCard>
                    </NGridItem>
                    <NGridItem :span="1">
                      <NCard size="small" :bordered="false">
                        <NStatistic :label="t('stats.totalShifts')" :value="statsRows.total" />
                      </NCard>
                    </NGridItem>
                    <NGridItem :span="1">
                      <NCard size="small" :bordered="false">
                        <NStatistic :label="t('stats.upshifts')" :value="statsRows.upshifts" />
                      </NCard>
                    </NGridItem>
                    <NGridItem :span="1">
                      <NCard size="small" :bordered="false">
                        <NStatistic :label="t('stats.downshifts')" :value="statsRows.downshifts" />
                      </NCard>
                    </NGridItem>
                    <NGridItem :span="1">
                      <NCard size="small" :bordered="false">
                        <NStatistic :label="t('stats.kickdowns')" :value="statsRows.kickdowns" />
                      </NCard>
                    </NGridItem>
                    <NGridItem :span="1">
                      <NCard size="small" :bordered="false">
                        <NStatistic :label="t('stats.brakeDowns')" :value="statsRows.brakeDowns" />
                      </NCard>
                    </NGridItem>
                    <NGridItem :span="1">
                      <NCard size="small" :bordered="false">
                        <NStatistic :label="t('stats.predictives')" :value="statsRows.predictives" />
                      </NCard>
                    </NGridItem>
                    <NGridItem :span="1">
                      <NCard size="small" :bordered="false">
                        <NStatistic :label="t('stats.launches')" :value="statsRows.launches" />
                      </NCard>
                    </NGridItem>
                  </NGrid>

                  <NDivider title-placement="left">
                    {{ t('stats.performance') }}
                  </NDivider>

                  <NGrid :cols="4" :x-gap="12" :y-gap="12" responsive="screen" item-responsive>
                    <NGridItem :span="1">
                      <NCard size="small" :bordered="false">
                        <NStatistic :label="t('stats.peakRpm')" :value="statsRows.peakRpm" />
                      </NCard>
                    </NGridItem>
                    <NGridItem :span="1">
                      <NCard size="small" :bordered="false">
                        <NStatistic :label="t('stats.peakSpeed')" :value="statsRows.peakSpeed">
                          <template #suffix>
                            km/h
                          </template>
                        </NStatistic>
                      </NCard>
                    </NGridItem>
                    <NGridItem :span="1">
                      <NCard size="small" :bordered="false">
                        <NStatistic :label="t('stats.peakGLat')" :value="statsRows.peakGLat" />
                      </NCard>
                    </NGridItem>
                    <NGridItem :span="1">
                      <NCard size="small" :bordered="false">
                        <NStatistic :label="t('stats.peakGLon')" :value="statsRows.peakGLon" />
                      </NCard>
                    </NGridItem>
                    <NGridItem :span="1">
                      <NCard size="small" :bordered="false">
                        <NStatistic :label="t('stats.peakPower')" :value="statsRows.peakPower">
                          <template #suffix>
                            kW
                          </template>
                        </NStatistic>
                      </NCard>
                    </NGridItem>
                    <NGridItem :span="1">
                      <NCard size="small" :bordered="false">
                        <NStatistic :label="t('stats.avgThrottle')" :value="statsRows.avgThr">
                          <template #suffix>
                            %
                          </template>
                        </NStatistic>
                      </NCard>
                    </NGridItem>
                    <NGridItem :span="1">
                      <NCard size="small" :bordered="false">
                        <NStatistic :label="t('stats.carsDriven')" :value="statsRows.cars" />
                      </NCard>
                    </NGridItem>
                  </NGrid>

                  <NDivider title-placement="left">
                    {{ t('stats.learning') }}
                  </NDivider>

                  <NFlex :size="12">
                    <NTag :type="statsRows.calib ? 'success' : 'warning'" :bordered="false">
                      {{ t('stats.gearRatios') }}: {{ statsRows.calib ? t('stats.learned') : t('stats.learningStatus') }}
                    </NTag>
                    <NTag :type="statsRows.powerLearned ? 'success' : 'warning'" :bordered="false">
                      {{ t('stats.powerCurve') }}: {{ statsRows.powerLearned ? t('stats.learned') : t('stats.learningStatus') }}
                    </NTag>
                  </NFlex>
                </template>
                <NEmpty v-else :description="t('connection.standby')" />
              </template>

              <!-- History -->
              <template v-else-if="tab.key === 'history'">
                <NCard size="small" :bordered="false" :title="t('history.title')">
                  <NEmpty v-if="historyItems.length === 0" :description="t('history.empty')" />
                  <NScrollbar v-else style="max-height: calc(100vh - 280px);">
                    <NFlex vertical :size="6">
                      <NCard
                        v-for="(h, i) in historyItems"
                        :key="i"
                        size="small"
                        embedded
                      >
                        <NFlex align="center" justify="space-between">
                          <NFlex align="center" :size="10">
                            <NIcon
                              :component="h.action === 'UP' ? ArrowUpOutline : ArrowDownOutline"
                              size="18"
                              :color="h.action === 'UP' ? '#16a34a' : '#d97706'"
                            />
                            <NText strong>
                              {{ h.action }}
                            </NText>
                            <NTag size="small" :bordered="false">
                              gear {{ h.gear }}
                            </NTag>
                            <NText depth="3" style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;">
                              {{ h.reason || h.rule }}
                            </NText>
                          </NFlex>
                          <NText depth="3" style="font-family: ui-monospace, monospace; font-size: 11px;">
                            {{ shiftHistoryTimestamp(h.ts) }} · {{ h.rpm_pct }}% · T{{ h.throttle }} · B{{ h.brake }}
                          </NText>
                        </NFlex>
                      </NCard>
                    </NFlex>
                  </NScrollbar>
                </NCard>
              </template>

              <!-- About -->
              <template v-else-if="tab.key === 'about'">
                <NFlex justify="center">
                  <NCard size="medium" :bordered="false" style="max-width: 640px; width: 100%;">
                    <NFlex align="center" :size="16">
                      <div class="brand-mark brand-mark--lg">
                        TCU
                      </div>
                      <div>
                        <div style="font-size: 20px; font-weight: 700;">
                          {{ t('app.title') }}
                        </div>
                        <NText depth="3">
                          v{{ updater.currentVersion.value || buildVersion }} · {{ t('app.subtitle') }}
                        </NText>
                      </div>
                    </NFlex>
                    <NDivider />
                    <NText>{{ t('electronApp.aboutTagline') }}</NText>

                    <NDivider title-placement="left">
                      {{ t('updater.title') }}
                    </NDivider>

                    <NFlex justify="space-between" align="center" style="margin-bottom: 12px;">
                      <NTag :type="updaterStatusType" :bordered="false" round>
                        {{ updaterStatusText }}
                      </NTag>
                      <NText depth="3" style="font-size: 12px;">
                        {{ t('updater.currentVersion') }}: v{{ updater.currentVersion.value || buildVersion }}
                      </NText>
                    </NFlex>

                    <NFlex :size="8">
                      <NButton
                        :loading="updater.state.value.kind === 'checking' || updater.state.value.kind === 'progress'"
                        :disabled="updater.state.value.kind === 'downloaded'"
                        @click="updater.check"
                      >
                        <template #icon>
                          <NIcon :component="CloudDownloadOutline" />
                        </template>
                        {{ t('electronApp.checkUpdates') }}
                      </NButton>
                      <NButton
                        v-if="updater.state.value.kind === 'downloaded'"
                        type="primary"
                        @click="updater.install"
                      >
                        {{ t('updater.installNow') }}
                      </NButton>
                      <NButton type="primary" ghost @click="openDashboard">
                        <template #icon>
                          <NIcon :component="OpenOutline" />
                        </template>
                        {{ t('electronApp.openDashboard') }}
                      </NButton>
                    </NFlex>

                    <NDivider />
                    <NButton text type="primary" @click="openGithub">
                      <template #icon>
                        <NIcon :component="LogoGithub" />
                      </template>
                      {{ t('electronApp.githubRepo') }}
                    </NButton>
                    <NText depth="3" style="font-size: 12px; display: block; margin-top: 12px;">
                      {{ t('electronApp.aboutFooter') }}
                    </NText>
                  </NCard>
                </NFlex>
              </template>
            </NTabPane>
          </NTabs>
        </NLayoutContent>
      </NLayout>

      <NModal
        :show="store.modal.open"
        preset="card"
        :title="store.modal.title === 'copied'
          ? t('modal.copied')
          : store.modal.title || (store.modal.mode === 'export' ? t('modal.exportTitle') : t('modal.importTitle'))"
        style="width: 600px; max-width: 90vw;"
        :mask-closable="true"
        @update:show="(v) => !v && store.closeModal()"
      >
        <NInput
          type="textarea"
          :value="store.modal.text"
          :readonly="store.modal.readOnly"
          :autosize="{ minRows: 10, maxRows: 18 }"
          style="font-family: ui-monospace, monospace; font-size: 12px;"
          @update:value="(v) => (store.modal.text = v)"
        />
        <template #footer>
          <NFlex justify="end" :size="8">
            <NButton @click="store.closeModal">
              {{ t('modal.cancel') }}
            </NButton>
            <NButton type="primary" @click="store.confirmModal">
              {{ t('modal.confirm') }}
            </NButton>
          </NFlex>
        </template>
      </NModal>
    </NMessageProvider>
  </NConfigProvider>
</template>

<style scoped>
.brand-mark {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #16a34a 0%, #059669 100%);
  color: #ffffff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3);
}

.brand-mark--lg {
  width: 56px;
  height: 56px;
  font-size: 14px;
  border-radius: 12px;
}

kbd {
  display: inline-block;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  padding: 1px 6px;
  font-family: ui-monospace, monospace;
  font-size: 11px;
  color: #0f172a;
}
</style>
