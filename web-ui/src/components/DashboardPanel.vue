<script setup>
import { toRefs, computed, ref, watch } from 'vue'

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

// MoTeC Style G-Force History Scatter Plot
const gHistory = ref([])
const MAX_G = 2.5 // S2/X class hypercar limits

watch(() => telemetry.value, (newT) => {
  if (!newT || !live.value) return
  
  const lat = newT.g_lat || 0
  const lon = newT.g_lon || 0
  
  gHistory.value.push({ lat, lon, id: Date.now() + Math.random() })
  if (gHistory.value.length > 12) {
    gHistory.value.shift()
  }
}, { deep: true })

const gDotStyle = computed(() => {
  const x = Math.max(-MAX_G, Math.min(MAX_G, gLat.value))
  const y = Math.max(-MAX_G, Math.min(MAX_G, gLon.value))
  const px = 50 + (x / MAX_G) * 50
  const py = 50 - (y / MAX_G) * 50
  return { left: `${px}%`, top: `${py}%` }
})

const getTrailStyle = (pt, index) => {
  const x = Math.max(-MAX_G, Math.min(MAX_G, pt.lat))
  const y = Math.max(-MAX_G, Math.min(MAX_G, pt.lon))
  const px = 50 + (x / MAX_G) * 50
  const py = 50 - (y / MAX_G) * 50
  const opacity = (index + 1) / 15
  return { left: `${px}%`, top: `${py}%`, opacity }
}
</script>

