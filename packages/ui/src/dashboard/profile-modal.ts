export function textareaValue(event: Event): string {
  const el = event.target
  if (el instanceof HTMLTextAreaElement)
    return el.value
  return ''
}

export function modalBindings(
  props: { open: boolean },
  emit: (e: 'close' | 'confirm', ...args: unknown[]) => void,
) {
  return {
    onBackdrop: (e: MouseEvent) => {
      if (e.target === e.currentTarget)
        emit('close')
    },
  }
}
