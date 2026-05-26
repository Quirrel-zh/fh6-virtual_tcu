<script setup lang="ts">
import {
  ArrowDownOutline,
  ArrowUpOutline,
} from '@vicons/ionicons5'
import {
  NCard,
  NEmpty,
  NFlex,
  NIcon,
  NScrollbar,
  NTag,
  NText,
} from 'naive-ui'
import { inject } from 'vue'
import { settingsContextKey } from './context'

const ctx = inject(settingsContextKey)!
const { t, historyItems } = ctx

function shiftHistoryTimestamp(ts: number) {
  return new Date(ts * 1000).toTimeString().slice(0, 8)
}
</script>

<template>
  <NCard size="small" :bordered="false" :title="t('history.title')">
    <NEmpty v-if="historyItems.length === 0" :description="t('history.empty')" />
    <NScrollbar v-else style="max-height: calc(100vh - 280px);">
      <NFlex vertical :size="6">
        <NCard
          v-for="(h1, i) in historyItems"
          :key="i"
          size="small"
          embedded
        >
          <NFlex align="center" justify="space-between">
            <NFlex align="center" :size="10">
              <NIcon
                :component="h1.action === 'UP' ? ArrowUpOutline : ArrowDownOutline"
                size="18"
                :color="h1.action === 'UP' ? '#16a34a' : '#d97706'"
              />
              <NText strong>
                {{ h1.action }}
              </NText>
              <NTag size="small" :bordered="false">
                gear {{ h1.gear }}
              </NTag>
              <NText depth="3" style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;">
                {{ h1.reason || h1.rule }}
              </NText>
            </NFlex>
            <NText depth="3" style="font-family: ui-monospace, monospace; font-size: 11px;">
              {{ shiftHistoryTimestamp(h1.ts) }} · {{ h1.rpm_pct }}% · T{{ h1.throttle }} · B{{ h1.brake }}
            </NText>
          </NFlex>
        </NCard>
      </NFlex>
    </NScrollbar>
  </NCard>
</template>
