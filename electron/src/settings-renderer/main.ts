import { i18n } from '@virtual-tcu/shared/i18n'
import { createApp } from 'vue'
import SettingsApp from './SettingsApp.vue'
import './styles.css'

createApp(SettingsApp).use(i18n).mount('#app')
