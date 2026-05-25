import type { DriveMode } from '../types/ws'

export const MODE_PILL: Record<DriveMode, string> = {
  COMFORT: 'border-mode-comfort bg-mode-comfort/10 text-mode-comfort',
  DYNAMIC: 'border-mode-dynamic bg-mode-dynamic/10 text-mode-dynamic',
  RACE: 'border-mode-race bg-mode-race/10 text-mode-race',
  DRIFT: 'border-mode-drift bg-mode-drift/10 text-mode-drift',
  OFFROAD: 'border-mode-offroad bg-mode-offroad/10 text-mode-offroad',
  MANUAL: 'border-mode-manual bg-mode-manual/10 text-mode-manual',
}

export const MODE_BTN_ACTIVE: Record<DriveMode, string> = {
  COMFORT: 'border-mode-comfort text-mode-comfort shadow-[0_0_0_1px_currentColor,0_0_16px_-4px_currentColor]',
  DYNAMIC: 'border-mode-dynamic text-mode-dynamic shadow-[0_0_0_1px_currentColor,0_0_16px_-4px_currentColor]',
  RACE: 'border-mode-race text-mode-race shadow-[0_0_0_1px_currentColor,0_0_16px_-4px_currentColor]',
  DRIFT: 'border-mode-drift text-mode-drift shadow-[0_0_0_1px_currentColor,0_0_16px_-4px_currentColor]',
  OFFROAD: 'border-mode-offroad text-mode-offroad shadow-[0_0_0_1px_currentColor,0_0_16px_-4px_currentColor]',
  MANUAL: 'border-mode-manual text-mode-manual shadow-[0_0_0_1px_currentColor,0_0_16px_-4px_currentColor]',
}

export const REGIME_PILL: Record<string, string> = {
  CRUISE: 'bg-mode-comfort/15 text-mode-comfort',
  ADAPTIVE: 'bg-mode-dynamic/15 text-mode-dynamic',
  SPORT: 'bg-mode-race/15 text-mode-race',
}

export const ATTITUDE_CLASS: Record<string, string> = {
  NEUTRAL: 'text-accent',
  UNDER: 'text-accent-2',
  OVER: 'text-warn',
  SPIN: 'text-danger',
}

export const MODE_BTN_BASE =
  'relative mb-2 grid w-full grid-cols-[1fr_auto] items-center gap-2.5 overflow-hidden rounded-[10px] border border-tcu-border bg-tcu-bg-1 px-3.5 py-3 text-left text-sm font-medium text-tcu-txt-muted transition before:absolute before:top-0 before:bottom-0 before:left-0 before:w-0.75 before:bg-transparent before:transition-colors hover:translate-x-0.5 hover:bg-tcu-bg-2 hover:text-tcu-txt'

export function modeBtnClass(id: DriveMode, active: boolean): string {
  return active
    ? `${MODE_BTN_BASE} bg-tcu-bg-2 before:bg-current ${MODE_BTN_ACTIVE[id]}`
    : MODE_BTN_BASE
}
