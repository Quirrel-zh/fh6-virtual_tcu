<script setup lang="ts">
  import {
    EyeOutline,
    HelpCircleOutline,
    OpenOutline,
    RocketOutline,
    SettingsOutline,
    SpeedometerOutline,
    StatsChartOutline,
    TimeOutline,
  } from '@vicons/ionicons5'
  import TcuConfigProvider from '@virtual-tcu/ui/components/TcuConfigProvider.vue'
  import { settingsContextKey } from '@virtual-tcu/ui/settings'
  import SettingsAbout from '@virtual-tcu/ui/settings/SettingsAbout.vue'
  import SettingsAdvanced from '@virtual-tcu/ui/settings/SettingsAdvanced.vue'
  import SettingsConfig from '@virtual-tcu/ui/settings/SettingsConfig.vue'
  import SettingsHistory from '@virtual-tcu/ui/settings/SettingsHistory.vue'
  import SettingsOverview from '@virtual-tcu/ui/settings/SettingsOverview.vue'
  import SettingsStats from '@virtual-tcu/ui/settings/SettingsStats.vue'
  import {
    NBadge,
    NButton,
    NDivider,
    NFlex,
    NIcon,
    NInput,
    NLayout,
    NLayoutContent,
    NLayoutHeader,
    NModal,
    NSelect,
    NTabPane,
    NTabs,
    NTag,
  } from 'naive-ui'
  import { provide } from 'vue'
  import { brandIconUrl, useSettingsApp } from './SettingsApp'

  const ctx = useSettingsApp()
  provide(settingsContextKey, ctx as any)

  const {
    t,
    locale,
    activeTab,
    tabs,
    localeOptions,
    statusLabel,
    setLocale,
    openDashboard,
    toggleHud,
    updater,
    store,
  } = ctx

  const buildVersion = __APP_VERSION__

  const tabIcon = {
    overview: SpeedometerOutline,
    config: SettingsOutline,
    advanced: RocketOutline,
    stats: StatsChartOutline,
    history: TimeOutline,
    about: HelpCircleOutline,
  } as const

  function statusType() {
    if (statusLabel.value.kind === 'success') return 'success'
    if (statusLabel.value.kind === 'warning') return 'warning'
    return 'error'
  }
</script>

<template>
  <TcuConfigProvider>
    <NLayout style="height: 100%" content-style="display: flex; flex-direction: column;">
      <NLayoutHeader bordered style="padding: 12px 20px">
        <NFlex justify="space-between" align="center">
          <NFlex align="center" :size="16">
            <img class="brand-mark" :src="brandIconUrl" :alt="t('app.title')" />
            <div>
              <div style="font-size: 15px; font-weight: 600">
                {{ t('app.title') }}
              </div>
              <div style="font-size: 11px; color: #64748b; letter-spacing: 0.05em">
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
            <NTag
              round
              size="small"
              :bordered="false"
              :color="{ color: '#f1f5f9', textColor: '#0f172a' }"
            >
              {{ store.mode.value }}
            </NTag>
          </NFlex>

          <NFlex :size="8" align="center">
            <NSelect
              :value="locale"
              :options="localeOptions"
              size="small"
              style="width: 120px"
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

      <NLayoutContent style="flex: 1; min-height: 0" content-style="padding: 0;">
        <NTabs
          :value="activeTab"
          type="line"
          size="medium"
          style="height: 100%"
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

            <SettingsOverview v-if="tab.key === 'overview'" />
            <SettingsConfig v-else-if="tab.key === 'config'" />
            <SettingsAdvanced v-else-if="tab.key === 'advanced'" />
            <SettingsStats v-else-if="tab.key === 'stats'" />
            <SettingsHistory v-else-if="tab.key === 'history'" />
            <SettingsAbout v-else-if="tab.key === 'about'" :build-version="buildVersion" />
          </NTabPane>
        </NTabs>
      </NLayoutContent>
    </NLayout>

    <NModal
      :show="store.modal.open"
      preset="card"
      :title="
        store.modal.title === 'copied'
          ? t('modal.copied')
          : store.modal.title ||
            (store.modal.mode === 'export' ? t('modal.exportTitle') : t('modal.importTitle'))
      "
      style="width: 600px; max-width: 90vw"
      :mask-closable="true"
      @update:show="(v) => !v && store.closeModal()"
    >
      <NInput
        type="textarea"
        :value="store.modal.text"
        :readonly="store.modal.readOnly"
        :autosize="{ minRows: 10, maxRows: 18 }"
        style="font-family: ui-monospace, monospace; font-size: 12px"
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
  </TcuConfigProvider>
</template>

<style scoped>
  .brand-mark {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    object-fit: contain;
    display: block;
    flex-shrink: 0;
    filter: drop-shadow(0 1px 2px rgba(15, 23, 42, 0.16))
      drop-shadow(0 2px 8px rgba(15, 23, 42, 0.1));
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
