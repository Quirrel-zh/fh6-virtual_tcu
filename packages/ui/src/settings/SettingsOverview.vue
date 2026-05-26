<script setup lang="ts">
import {
  EyeOutline,
  OpenOutline,
} from '@vicons/ionicons5'
import {
  NButton,
  NCard,
  NDivider,
  NFlex,
  NGrid,
  NGridItem,
  NIcon,
  NTag,
  NText,
} from 'naive-ui'
import { inject } from 'vue'
import { settingsContextKey } from './context'

const ctx = inject(settingsContextKey)!
const { t, store, driveModes, dashboardUrl, lanUrl, udpPort, openDashboard, toggleHud, onLogStart, onLogStop } = ctx

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

function modeTagText(id: string, i18nKey: string) {
  return `${t(`modes.${i18nKey}.name`)} · ${t(`modes.${i18nKey}.tag`).toUpperCase()}`
}
</script>

<template>
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

<style scoped>
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
