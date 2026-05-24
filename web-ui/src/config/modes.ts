import type { DriveMode } from '@/types/ws'

export interface ModeDef {
  id: DriveMode
  i18nKey: string
}

export const DRIVE_MODES: ModeDef[] = [
  { id: 'DAILY', i18nKey: 'daily' },
  { id: 'TRACK', i18nKey: 'track' },
  { id: 'MUD', i18nKey: 'mud' },
  { id: 'MANUAL', i18nKey: 'manual' },
]
