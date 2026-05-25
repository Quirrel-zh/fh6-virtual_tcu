import { createI18n } from 'vue-i18n'
import en from '../locales/en'
import zhCN from '../locales/zh-CN'

export type AppLocale = 'en' | 'zh-CN'

const STORAGE_KEY = 'tcu-ui-locale'

function detectLocale(): AppLocale {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === 'en' || saved === 'zh-CN')
    return saved
  const lang = navigator.language.toLowerCase()
  return lang.startsWith('zh') ? 'zh-CN' : 'en'
}

export const i18n = createI18n({
  legacy: false,
  locale: detectLocale(),
  fallbackLocale: 'en',
  messages: {
    en,
    'zh-CN': zhCN,
  },
})

export function setAppLocale(locale: AppLocale) {
  i18n.global.locale.value = locale
  localStorage.setItem(STORAGE_KEY, locale)
  document.documentElement.lang = locale === 'zh-CN' ? 'zh-CN' : 'en'
}

document.documentElement.lang = i18n.global.locale.value === 'zh-CN' ? 'zh-CN' : 'en'
