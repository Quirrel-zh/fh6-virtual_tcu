import type { AppLocale } from '@virtual-tcu/shared/i18n'
import { setAppLocale } from '@virtual-tcu/shared/i18n'

export const localeOptions: { value: AppLocale, labelKey: string }[] = [
  { value: 'en', labelKey: 'locale.en' },
  { value: 'zh-CN', labelKey: 'locale.zh' },
]

export function onLocaleChange(e: Event) {
  const v = (e.target as HTMLSelectElement).value as AppLocale
  setAppLocale(v)
}
