import type { LogStatus, SessionStats, ShiftHistoryItem, TelemetrySnapshot } from './telemetry'

export type DriveMode = 'DAILY' | 'TRACK' | 'MUD' | 'MANUAL'

export type ConfigMap = Record<string, string | number | boolean>

export interface InitPayload {
  mode: DriveMode
  live: boolean
  shift_count: number
  packets_total: number
  config: ConfigMap
  defaults: ConfigMap
  log_status: LogStatus
}

export interface StatePayload {
  mode?: DriveMode
  live?: boolean
  shift_count?: number
  packets_total?: number
}

export type WsOutbound =
  | { type: 'set_mode'; mode: string }
  | { type: 'set_config'; key: string; value: string | number | boolean }
  | { type: 'reset_config' }
  | { type: 'log_start'; mode: string }
  | { type: 'log_stop' }
  | { type: 'request_graph' }
  | { type: 'export_profile' }
  | { type: 'import_profile'; data: unknown }

export type WsInbound =
  | { type: 'init'; data: InitPayload }
  | { type: 'telemetry'; data: TelemetrySnapshot }
  | { type: 'state'; data: StatePayload }
  | { type: 'config_reset'; data: ConfigMap }
  | { type: 'log_status'; data: LogStatus; last_file?: string }
  | { type: 'profile_export'; data: unknown }
  | { type: 'profile_imported'; ok: boolean; data?: ConfigMap; error?: string }
  | { type: 'graph_data'; data: unknown }

export interface TcuUiState {
  connected: boolean
  live: boolean
  mode: DriveMode
  shiftCount: number
  packetsTotal: number
  config: ConfigMap
  defaults: ConfigMap
  telemetry: TelemetrySnapshot | null
  logStatus: LogStatus | null
  shiftHistory: ShiftHistoryItem[]
  sessionStats: SessionStats | null
  watchdogStuck: boolean
}
