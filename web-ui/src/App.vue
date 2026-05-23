<script setup>
import { useI18n } from 'vue-i18n'
import AppFooter from './components/AppFooter.vue'
import AppHeader from './components/AppHeader.vue'
import DashboardPanel from './components/DashboardPanel.vue'
import ModeSidebar from './components/ModeSidebar.vue'
import ProfileModal from './components/ProfileModal.vue'
import SettingsPanel from './components/SettingsPanel.vue'
import { useTcuStore } from './composables/useTcuStore'

const { t } = useI18n()

const {
  mode,
  connected,
  live,
  shiftCount,
  packetsTotal,
  telemetry,
  logStatus,
  shiftHistory,
  watchdogStuck,
  sessionStats,
  config,
  modal,
  send,
  setMode,
  setConfig,
  resetConfig,
  closeModal,
  confirmModal,
  openModal,
} = useTcuStore()

function onLogStart(logMode) {
  send({ type: 'log_start', mode: logMode })
}

function onOpenImport() {
  openModal('import', t('modal.importTitle'), '')
}
</script>

<template>
  <AppHeader :mode="mode" :connected="connected" :live="live" />
  <main class="grid gap-px bg-tcu-border max-[1100px]:grid-cols-1 grid-cols-[260px_1fr_340px]">
    <ModeSidebar
      :mode="mode"
      :shift-count="shiftCount"
      :packets-total="packetsTotal"
      :telemetry="telemetry"
      :log-status="logStatus"
      @set-mode="setMode"
      @log-start="onLogStart"
      @log-stop="() => send({ type: 'log_stop' })"
    />
    <DashboardPanel :live="live" :telemetry="telemetry" />
    <SettingsPanel
      :config="config"
      :telemetry="telemetry"
      :session-stats="sessionStats"
      :shift-history="shiftHistory"
      :watchdog-stuck="watchdogStuck"
      @set-config="setConfig"
      @reset-config="resetConfig"
      @export-profile="() => send({ type: 'export_profile' })"
      @open-import="onOpenImport"
    />
  </main>
  <AppFooter :config="config" />
  
  <ProfileModal
    :open="modal.open"
    :mode="modal.mode"
    :title="
      modal.title === 'copied'
        ? t('modal.copied')
        : modal.title || (modal.mode === 'export' ? t('modal.exportTitle') : t('modal.importTitle'))
    "
    :text="modal.text"
    :read-only="modal.readOnly"
    @close="closeModal"
    @confirm="confirmModal"
    @update:text="(v) => (modal.text = v)"
  />
</template>
