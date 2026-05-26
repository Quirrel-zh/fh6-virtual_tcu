<script setup lang="ts">
import { actionBtn, actionBtnCompact, actionBtnPrimary } from '../styles/ui'
import { modalBindings, textareaValue } from './profile-modal'

const props = defineProps<{
  open: boolean
  mode: string
  title?: string
  text?: string
  readOnly?: boolean
}>()
const emit = defineEmits<{
  close: []
  confirm: []
  'update:text': [value: string]
}>()
const b = modalBindings(props, emit)
</script>

<template>
  <div
    class="fixed inset-0 z-100 flex items-center justify-center bg-black/70 p-5"
    :class="open ? 'flex' : 'hidden'"
    @click="b.onBackdrop"
  >
    <div
      class="border-tcu-border bg-tcu-bg-1 flex max-h-[80vh] w-full max-w-xl flex-col gap-3 rounded-xl border p-5"
      @click.stop
    >
      <h3 class="m-0 text-base font-semibold">
        {{ title || $t('modal.profile') }}
      </h3>
      <textarea
        class="border-tcu-border bg-tcu-bg-0 text-tcu-txt min-h-[200px] w-full resize-y rounded-md border p-2.5 font-mono text-[11px]"
        :value="text"
        spellcheck="false"
        :readonly="readOnly"
        @input="emit('update:text', textareaValue($event))"
      />
      <div class="flex justify-end gap-2">
        <button type="button" :class="[actionBtn, actionBtnCompact]" @click="emit('close')">
          {{ $t('modal.cancel') }}
        </button>
        <button type="button" :class="[actionBtnPrimary, actionBtnCompact]" @click="emit('confirm')">
          {{ $t('modal.confirm') }}
        </button>
      </div>
    </div>
  </div>
</template>
