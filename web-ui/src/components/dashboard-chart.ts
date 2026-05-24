import type { TelemetrySnapshot } from '@/types/telemetry'
import { computed, onMounted, onUnmounted, ref, shallowRef, watch } from 'vue'

const MAX_POINTS = 300
const SPEED_CAP_KMH = 350
const PAD = { top: 14, right: 10, bottom: 22, left: 36 }

export interface ChartLegendItem {
  key: string
  label: string
  color: string
  value: string
}

interface SeriesDef {
  key: string
  label: string
  color: string
  data: number[]
  format: (v: number) => string
}

export function useDashboardChart(getTelemetry: () => TelemetrySnapshot | null) {
  const canvasRef = ref<HTMLCanvasElement | null>(null)
  const rpm = shallowRef<number[]>([])
  const thr = shallowRef<number[]>([])
  const brk = shallowRef<number[]>([])
  const spd = shallowRef<number[]>([])
  const gearMarks = shallowRef<number[]>([])
  let lastGear: number | null = null

  const latest = computed(() => getTelemetry())

  const legend = computed<ChartLegendItem[]>(() => {
    const t = latest.value
    const last = (arr: number[]) => (arr.length ? arr[arr.length - 1] : 0)
    const thrVal = last(thr.value)
    const brkVal = last(brk.value)
    const spdVal = last(spd.value) * SPEED_CAP_KMH
    return [
      { key: 'rpm', label: 'RPM', color: '#4ade80', value: `${Math.round(t?.rpm ?? 0)}` },
      { key: 'thr', label: 'THR', color: '#22d3ee', value: `${Math.round(thrVal * 100)}%` },
      { key: 'brk', label: 'BRK', color: '#ef4444', value: `${Math.round(brkVal * 100)}%` },
      { key: 'spd', label: 'SPD', color: '#a78bfa', value: `${Math.round(spdVal)} km/h` },
    ]
  })

  function push(t: TelemetrySnapshot) {
    rpm.value = [...rpm.value, t.rpm_pct || 0].slice(-MAX_POINTS)
    thr.value = [...thr.value, t.throttle || 0].slice(-MAX_POINTS)
    brk.value = [...brk.value, t.brake || 0].slice(-MAX_POINTS)
    spd.value = [...spd.value, Math.min(1, (t.speed_kmh || 0) / SPEED_CAP_KMH)].slice(-MAX_POINTS)

    if (lastGear !== null && t.gear !== lastGear)
      gearMarks.value = [...gearMarks.value, rpm.value.length - 1].slice(-24)
    lastGear = t.gear

    draw()
  }

  function seriesList(): SeriesDef[] {
    return [
      { key: 'rpm', label: 'RPM', color: '#4ade80', data: rpm.value, format: v => `${Math.round(v * 100)}%` },
      { key: 'thr', label: 'THR', color: '#22d3ee', data: thr.value, format: v => `${Math.round(v * 100)}%` },
      { key: 'brk', label: 'BRK', color: '#ef4444', data: brk.value, format: v => `${Math.round(v * 100)}%` },
      { key: 'spd', label: 'SPD', color: '#a78bfa', data: spd.value, format: v => `${Math.round(v * SPEED_CAP_KMH)}` },
    ]
  }

  function draw() {
    const canvas = canvasRef.value
    if (!canvas || canvas.clientWidth === 0 || canvas.clientHeight === 0)
      return

    const ctx = canvas.getContext('2d')
    if (!ctx)
      return

    if (canvas.width !== canvas.clientWidth || canvas.height !== canvas.clientHeight) {
      canvas.width = canvas.clientWidth
      canvas.height = canvas.clientHeight
    }

    const W = canvas.width
    const H = canvas.height
    const plotW = W - PAD.left - PAD.right
    const plotH = H - PAD.top - PAD.bottom

    ctx.clearRect(0, 0, W, H)

    ctx.fillStyle = 'rgba(255,255,255,0.35)'
    ctx.font = '10px ui-monospace, monospace'
    ctx.textAlign = 'right'
    ctx.textBaseline = 'middle'
    for (let i = 0; i <= 4; i++) {
      const pct = 1 - i / 4
      const y = PAD.top + (plotH / 4) * i
      ctx.fillText(`${Math.round(pct * 100)}%`, PAD.left - 6, y)

      ctx.strokeStyle = 'rgba(255,255,255,0.06)'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(PAD.left, y)
      ctx.lineTo(W - PAD.right, y)
      ctx.stroke()
    }

    ctx.fillStyle = 'rgba(113,113,122,0.9)'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'top'
    ctx.fillText('~10s window', PAD.left + plotW / 2, H - PAD.bottom + 6)

    for (const markIdx of gearMarks.value) {
      if (markIdx >= rpm.value.length)
        continue
      const x = PAD.left + (markIdx / Math.max(1, MAX_POINTS - 1)) * plotW
      ctx.strokeStyle = 'rgba(250,204,21,0.35)'
      ctx.lineWidth = 1
      ctx.setLineDash([3, 4])
      ctx.beginPath()
      ctx.moveTo(x, PAD.top)
      ctx.lineTo(x, PAD.top + plotH)
      ctx.stroke()
      ctx.setLineDash([])
    }

    for (const s of seriesList()) {
      if (s.data.length < 2)
        continue
      ctx.strokeStyle = s.color
      ctx.lineWidth = 1.6
      ctx.lineJoin = 'round'
      ctx.beginPath()
      for (let i = 0; i < s.data.length; i++) {
        const x = PAD.left + (i / (MAX_POINTS - 1)) * plotW
        const y = PAD.top + plotH - s.data[i] * plotH
        if (i === 0)
          ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      }
      ctx.stroke()
    }
  }

  let ro: ResizeObserver | null = null

  onMounted(() => {
    ro = new ResizeObserver(() => draw())
    watch(canvasRef, (el) => {
      if (el)
        ro?.observe(el)
    }, { immediate: true })
  })

  onUnmounted(() => ro?.disconnect())

  watch(
    () => getTelemetry(),
    (t) => {
      if (t)
        push(t)
    },
  )

  return { canvasRef, legend, draw }
}
