export interface LogStatus {
  recording: boolean
  mode: string
  packets: number
  size_kb: number
}

export interface ShiftHistoryItem {
  ts: number
  action: string
  gear: number
  rpm_pct: number
  throttle: number
  brake: number
  reason?: string
  rule?: string
}

export interface SessionStats {
  duration_s: number
  upshifts: number
  downshifts: number
  kickdowns: number
  brake_downs: number
  predictives: number
  launches: number
  peak_rpm: number
  peak_speed: number
  peak_g_lat: number
  peak_g_lon: number
  peak_power_kw: number
  avg_throttle: number
  cars_driven: number
}

export interface TelemetrySnapshot {
  gear: number
  speed_kmh: number
  rpm: number
  rpm_max: number
  rpm_pct: number
  throttle: number
  brake: number
  tcu_state: string
  tcu_state_sub: string
  shift_hint?: string
  power_kw?: number
  torque_nm?: number
  turbo_bar?: number
  drivetrain?: string
  g_lat?: number
  g_lon?: number
  attitude?: string
  attitude_sub?: string
  grip_usage?: number
  peak_rpm?: number
  peak_g?: number
  calibrated?: boolean
  drive_style_index?: number
  drive_style_regime?: string
  peak_torque_rpm_pct?: number | null
  peak_power_rpm_pct?: number | null
  airborne?: boolean
  yaw_transient?: boolean
  session_stats?: SessionStats
  shift_history?: ShiftHistoryItem[]
  watchdog_stuck?: boolean
  log_status?: LogStatus
  power_curve_learned?: boolean
}
