import { createApp } from 'vue'
import { i18n } from '@web-ui/i18n'
import SettingsApp from './SettingsApp.vue'
import './styles.css'

createApp(SettingsApp).use(i18n).mount('#app')
