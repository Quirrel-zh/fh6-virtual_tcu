<script setup lang="ts">
  import { VIGEMBUS_DRIVER_URL } from '@virtual-tcu/shared/config/links'
  import {
    NAlert,
    NButton,
    NCard,
    NFlex,
    NGrid,
    NGridItem,
    NInput,
    NSelect,
    NSlider,
    NText,
  } from 'naive-ui'
  import { computed, inject, ref } from 'vue'
  import { settingsContextKey } from './context'

  const ctx = inject(settingsContextKey)!
  const {
    t,
    store,
    hotkeyFields,
    shiftKeyFields,
    outputModeOptions,
    gamepadButtonFields,
    gamepadButtonOptions,
    advancedSliders,
    networkDraftHost,
    networkDraftWebPort,
    networkDraftUdpPort,
    networkDirty,
    networkApplyError,
    networkApplyOk,
    networkApplying,
    applyNetworkSettings,
    onExportProfile,
    onOpenImport,
    restartBackend,
    configNumber,
    configText,
    sliderUnit,
  } = ctx

  const gamepadCheckError = ref('')
  const gamepadChecking = ref(false)

  function onInstallDriver() {
    store.installViGEmBus()
  }

  function applyAndRestart() {
    applyNetworkSettings()
    restartBackend()
  }

  const outputModeValue = computed(() => {
    const v = (store.config as Record<string, unknown>).output_mode
    return typeof v === 'string' && (v === 'keyboard' || v === 'gamepad') ? v : 'keyboard'
  })

  const outputModeOptionsComputed = computed(() =>
    outputModeOptions.map((o) => ({
      label: t(`extras.${o.i18nKey}`),
      value: o.value,
    })),
  )

  const vigembusUrl = VIGEMBUS_DRIVER_URL

  async function onOutputModeChange(v: string) {
    if (v === 'gamepad') {
      // Backend is already driving shifts via a virtual gamepad — no probe needed.
      if (store.effectiveOutputMode === 'gamepad') {
        gamepadCheckError.value = ''
        store.setConfig('output_mode', v)
        return
      }

      gamepadCheckError.value = ''
      gamepadChecking.value = true
      try {
        const result = await store.checkGamepad()
        if (!result.ok) {
          gamepadCheckError.value =
            result.error === 'timeout'
              ? t('extras.gamepadCheckTimeout')
              : t('extras.gamepadCheckFailed')
          return
        }
      } catch {
        gamepadCheckError.value = t('extras.gamepadCheckTimeout')
        return
      } finally {
        gamepadChecking.value = false
      }
    }
    // Driver OK or switching to keyboard — save config
    gamepadCheckError.value = ''
    store.setConfig('output_mode', v)
  }
</script>

