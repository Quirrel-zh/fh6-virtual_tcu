import type { DriveMode } from '../types/ws'

export interface ModeDef {
  id: DriveMode
  i18nKey: string
}

export const DRIVE_MODES: ModeDef[] = [
  { id: 'COMFORT', i18nKey: 'comfort' },
  { id: 'DYNAMIC', i18nKey: 'dynamic' },
  { id: 'RACE', i18nKey: 'race' },
  { id: 'DRIFT', i18nKey: 'drift' },
  { id: 'OFFROAD', i18nKey: 'offroad' },
  { id: 'MANUAL', i18nKey: 'manual' },
]
