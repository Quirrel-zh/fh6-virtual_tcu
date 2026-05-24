export interface FeatureToggle {
  key: string
  i18nKey: string
}

export const FEATURE_TOGGLES: FeatureToggle[] = [
  { key: 'feat_cornering_lock', i18nKey: 'corneringLock' },
  { key: 'feat_launch_control', i18nKey: 'launchControl' },
  { key: 'feat_brake_curve', i18nKey: 'brakeCurve' },
  { key: 'feat_drivetrain_aware', i18nKey: 'drivetrainAware' },
  { key: 'feat_shift_advisor', i18nKey: 'shiftAdvisor' },
  { key: 'feat_reverse_hold', i18nKey: 'reverseHold' },
  { key: 'feat_sound_beep', i18nKey: 'soundBeep' },
  { key: 'feat_engine_brake', i18nKey: 'engineBrake' },
  { key: 'feat_power_curve', i18nKey: 'powerCurve' },
  { key: 'feat_turbo_compensate', i18nKey: 'turboCompensate' },
  { key: 'feat_airtime_lock', i18nKey: 'airtimeLock' },
  { key: 'feat_transient_lock', i18nKey: 'transientLock' },
  { key: 'feat_drive_style', i18nKey: 'driveStyle' },
  { key: 'feat_discord_rpc', i18nKey: 'discordRpc' },
]

export interface SliderDef {
  key: string
  i18nKey: string
  min: number
  max: number
  step?: number
  unit?: 'percent' | 'rpm' | 'raw'
  panel?: 'settings' | 'extras'
  hintKey?: string
}

export const SETTING_SLIDERS: SliderDef[] = [
  { key: 'launch_rpm', i18nKey: 'launchRpm', min: 2000, max: 8000, step: 100, unit: 'rpm', panel: 'settings' },
  { key: 'daily_up_wot', i18nKey: 'dailyUpWot', min: 50, max: 95, panel: 'settings' },
  {
    key: 'track_up_wot',
    i18nKey: 'trackUpWot',
    min: 70,
    max: 99,
    panel: 'settings',
    hintKey: 'trackFallbackHint',
  },
  { key: 'mud_up_wot', i18nKey: 'mudUpWot', min: 75, max: 98, panel: 'settings' },
  { key: 'mud_down_rpm', i18nKey: 'mudDownRpm', min: 35, max: 70, panel: 'settings' },
  { key: 'brake_thr', i18nKey: 'brakeThr', min: 20, max: 80, panel: 'settings' },
  { key: 'cornering_yaw', i18nKey: 'corneringYaw', min: 10, max: 50, unit: 'raw', panel: 'settings' },
  { key: 'daily_up_idle', i18nKey: 'dailyUpIdle', min: 20, max: 70, panel: 'extras' },
  { key: 'daily_up_mid', i18nKey: 'dailyUpMid', min: 30, max: 85, panel: 'extras' },
  { key: 'track_up_idle', i18nKey: 'trackUpIdle', min: 40, max: 90, panel: 'extras' },
  { key: 'track_up_mid', i18nKey: 'trackUpMid', min: 50, max: 95, panel: 'extras' },
  { key: 'kickdown_pedal', i18nKey: 'kickdownPedal', min: 50, max: 100, panel: 'extras' },
  { key: 'kickdown_rpm', i18nKey: 'kickdownRpm', min: 30, max: 80, panel: 'extras' },
  { key: 'coast_down_rpm', i18nKey: 'coastDownRpm', min: 10, max: 50, panel: 'extras' },
]

export const HOTKEY_FIELDS = [
  { key: 'hotkey_cycle_mode', i18nKey: 'cycleMode', placeholder: 'f9' },
  { key: 'hotkey_toggle_log', i18nKey: 'toggleLog', placeholder: 'f8' },
] as const

export const SHIFT_KEY_FIELDS = [
  { key: 'shift_key_up', i18nKey: 'shiftKeyUp', placeholder: 'e' },
  { key: 'shift_key_down', i18nKey: 'shiftKeyDown', placeholder: 'q' },
] as const

export const SETTING_GROUPS: { i18nKey: string, keys: string[], hintKey?: string }[] = [
  { i18nKey: 'launchControl', keys: ['launch_rpm'] },
  { i18nKey: 'daily', keys: ['daily_up_wot'] },
  { i18nKey: 'track', keys: ['track_up_wot'], hintKey: 'trackFallbackHint' },
  { i18nKey: 'mud', keys: ['mud_up_wot', 'mud_down_rpm'] },
  { i18nKey: 'common', keys: ['brake_thr', 'cornering_yaw'] },
]
