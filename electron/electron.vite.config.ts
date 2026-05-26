import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig, externalizeDepsPlugin } from 'electron-vite'

const pkg = JSON.parse(readFileSync(resolve(__dirname, 'package.json'), 'utf-8'))
const versionDefine = { __APP_VERSION__: JSON.stringify(pkg.version) }

export default defineConfig({
  main: {
    plugins: [externalizeDepsPlugin()],
    build: {
      outDir: resolve(__dirname, 'out/main'),
      rollupOptions: {
        input: { index: resolve(__dirname, 'src/main/index.ts') },
      },
    },
  },
  preload: {
    plugins: [externalizeDepsPlugin()],
    build: {
      outDir: resolve(__dirname, 'out/preload'),
      rollupOptions: {
        input: {
          main: resolve(__dirname, 'src/preload/main.ts'),
          hud: resolve(__dirname, 'src/preload/hud.ts'),
        },
      },
    },
  },
  renderer: {
    root: resolve(__dirname, 'src'),
    define: versionDefine,
    build: {
      outDir: resolve(__dirname, 'out/renderer'),
      rollupOptions: {
        input: {
          index: resolve(__dirname, 'src/hud-renderer/index.html'),
          settings: resolve(__dirname, 'src/settings-renderer/index.html'),
        },
      },
    },
    plugins: [vue(), tailwindcss()],
  },
})