<template>
  <div class="h-full flex flex-col gap-3 p-4 bg-[#050505] font-mono text-[#e4e4e7] border-l border-[#1a1a24] select-none overflow-hidden">
    
    <div v-if="live && telemetry" class="flex flex-col h-full gap-3">
      
      <div class="flex gap-1 h-10 w-full px-2 rounded-md bg-[#0a0a0c] border border-[#27272a] items-center justify-between">
        <div v-for="i in 20" :key="i" 
             class="flex-1 h-5 rounded-[2px] transition-colors duration-75 border border-black/50" 
             :class="getLedColor(i, rpmPct)">
        </div>
      </div>

      <div class="grid grid-cols-[220px_1fr_180px] gap-3 h-[240px]">
        
        <div class="flex flex-col gap-3">
          <div class="flex-1 flex flex-col justify-center items-center bg-[#0a0a0c] border border-[#27272a] rounded-lg shadow-inner relative overflow-hidden">
            <div v-if="hint" class="absolute top-2 left-0 w-full text-center text-accent font-bold animate-pulse text-sm tracking-widest z-10">
              {{ hint }}
            </div>
            
            <div class="text-[140px] font-black leading-none tabular-nums tracking-tighter" 
                 :class="state === 'SHIFTING' ? 'text-accent-2' : gear === 'R' ? 'text-warn' : 'text-white'">
              {{ gear }}
            </div>
            <div class="text-[10px] text-tcu-txt-dim uppercase tracking-widest mt-1 absolute bottom-3">
              {{ t.drivetrain || 'DRIVETRAIN' }}
            </div>
          </div>
          
          <div class="h-24 flex flex-col justify-center items-center bg-[#0a0a0c] border border-[#27272a] rounded-lg">
            <div class="text-6xl font-bold tracking-tight text-white tabular-nums">{{ speed }}</div>
            <div class="text-[10px] text-tcu-txt-dim uppercase tracking-widest mt-1">KM/H</div>
          </div>
        </div>
        
        <div class="flex flex-col gap-3">
          <div class="flex-1 flex flex-col justify-center bg-[#0a0a0c] border border-[#27272a] rounded-lg p-5 relative">
            
            <div class="flex justify-between items-end mb-2">
              <div class="text-7xl font-bold tracking-tight tabular-nums" :class="rpmPct > 0.9 ? 'text-danger' : 'text-warn'">
                {{ rpm }}
              </div>
              <div class="text-right">
                <div class="text-sm font-bold text-tcu-txt-dim tabular-nums">MAX {{ rpmMax }}</div>
                <div class="text-[10px] text-tcu-txt-dim uppercase tracking-widest">RPM</div>
              </div>
            </div>

            <div class="h-6 w-full bg-[#18181b] rounded-sm mt-4 border border-[#27272a] relative overflow-hidden">
              <div class="absolute h-full left-0 top-0 transition-all duration-75"
                   :class="rpmPct > 0.9 ? 'bg-danger' : rpmPct > 0.7 ? 'bg-warn' : 'bg-accent'"
                   :style="{ width: `${Math.min(100, rpmPct * 100)}%` }">
              </div>
              <div v-if="t.peak_torque_rpm_pct" class="absolute h-full w-0.5 bg-blue-500 z-10" :style="{ left: `${t.peak_torque_rpm_pct * 100}%` }"></div>
              <div v-if="t.peak_power_rpm_pct" class="absolute h-full w-0.5 bg-purple-500 z-10" :style="{ left: `${t.peak_power_rpm_pct * 100}%` }"></div>
            </div>
            <div class="flex justify-between w-full mt-1 px-1">
              <span class="text-[9px] text-blue-500">PEAK TQ</span>
              <span class="text-[9px] text-purple-500">PEAK HP</span>
            </div>

          </div>

          <div class="grid grid-cols-3 gap-3 h-20">
            <div class="bg-[#0a0a0c] border border-[#27272a] rounded-lg p-3 flex flex-col justify-between">
              <span class="text-[10px] text-tcu-txt-dim uppercase tracking-widest">Power</span>
              <div class="text-2xl font-bold text-white tabular-nums">{{ powerKw }} <span class="text-xs text-tcu-txt-dim">kW</span></div>
            </div>
            <div class="bg-[#0a0a0c] border border-[#27272a] rounded-lg p-3 flex flex-col justify-between">
              <span class="text-[10px] text-tcu-txt-dim uppercase tracking-widest">Torque</span>
              <div class="text-2xl font-bold text-white tabular-nums">{{ torqueNm }} <span class="text-xs text-tcu-txt-dim">Nm</span></div>
            </div>
            <div class="bg-[#0a0a0c] border border-[#27272a] rounded-lg p-3 flex flex-col justify-between relative overflow-hidden">
              <span class="text-[10px] text-tcu-txt-dim uppercase tracking-widest z-10">Turbo</span>
              <div class="text-2xl font-bold text-accent-2 tabular-nums z-10">{{ turboBar }} <span class="text-xs text-tcu-txt-dim">Bar</span></div>
              <div class="absolute bottom-0 left-0 w-full bg-accent-2/20 transition-all duration-75" :style="{ height: `${(t.turbo_bar / 2.0) * 100}%` }"></div>
            </div>
          </div>
        </div>

        <div class="bg-[#0a0a0c] border border-[#27272a] rounded-lg p-4 flex justify-between gap-2">
          
          <div class="flex flex-col items-center justify-end w-10 h-full gap-2">
            <span class="text-[10px] font-bold text-white tabular-nums">{{ Math.round(clutch) }}</span>
            <div class="flex-1 w-6 bg-[#18181b] border border-[#27272a] rounded flex items-end overflow-hidden">
              <div class="w-full bg-blue-500 transition-all duration-75" :style="{ height: `${clutch}%` }"></div>
            </div>
            <span class="text-[10px] text-tcu-txt-dim uppercase">CLT</span>
          </div>

          <div class="flex flex-col items-center justify-end w-10 h-full gap-2">
            <span class="text-[10px] font-bold text-white tabular-nums">{{ Math.round(brake) }}</span>
            <div class="flex-1 w-6 bg-[#18181b] border border-[#27272a] rounded flex items-end overflow-hidden">
              <div class="w-full bg-danger transition-all duration-75" :style="{ height: `${brake}%` }"></div>
            </div>
            <span class="text-[10px] text-tcu-txt-dim uppercase">BRK</span>
          </div>

          <div class="flex flex-col items-center justify-end w-10 h-full gap-2">
            <span class="text-[10px] font-bold text-white tabular-nums">{{ Math.round(throttle) }}</span>
            <div class="flex-1 w-6 bg-[#18181b] border border-[#27272a] rounded flex items-end overflow-hidden">
              <div class="w-full bg-accent transition-all duration-75" :style="{ height: `${throttle}%` }"></div>
            </div>
            <span class="text-[10px] text-tcu-txt-dim uppercase">THR</span>
          </div>

        </div>
      </div>

      <div class="grid grid-cols-[1fr_200px_200px] gap-3 flex-1">
        
        <div class="bg-[#0a0a0c] border rounded-lg p-5 flex flex-col justify-center relative overflow-hidden"
             :class="state === 'SHIFTING' ? 'border-accent-2/50 bg-accent-2/5' : state.includes('LOCK') || state.includes('BLOCKED') ? 'border-danger/50 bg-danger/5' : 'border-[#27272a]'">
          <div class="text-[10px] text-tcu-txt-dim uppercase tracking-widest absolute top-3 left-4">TCU Controller Status</div>
          <div class="text-3xl font-bold tracking-wide mt-2" 
               :class="state.includes('DOWN') ? 'text-warn' : state.includes('UP') ? 'text-accent' : 'text-white'">
            {{ state }}
          </div>
          <div class="text-sm text-tcu-txt-muted uppercase mt-1 font-semibold">{{ subState }}</div>
          
          <div class="absolute top-3 right-4 flex gap-2">
             <span v-if="isAirborne" class="ui-badge-danger animate-pulse">AIRBORNE</span>
             <span v-if="isYawLocked" class="ui-badge-warn animate-pulse">YAW LOCK</span>
          </div>
        </div>

        <div class="bg-[#0a0a0c] border border-[#27272a] rounded-lg p-4 flex flex-col">
          <div class="text-[10px] text-tcu-txt-dim uppercase tracking-widest mb-3">Dynamics</div>
          
          <div class="flex justify-between items-center mb-1">
            <span class="text-xs text-tcu-txt-muted">Attitude</span>
            <span class="text-xs font-bold" :class="attitude === 'OVER' ? 'text-danger' : attitude === 'UNDER' ? 'text-warn' : 'text-accent'">
              {{ attitude }}
            </span>
          </div>
          
          <div class="flex justify-between items-center mb-4">
            <span class="text-xs text-tcu-txt-muted">Drive Style</span>
            <span class="text-xs font-bold text-accent-2">{{ t.drive_style_regime || 'CRUISE' }}</span>
          </div>

          <div class="mt-auto">
            <div class="flex justify-between items-end mb-1">
              <span class="text-[10px] text-tcu-txt-dim uppercase">Grip Usage</span>
              <span class="text-xs font-bold tabular-nums text-white">{{ Math.round(gripUsage) }}%</span>
            </div>
            <div class="h-1.5 w-full bg-[#18181b] rounded-full overflow-hidden">
              <div class="h-full transition-all duration-75"
                   :class="gripUsage > 90 ? 'bg-danger' : gripUsage > 75 ? 'bg-warn' : 'bg-accent'"
                   :style="{ width: `${Math.min(100, gripUsage)}%` }">
              </div>
            </div>
          </div>
        </div>

        <div class="bg-[#0a0a0c] border border-[#27272a] rounded-lg p-3 flex flex-col items-center justify-center relative">
          <div class="text-[10px] text-tcu-txt-dim uppercase tracking-widest absolute top-2 left-3">G-Force</div>
          
          <div class="w-24 h-24 mt-4 rounded-full border-2 border-[#27272a] bg-[#111113] relative overflow-hidden">
            <div class="absolute top-1/2 left-0 w-full h-[1px] bg-[#27272a]"></div>
            <div class="absolute top-0 left-1/2 w-[1px] h-full bg-[#27272a]"></div>
            <div class="absolute top-[25%] left-[25%] w-1/2 h-1/2 rounded-full border border-[#27272a]/50"></div>
            
            <div v-for="(pt, i) in gHistory" :key="pt.id"
                 class="absolute w-2 h-2 bg-yellow-400 rounded-full transform -translate-x-1/2 -translate-y-1/2 transition-none pointer-events-none"
                 :style="getTrailStyle(pt, i)">
            </div>
            
            <div class="absolute w-3 h-3 bg-yellow-400 rounded-full shadow-[0_0_8px_rgba(250,204,21,0.8)] transform -translate-x-1/2 -translate-y-1/2 transition-all duration-75 z-10"
                 :style="gDotStyle">
            </div>
          </div>

          <div class="w-full flex justify-between px-2 mt-3">
            <div class="flex flex-col items-center">
              <span class="text-[9px] text-tcu-txt-dim">LAT</span>
              <span class="text-xs font-bold tabular-nums text-white">{{ gLat.toFixed(2) }}</span>
            </div>
            <div class="flex flex-col items-center">
              <span class="text-[9px] text-tcu-txt-dim">LON</span>
              <span class="text-xs font-bold tabular-nums text-white">{{ gLon.toFixed(2) }}</span>
            </div>
          </div>

        </div>

      </div>
      
    </div>

    <div v-else class="flex flex-col items-center justify-center h-full text-[#a1a1aa] bg-[#0a0a0c] rounded-lg border border-[#27272a] border-dashed">
      <div class="text-4xl font-black mb-3 tracking-widest text-[#27272a]">OFFLINE</div>
      <div class="text-sm uppercase tracking-widest text-tcu-txt-dim flex items-center gap-2">
        <div class="w-2 h-2 rounded-full bg-danger animate-pulse"></div>
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