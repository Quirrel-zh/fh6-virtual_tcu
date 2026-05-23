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
  { key: 'comfort_up_wot', i18nKey: 'comfortUpWot', min: 50, max: 95, panel: 'settings' },
  { key: 'dynamic_up_wot', i18nKey: 'dynamicUpWot', min: 60, max: 98, panel: 'settings' },
  {
    key: 'race_up_wot',
    i18nKey: 'raceUpWot',
    min: 70,
    max: 99,
    panel: 'settings',
    hintKey: 'raceFallbackHint',
  },
  { key: 'offroad_up_wot', i18nKey: 'offroadUpWot', min: 75, max: 98, panel: 'settings' },
  { key: 'offroad_down_rpm', i18nKey: 'offroadDownRpm', min: 35, max: 70, panel: 'settings' },
  { key: 'brake_thr', i18nKey: 'brakeThr', min: 20, max: 80, panel: 'settings' },
  { key: 'cornering_yaw', i18nKey: 'corneringYaw', min: 10, max: 50, unit: 'raw', panel: 'settings' },
  { key: 'comfort_up_idle', i18nKey: 'comfortUpIdle', min: 20, max: 70, panel: 'extras' },
  { key: 'comfort_up_mid', i18nKey: 'comfortUpMid', min: 30, max: 85, panel: 'extras' },
  { key: 'dynamic_up_idle', i18nKey: 'dynamicUpIdle', min: 30, max: 80, panel: 'extras' },
  { key: 'dynamic_up_mid', i18nKey: 'dynamicUpMid', min: 40, max: 90, panel: 'extras' },
  { key: 'race_up_idle', i18nKey: 'raceUpIdle', min: 40, max: 90, panel: 'extras' },
  { key: 'race_up_mid', i18nKey: 'raceUpMid', min: 50, max: 95, panel: 'extras' },
  { key: 'kickdown_pedal', i18nKey: 'kickdownPedal', min: 50, max: 100, panel: 'extras' },
  { key: 'kickdown_rpm', i18nKey: 'kickdownRpm', min: 30, max: 80, panel: 'extras' },
  { key: 'coast_down_rpm', i18nKey: 'coastDownRpm', min: 10, max: 50, panel: 'extras' },
  { key: 'drift_up', i18nKey: 'driftUp', min: 70, max: 99, panel: 'extras' },
  { key: 'drift_down', i18nKey: 'driftDown', min: 40, max: 85, panel: 'extras' },
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
  { i18nKey: 'comfort', keys: ['comfort_up_wot'] },
  { i18nKey: 'dynamic', keys: ['dynamic_up_wot'] },
  { i18nKey: 'race', keys: ['race_up_wot'], hintKey: 'raceFallbackHint' },
  { i18nKey: 'offroad', keys: ['offroad_up_wot', 'offroad_down_rpm'] },
  { i18nKey: 'common', keys: ['brake_thr', 'cornering_yaw'] },
]
