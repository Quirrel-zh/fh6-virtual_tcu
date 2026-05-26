import type { SliderDef } from '../config/settings'
import type { ConfigMap } from '../types/ws'

export function sliderUnit(s: Pick<SliderDef, 'unit'>): string {
  if (s.unit === 'rpm') return ' rpm'
  if (s.unit === 'raw') return ''
  return '%'
}

export function formatSliderValue(key: string, value: number, unit?: SliderDef['unit']): string {
  if (unit === 'rpm' || key === 'launch_rpm') return String(Math.round(value))
  if (unit === 'raw' || key === 'cornering_yaw') return String(Math.round(value))
  return `${Math.round(value)}%`
}

export function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const sec = Math.floor(seconds % 60)
  return `${m}m ${sec.toString().padStart(2, '0')}s`
}

export function gearDisplay(gear: number, labels: { reverse: string; neutral: string }): string {
  if (gear === 0) return labels.reverse
  if (gear === -1) return labels.neutral
  return String(gear)
}

export function configBool(config: ConfigMap, key: string): boolean {
  return !!config[key]
}
