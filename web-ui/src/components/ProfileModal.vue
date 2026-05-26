<script setup lang="ts">
import { actionBtn, actionBtnCompact, actionBtnPrimary } from '@/styles/ui'
import { modalBindings, textareaValue } from './profile-modal'

const props = defineProps({
  open: { type: Boolean, required: true },
  mode: { type: String, required: true },
  title: { type: String, default: '' },
  text: { type: String, default: '' },
  readOnly: { type: Boolean, default: false },
})
const emit = defineEmits(['close', 'confirm', 'update:text'])
const b = modalBindings(props, emit)
</script>

<template>
  <div
    class="fixed inset-0 z-100 flex items-center justify-center bg-black/70 p-5"
    :class="open ? 'flex' : 'hidden'"
    @click="b.onBackdrop"
  >
    <div
      class="flex max-h-[80vh] w-full max-w-xl flex-col gap-3 rounded-xl border border-tcu-border bg-tcu-bg-1 p-5"
      @click.stop
    >
      <h3 class="m-0 text-base font-semibold">
        {{ title || $t('modal.profile') }}
      </h3>
      <textarea
        class="min-h-[200px] w-full resize-y rounded-md border border-tcu-border bg-tcu-bg-0 p-2.5 font-mono text-[11px] text-tcu-txt"
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
