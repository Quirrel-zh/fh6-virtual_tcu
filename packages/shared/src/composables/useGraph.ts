import type { TelemetrySnapshot } from '../types/telemetry'
import { onMounted, onUnmounted, ref, shallowRef, watch } from 'vue'

const MAX_POINTS = 300

export function useGraph(getTelemetry: () => TelemetrySnapshot | null) {
  const canvasRef = ref<HTMLCanvasElement | null>(null)
  const rpm = shallowRef<number[]>([])
  const thr = shallowRef<number[]>([])
  const brk = shallowRef<number[]>([])

  function push(t: TelemetrySnapshot) {
    rpm.value = [...rpm.value, t.rpm_pct || 0].slice(-MAX_POINTS)
    thr.value = [...thr.value, t.throttle || 0].slice(-MAX_POINTS)
    brk.value = [...brk.value, t.brake || 0].slice(-MAX_POINTS)
    draw()
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
    ctx.clearRect(0, 0, W, H)
    ctx.strokeStyle = 'rgba(255,255,255,0.04)'
    ctx.lineWidth = 1
    for (let i = 0; i <= 4; i++) {
      const y = (H / 4) * i
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(W, y)
      ctx.stroke()
    }

    const series = [
      { data: rpm.value, color: '#4ade80' },
      { data: thr.value, color: '#22d3ee' },
      { data: brk.value, color: '#ef4444' },
    ]

    for (const s of series) {
      if (s.data.length < 2)
        continue
      ctx.strokeStyle = s.color
      ctx.lineWidth = 1.5
      ctx.beginPath()
      for (let i = 0; i < s.data.length; i++) {
        const x = (i / MAX_POINTS) * W
        const y = H - s.data[i] * H
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

  return { canvasRef, push, draw }
}
