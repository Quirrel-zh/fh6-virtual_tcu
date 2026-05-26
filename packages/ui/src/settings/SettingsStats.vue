<script setup lang="ts">
import {
  NCard,
  NDivider,
  NEmpty,
  NFlex,
  NGrid,
  NGridItem,
  NStatistic,
  NTag,
} from 'naive-ui'
import { inject } from 'vue'
import { settingsContextKey } from './context'

const ctx = inject(settingsContextKey)!
const { t, statsRows } = ctx
</script>

<template>
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
