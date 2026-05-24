<script setup>
  import AppFooter from './components/AppFooter.vue'
  import AppHeader from './components/AppHeader.vue'
  import DashboardPanel from './components/DashboardPanel.vue'
  import ModeSidebar from './components/ModeSidebar.vue'
  import StatsHistoryPanel from './components/StatsHistoryPanel.vue'
  import { useTcuViewStore } from './composables/useTcuViewStore'

  const {
    mode,
    connected,
    live,
    shiftCount,
    packetsTotal,
    telemetry,
    logStatus,
    shiftHistory,
    sessionStats,
  } = useTcuViewStore()
</script>

<template>
  <AppHeader :mode="mode" :connected="connected" :live="live" />
  <main
    class="bg-tcu-border grid min-h-0 grid-cols-[260px_1fr_300px] gap-px max-[1100px]:grid-cols-1"
  >
    <ModeSidebar
      :mode="mode"
      :shift-count="shiftCount"
      :packets-total="packetsTotal"
      :telemetry="telemetry"
      :log-status="logStatus"
      :interactive="false"
    />
    <DashboardPanel :live="live" :telemetry="telemetry" />
    <StatsHistoryPanel
      :telemetry="telemetry"
      :session-stats="sessionStats"
      :shift-history="shiftHistory"
    />
  </main>
  <AppFooter />
</template>
