<script setup>
  import { toRefs, computed } from 'vue'
  import DashboardChart from './DashboardChart.vue'

  const props = defineProps({
    live: { type: Boolean, required: true },
    telemetry: { type: Object, default: () => ({}) },
  })
  const { live, telemetry } = toRefs(props)

  const t = computed(() => telemetry.value || {})
  const speed = computed(() => Math.round(t.value.speed_kmh || 0))
  const rpm = computed(() => Math.round(t.value.rpm || 0))
  const rpmMax = computed(() => Math.round(t.value.rpm_max || 8000))
  const rpmPct = computed(() => t.value.rpm_pct || 0)
  const powerKw = computed(() => Math.round(t.value.power_kw || 0))
  const torqueNm = computed(() => Math.round(t.value.torque_nm || 0))
  const turboBar = computed(() => (t.value.turbo_bar || 0).toFixed(2))

  const throttle = computed(() => (t.value.throttle || 0) * 100)
  const brake = computed(() => (t.value.brake || 0) * 100)
  const clutch = computed(() => (t.value.clutch_raw ? (t.value.clutch_raw / 255) * 100 : 0))

  const gLat = computed(() => t.value.g_lat || 0)
  const gLon = computed(() => t.value.g_lon || 0)
  const gripUsage = computed(() => (t.value.grip_usage || 0) * 100)

  const state = computed(() => t.value.tcu_state || 'STANDBY')
  const subState = computed(() => t.value.tcu_state_sub || 'AWAITING TELEMETRY')
  const attitude = computed(() => t.value.attitude || 'NEUTRAL')
  const hint = computed(() => t.value.shift_hint || '')

  const isAirborne = computed(() => t.value.airborne || false)
  const isYawLocked = computed(() => t.value.yaw_transient || false)

  const gear = computed(() => {
    const g = t.value.gear
    if (g === 0) return 'R'
    if (g === 11) return 'N'
    return g || '-'
  })

  const getLedColor = (index, pct) => {
    const totalLeds = 20
    const threshold = index / totalLeds

    if (pct < threshold) return 'bg-[#18181b] shadow-none'

    if (index > 17) return 'bg-blue-500 shadow-[0_0_12px_rgba(59,130,246,0.9)]'
    if (index > 13) return 'bg-red-500 shadow-[0_0_12px_rgba(239,68,68,0.9)]'
    if (index > 8) return 'bg-yellow-400 shadow-[0_0_10px_rgba(250,204,21,0.8)]'
    return 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.8)]'
  }

  const gDotStyle = computed(() => {
    const maxG = 1.5
    const x = Math.max(-maxG, Math.min(maxG, gLat.value))
    const y = Math.max(-maxG, Math.min(maxG, gLon.value))
    const px = 50 + (x / maxG) * 50
    const py = 50 - (y / maxG) * 50
    return { left: `${px}%`, top: `${py}%` }
  })
</script>

