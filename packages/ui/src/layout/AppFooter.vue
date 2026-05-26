<script setup lang="ts">
import { GITHUB_REPO_URL } from './app-footer'
</script>

<template>
  <footer
    class="border-tcu-border bg-tcu-bg-1 text-tcu-txt-dim border-t px-6 py-2 text-center font-mono text-[11px]"
  >
    {{ $t('footer.viewOnlyHint') }}
    <span class="mx-1.5">·</span>
    <a
      :href="GITHUB_REPO_URL"
      target="_blank"
      rel="noopener noreferrer"
      class="text-accent hover:underline"
    >
      {{ $t('footer.github') }}
    </a>
  </footer>
</template>
