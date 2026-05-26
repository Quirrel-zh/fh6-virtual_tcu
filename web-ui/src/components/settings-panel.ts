import { useDialog } from 'naive-ui'
import { useI18n } from 'vue-i18n'

export {
  CONFIG_TAB_IDS,
  hotkeyInputValue,
  sliderUnit,
  TAB_IDS,
  useSettingsPanel,
} from '@virtual-tcu/ui/dashboard'
export type { TabId } from '@virtual-tcu/ui/dashboard'

export function useConfirmReset(onConfirm: () => void) {
  const { t } = useI18n()
  const dialog = useDialog()

  function confirmReset() {
    dialog.warning({
      title: t('settings.reset'),
      content: t('settings.resetConfirm'),
      positiveText: t('modal.confirm'),
      negativeText: t('modal.cancel'),
      onPositiveClick: () => {
        onConfirm()
      },
    })
  }

  return { confirmReset }
}