<template>
  <div
    class="bg-tcu-bg-0 flex h-full min-h-0 flex-col justify-start gap-3 overflow-hidden border-l border-[#1a1a24] p-4 font-mono text-[#e4e4e7] select-none"
  >
    <div v-if="live && telemetry" class="flex min-h-0 flex-1 flex-col gap-3 overflow-hidden">
      <div class="flex shrink-0 flex-col gap-3">
        <div
          class="flex h-10 w-full shrink-0 items-center justify-between gap-1 rounded-md border border-[#27272a] bg-[#0a0a0c] px-2"
        >
          <div
            v-for="i in 20"
            :key="i"
            class="h-5 flex-1 rounded-[2px] border border-black/50 transition-colors duration-75"
            :class="getLedColor(i, rpmPct)"
          ></div>
        </div>

        <div class="grid h-[280px] shrink-0 grid-cols-[220px_1fr_180px] gap-3 overflow-hidden">
          <div class="flex flex-col gap-3">
            <div
              class="relative flex flex-1 flex-col items-center justify-center overflow-hidden rounded-lg border border-[#27272a] bg-[#0a0a0c] shadow-inner"
            >
              <div
                v-if="hint"
                class="text-accent absolute top-2 left-0 z-10 w-full animate-pulse text-center text-sm font-bold tracking-widest"
              >
                {{ hint }}
              </div>

              <div
                class="text-[140px] leading-none font-black tracking-tighter tabular-nums"
                :class="
                  state === 'SHIFTING' ? 'text-accent-2' : gear === 'R' ? 'text-warn' : 'text-white'
                "
              >
                {{ gear }}
              </div>
              <div
                class="text-tcu-txt-dim absolute bottom-3 mt-1 text-[10px] tracking-widest uppercase"
              >
                {{ t.drivetrain || 'DRIVETRAIN' }}
              </div>
            </div>

            <div
              class="flex h-24 flex-col items-center justify-center rounded-lg border border-[#27272a] bg-[#0a0a0c]"
            >
              <div class="text-6xl font-bold tracking-tight text-white tabular-nums">
                {{ speed }}
              </div>
              <div class="text-tcu-txt-dim mt-1 text-[10px] tracking-widest uppercase">KM/H</div>
            </div>
          </div>

          <div class="flex flex-col gap-3">
            <div
              class="relative flex flex-1 flex-col justify-center rounded-lg border border-[#27272a] bg-[#0a0a0c] p-5"
            >
              <div class="mb-2 flex items-end justify-between">
                <div
                  class="text-7xl font-bold tracking-tight tabular-nums"
                  :class="rpmPct > 0.9 ? 'text-danger' : 'text-warn'"
                >
                  {{ rpm }}
                </div>
                <div class="text-right">
                  <div class="text-tcu-txt-dim text-sm font-bold tabular-nums">
                    MAX {{ rpmMax }}
                  </div>
                  <div class="text-tcu-txt-dim text-[10px] tracking-widest uppercase">RPM</div>
                </div>
              </div>

              <div
                class="relative mt-4 h-6 w-full overflow-hidden rounded-sm border border-[#27272a] bg-[#18181b]"
              >
                <div
                  class="absolute top-0 left-0 h-full transition-all duration-75"
                  :class="rpmPct > 0.9 ? 'bg-danger' : rpmPct > 0.7 ? 'bg-warn' : 'bg-accent'"
                  :style="{ width: `${Math.min(100, rpmPct * 100)}%` }"
                ></div>
                <div
                  v-if="t.peak_torque_rpm_pct"
                  class="absolute z-10 h-full w-0.5 bg-blue-500"
                  :style="{ left: `${t.peak_torque_rpm_pct * 100}%` }"
                ></div>
                <div
                  v-if="t.peak_power_rpm_pct"
                  class="absolute z-10 h-full w-0.5 bg-purple-500"
                  :style="{ left: `${t.peak_power_rpm_pct * 100}%` }"
                ></div>
              </div>
              <div class="mt-1 flex w-full justify-between px-1">
                <span class="text-[9px] text-blue-500">PEAK TQ</span>
                <span class="text-[9px] text-purple-500">PEAK HP</span>
              </div>
            </div>

            <div class="grid h-20 grid-cols-3 gap-3">
              <div
                class="flex flex-col justify-between rounded-lg border border-[#27272a] bg-[#0a0a0c] p-3"
              >
                <span class="text-tcu-txt-dim text-[10px] tracking-widest uppercase">Power</span>
                <div class="text-2xl font-bold text-white tabular-nums">
                  {{ powerKw }} <span class="text-tcu-txt-dim text-xs">kW</span>
                </div>
              </div>
              <div
                class="flex flex-col justify-between rounded-lg border border-[#27272a] bg-[#0a0a0c] p-3"
              >
                <span class="text-tcu-txt-dim text-[10px] tracking-widest uppercase">Torque</span>
                <div class="text-2xl font-bold text-white tabular-nums">
                  {{ torqueNm }} <span class="text-tcu-txt-dim text-xs">Nm</span>
                </div>
              </div>
              <div
                class="relative flex flex-col justify-between overflow-hidden rounded-lg border border-[#27272a] bg-[#0a0a0c] p-3"
              >
                <span class="text-tcu-txt-dim z-10 text-[10px] tracking-widest uppercase"
                  >Turbo</span
                >
                <div class="text-accent-2 z-10 text-2xl font-bold tabular-nums">
                  {{ turboBar }} <span class="text-tcu-txt-dim text-xs">Bar</span>
                </div>
                <div
                  class="bg-accent-2/20 absolute bottom-0 left-0 w-full transition-all duration-75"
                  :style="{ height: `${(t.turbo_bar / 2.0) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>

          <div
            class="flex justify-between gap-2 rounded-lg border border-tcu-border bg-tcu-bg-1 p-4"
          >
            <div class="flex h-full w-10 flex-col items-center justify-end gap-2">
              <span class="text-[10px] font-bold text-white tabular-nums">{{
                Math.round(clutch)
              }}</span>
              <div
                class="flex w-6 flex-1 items-end overflow-hidden rounded border border-tcu-border bg-tcu-bg-3"
              >
                <div
                  class="w-full bg-blue-500 transition-all duration-75"
                  :style="{ height: `${clutch}%` }"
                ></div>
              </div>
              <span class="text-tcu-txt-dim text-[10px] uppercase">CLT</span>
            </div>

            <div class="flex h-full w-10 flex-col items-center justify-end gap-2">
              <span class="text-[10px] font-bold text-white tabular-nums">{{
                Math.round(brake)
              }}</span>
              <div
                class="flex w-6 flex-1 items-end overflow-hidden rounded border border-tcu-border bg-tcu-bg-3"
              >
                <div
                  class="bg-danger w-full transition-all duration-75"
                  :style="{ height: `${brake}%` }"
                ></div>
              </div>
              <span class="text-tcu-txt-dim text-[10px] uppercase">BRK</span>
            </div>

            <div class="flex h-full w-10 flex-col items-center justify-end gap-2">
              <span class="text-[10px] font-bold text-white tabular-nums">{{
                Math.round(throttle)
              }}</span>
              <div
                class="flex w-6 flex-1 items-end overflow-hidden rounded border border-tcu-border bg-tcu-bg-3"
              >
                <div
                  class="bg-accent w-full transition-all duration-75"
                  :style="{ height: `${throttle}%` }"
                ></div>
              </div>
              <span class="text-tcu-txt-dim text-[10px] uppercase">THR</span>
            </div>
          </div>
        </div>

        <div class="grid h-[156px] shrink-0 grid-cols-[1fr_200px_200px] gap-3 overflow-hidden">
          <div
            class="relative flex flex-col justify-center overflow-hidden rounded-lg border bg-[#0a0a0c] p-5"
            :class="
              state === 'SHIFTING'
                ? 'border-accent-2/50 bg-accent-2/5'
                : state.includes('LOCK') || state.includes('BLOCKED')
                  ? 'border-danger/50 bg-danger/5'
                  : 'border-[#27272a]'
            "
          >
            <div
              class="text-tcu-txt-dim absolute top-3 left-4 text-[10px] tracking-widest uppercase"
            >
              TCU Controller Status
            </div>
            <div
              class="mt-2 text-3xl font-bold tracking-wide"
              :class="
                state.includes('DOWN')
                  ? 'text-warn'
                  : state.includes('UP')
                    ? 'text-accent'
                    : 'text-white'
              "
            >
              {{ state }}
            </div>
            <div class="text-tcu-txt-muted mt-1 text-sm font-semibold uppercase">
              {{ subState }}
            </div>

            <div class="absolute top-3 right-4 flex gap-2">
              <span v-if="isAirborne" class="ui-badge-danger animate-pulse">AIRBORNE</span>
              <span v-if="isYawLocked" class="ui-badge-warn animate-pulse">YAW LOCK</span>
            </div>
          </div>

          <div
            class="flex flex-col overflow-hidden rounded-lg border border-[#27272a] bg-[#0a0a0c] p-4"
          >
            <div class="text-tcu-txt-dim mb-3 text-[10px] tracking-widest uppercase">Dynamics</div>

            <div class="mb-1 flex items-center justify-between">
              <span class="text-tcu-txt-muted text-xs">Attitude</span>
              <span
                class="text-xs font-bold"
                :class="
                  attitude === 'OVER'
                    ? 'text-danger'
                    : attitude === 'UNDER'
                      ? 'text-warn'
                      : 'text-accent'
                "
              >
                {{ attitude }}
              </span>
            </div>

            <div class="mb-4 flex items-center justify-between">
              <span class="text-tcu-txt-muted text-xs">Drive Style</span>
              <span class="text-accent-2 text-xs font-bold">{{
                t.drive_style_regime || 'CRUISE'
              }}</span>
            </div>

            <div class="mt-auto">
              <div class="mb-1 flex items-end justify-between">
                <span class="text-tcu-txt-dim text-[10px] uppercase">Grip Usage</span>
                <span class="text-xs font-bold text-white tabular-nums"
                  >{{ Math.round(gripUsage) }}%</span
                >
              </div>
              <div class="h-1.5 w-full overflow-hidden rounded-full bg-[#18181b]">
                <div
                  class="h-full transition-all duration-75"
                  :class="gripUsage > 90 ? 'bg-danger' : gripUsage > 75 ? 'bg-warn' : 'bg-accent'"
                  :style="{ width: `${Math.min(100, gripUsage)}%` }"
                ></div>
              </div>
            </div>
          </div>

          <div
            class="relative flex flex-col items-center justify-center overflow-hidden rounded-lg border border-[#27272a] bg-[#0a0a0c] p-3"
          >
            <div
              class="text-tcu-txt-dim absolute top-2 left-3 text-[10px] tracking-widest uppercase"
            >
              G-Force
            </div>

            <div
              class="relative mt-3 h-20 w-20 shrink-0 rounded-full border-2 border-[#27272a] bg-[#111113]"
            >
              <div class="absolute top-1/2 left-0 h-[1px] w-full bg-[#27272a]"></div>
              <div class="absolute top-0 left-1/2 h-full w-[1px] bg-[#27272a]"></div>
              <div
                class="absolute top-[25%] left-[25%] h-1/2 w-1/2 rounded-full border border-[#27272a]/50"
              ></div>

              <div
                class="absolute h-3 w-3 -translate-x-1/2 -translate-y-1/2 transform rounded-full bg-yellow-400 shadow-[0_0_8px_rgba(250,204,21,0.8)] transition-all duration-75"
                :style="gDotStyle"
              ></div>
            </div>

            <div class="mt-2 flex w-full shrink-0 justify-between px-2">
              <div class="flex flex-col items-center">
                <span class="text-tcu-txt-dim text-[9px]">LAT</span>
                <span class="text-xs font-bold text-white tabular-nums">{{ gLat.toFixed(2) }}</span>
              </div>
              <div class="flex flex-col items-center">
                <span class="text-tcu-txt-dim text-[9px]">LON</span>
                <span class="text-xs font-bold text-white tabular-nums">{{ gLon.toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="min-h-0 flex-1 basis-0">
        <DashboardChart :telemetry="telemetry" />
      </div>
    </div>

    <div
      v-else
      class="flex h-full flex-col items-center justify-center rounded-lg border border-dashed border-[#27272a] bg-[#0a0a0c] text-[#a1a1aa]"
    >
      <div class="mb-3 text-4xl font-black tracking-widest text-[#27272a]">OFFLINE</div>
      <div class="text-tcu-txt-dim flex items-center gap-2 text-sm tracking-widest uppercase">
        <div class="bg-danger h-2 w-2 animate-pulse rounded-full"></div>
        Awaiting UDP Telemetry...
      </div>
    </div>
  </div>
</template>

<style scoped>
  .tabular-nums {
    font-variant-numeric: tabular-nums;
  }
</style>
