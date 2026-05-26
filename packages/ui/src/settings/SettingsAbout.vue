<script setup lang="ts">
import {
  CloudDownloadOutline,
  LogoGithub,
  OpenOutline,
} from '@vicons/ionicons5'
import {
  NButton,
  NCard,
  NDivider,
  NFlex,
  NIcon,
  NTag,
  NText,
} from 'naive-ui'
import { computed, inject } from 'vue'
import { settingsContextKey } from './context'

defineProps<{
  buildVersion: string
}>()
const ctx = inject(settingsContextKey)!
const { t, updater, openDashboard, openGithub } = ctx

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
</script>

<template>
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

<style scoped>
.brand-mark--lg {
  width: 56px;
  height: 56px;
  font-size: 14px;
  border-radius: 12px;
  background: linear-gradient(135deg, #16a34a 0%, #059669 100%);
  color: #ffffff;
  font-weight: 700;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3);
}
</style>