<template>
  <NFlex vertical :size="16">
    <NCard :title="t('extras.networkTitle')" size="small" :bordered="false">
      <NText depth="3" style="font-size: 12px; display: block; margin-bottom: 8px">
        {{ t('extras.networkHint') }}
      </NText>
      <NGrid :cols="2" :x-gap="16" :y-gap="10">
        <NGridItem>
          <NFlex justify="space-between" align="center" :size="8">
            <NText>{{ t('extras.webHost') }}</NText>
            <NInput
              v-model:value="networkDraftHost"
              placeholder="0.0.0.0"
              maxlength="15"
              size="small"
              style="width: 120px; font-family: ui-monospace, monospace"
            />
          </NFlex>
        </NGridItem>
        <NGridItem>
          <NFlex justify="space-between" align="center" :size="8">
            <NText>{{ t('extras.webPort') }}</NText>
            <NInput
              v-model:value="networkDraftWebPort"
              placeholder="8765"
              maxlength="5"
              size="small"
              style="width: 120px; font-family: ui-monospace, monospace"
            />
          </NFlex>
        </NGridItem>
        <NGridItem>
          <NFlex justify="space-between" align="center" :size="8">
            <NText>{{ t('extras.udpPort') }}</NText>
            <NInput
              v-model:value="networkDraftUdpPort"
              placeholder="5555"
              maxlength="5"
              size="small"
              style="width: 120px; font-family: ui-monospace, monospace"
            />
          </NFlex>
        </NGridItem>
      </NGrid>
      <NText depth="3" style="font-size: 11px; display: block; margin-top: 8px">
        {{ t('extras.udpPortHint') }}
      </NText>
      <NFlex :size="8" align="center" style="margin-top: 12px">
        <NButton
          type="primary"
          size="small"
          :disabled="!networkDirty || networkApplying"
          :loading="networkApplying"
          @click="applyNetworkSettings"
        >
          {{ t('extras.networkApply') }}
        </NButton>
        <NText v-if="networkApplyOk" depth="3" style="font-size: 12px; color: #16a34a">
          {{ t('extras.networkApplyOk') }}
        </NText>
        <NText v-else-if="networkApplyError" depth="3" style="font-size: 12px; color: #dc2626">
          {{ t(`extras.networkErrors.${networkApplyError}`) }}
        </NText>
        <NButton
          v-if="networkDirty"
          type="warning"
          size="small"
          style="margin-left: 8px"
          @click="applyAndRestart()"
        >
          {{ t('extras.saveAndRestart') }}
        </NButton>
      </NFlex>
    </NCard>

    <NCard :title="t('extras.profileTitle')" size="small" :bordered="false">
      <NText depth="3" style="font-size: 12px; display: block; margin-bottom: 12px">
        {{ t('extras.profileHint') }}
      </NText>
      <NFlex :size="8">
        <NButton @click="onExportProfile">
          {{ t('extras.export') }}
        </NButton>
        <NButton @click="onOpenImport">
          {{ t('extras.import') }}
        </NButton>
      </NFlex>
    </NCard>

    <NCard :title="t('extras.outputMode')" size="small" :bordered="false">
      <NText depth="3" style="font-size: 12px; display: block; margin-bottom: 8px">
        {{ t('extras.outputModeHint') }}
      </NText>
      <NSelect
        :value="outputModeValue"
        :options="outputModeOptionsComputed"
        :loading="gamepadChecking"
        size="small"
        style="width: 200px"
        @update:value="onOutputModeChange"
      />
      <NAlert
        v-if="gamepadCheckError"
        type="error"
        :title="gamepadCheckError"
        style="margin-top: 10px"
      >
        <template #default>
          <NFlex vertical :size="8">
            <NText depth="3" style="font-size: 12px">
              {{ t('extras.gamepadCheckFailedHint', { url: vigembusUrl }) }}
            </NText>
            <NButton type="primary" size="small" @click="onInstallDriver">
              {{ t('extras.installDriver') }}
            </NButton>
          </NFlex>
        </template>
      </NAlert>
      <template v-if="outputModeValue === 'gamepad'">
        <NText depth="3" style="font-size: 12px; display: block; margin: 12px 0 8px">
          {{ t('extras.gamepadButtonHint') }}
        </NText>
        <NGrid :cols="2" :x-gap="16" :y-gap="10">
          <NGridItem v-for="g1 in gamepadButtonFields" :key="g1.key">
            <NFlex justify="space-between" align="center" :size="8">
              <NText>{{ t(`extras.${g1.i18nKey}`) }}</NText>
              <NSelect
                :value="configText(g1.key) || g1.placeholder"
                :options="gamepadButtonOptions.map((o) => ({ label: o.label, value: o.value }))"
                size="small"
                style="width: 140px"
                @update:value="(v: string) => store.setConfig(g1.key, v)"
              />
            </NFlex>
          </NGridItem>
        </NGrid>
      </template>
      <NFlex :size="8" align="center" style="margin-top: 10px">
        <NButton type="warning" size="small" @click="restartBackend()">
          {{ t('extras.saveAndRestart') }}
        </NButton>
        <NText depth="3" style="font-size: 11px; color: #d97706">
          {{ t('extras.outputModeRestart') }}
        </NText>
      </NFlex>
    </NCard>

    <NCard :title="t('extras.shiftKeys')" size="small" :bordered="false">
      <NText depth="3" style="font-size: 12px; display: block; margin-bottom: 8px">
        {{ t('extras.shiftKeyHint') }}
      </NText>
      <NGrid :cols="2" :x-gap="16" :y-gap="10">
        <NGridItem v-for="h1 in shiftKeyFields" :key="h1.key">
          <NFlex justify="space-between" align="center" :size="8">
            <NText>{{ t(`extras.${h1.i18nKey}`) }}</NText>
            <NInput
              :value="configText(h1.key)"
              :placeholder="h1.placeholder"
              size="small"
              style="width: 100px; font-family: ui-monospace, monospace"
              @update:value="(v) => store.setConfig(h1.key, v.trim().toLowerCase())"
            />
          </NFlex>
        </NGridItem>
      </NGrid>
    </NCard>

    <NCard :title="t('extras.hotkeys')" size="small" :bordered="false">
      <NText depth="3" style="font-size: 12px; display: block; margin-bottom: 8px">
        {{ t('extras.hotkeyHint') }}
      </NText>
      <NGrid :cols="2" :x-gap="16" :y-gap="10">
        <NGridItem v-for="h1 in hotkeyFields" :key="h1.key">
          <NFlex justify="space-between" align="center" :size="8">
            <NText>{{ t(`extras.${h1.i18nKey}`) }}</NText>
            <NInput
              :value="configText(h1.key)"
              :placeholder="h1.placeholder"
              size="small"
              style="width: 100px; font-family: ui-monospace, monospace"
              @update:value="(v) => store.setConfig(h1.key, v.trim().toLowerCase())"
            />
          </NFlex>
        </NGridItem>
      </NGrid>
    </NCard>

    <NCard :title="t('extras.fullTuning')" size="small" :bordered="false">
      <NFlex vertical :size="14">
        <div v-for="s in advancedSliders" :key="s.key">
          <NFlex justify="space-between" align="center" style="margin-bottom: 4px">
            <NText>{{ t(`settings.${s.i18nKey}`) }}</NText>
            <NText code style="font-family: ui-monospace, monospace">
              {{ configNumber(s.key) }}{{ sliderUnit(s) }}
            </NText>
          </NFlex>
          <NSlider
            :value="configNumber(s.key)"
            :min="s.min"
            :max="s.max"
            :step="s.step ?? 1"
            @update:value="(v) => store.setConfig(s.key, v)"
          />
        </div>
      </NFlex>
    </NCard>
  </NFlex>
</template>
