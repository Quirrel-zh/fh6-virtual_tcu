<script setup>
import { hotkeyInput } from '@/styles/ui'
import { useConfigTextInput } from './config-text-input'

const props = defineProps({
  configKey: { type: String, required: true },
  config: { type: Object, required: true },
  placeholder: { type: String, default: '' },
  maxlength: { type: Number, default: 6 },
})

const emit = defineEmits(['commit'])

const { draft, onFocus, onInput, commit } = useConfigTextInput(
  () => props.config,
  () => props.configKey,
  (key, value) => emit('commit', key, value),
)
</script>

<template>
  <input
    type="text"
    :class="hotkeyInput"
    :value="draft"
    :maxlength="maxlength"
    :placeholder="placeholder"
    spellcheck="false"
    autocomplete="off"
    @focus="onFocus"
    @input="onInput"
    @change="commit"
  >
</template>
