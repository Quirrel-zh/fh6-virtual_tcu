<script setup lang="ts">
import {
  RefreshOutline,
} from '@vicons/ionicons5'
import {
  NButton,
  NCard,
  NFlex,
  NGrid,
  NGridItem,
  NIcon,
  NSlider,
  NSwitch,
  NText,
} from 'naive-ui'
import { inject } from 'vue'
import { settingsContextKey } from './context'

const ctx = inject(settingsContextKey)!
const { t, store, featureToggles, settingsSliders, configNumber, configBool, sliderUnit } = ctx
</script>

<template>
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
