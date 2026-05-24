<script setup lang="ts">
import { useHudApp } from './HudApp'

const {
  connected,
  live,
  mode,
  gearLabel,
  speed,
  rpm,
  rpmPct,
  tcuState,
  hint,
  modeColor,
  rpmBarColor,
  gearStyle,
  clickThrough,
  close,
  toggleClickThrough,
  syncClickThroughMouse,
  onMouseLeave,
} = useHudApp()
</script>

<template>
  <div
    class="hud-root"
    :class="{ disconnected: !connected, 'click-through': clickThrough }"
    @mousemove="syncClickThroughMouse"
    @mouseleave="onMouseLeave"
  >
    <div class="row top">
      <div class="mode-pill" :style="{ color: modeColor, borderColor: modeColor }">
        {{ mode }}
      </div>
      <div class="state-pill" :class="{ shifting: tcuState === 'SHIFTING' }">
        {{ tcuState }}
      </div>
      <div class="actions interactive">
        <button
          class="btn"
          :class="{ active: clickThrough }"
          title="Toggle click-through"
          @click="toggleClickThrough($event)"
        >
          ⇅
        </button>
        <button class="btn" title="Close HUD" @click="close">×</button>
      </div>
    </div>

    <div class="row main">
      <div class="gear" :style="gearStyle">{{ gearLabel }}</div>
      <div class="metrics">
        <div class="rpm">
          <span class="rpm-num">{{ rpm }}</span>
          <span class="rpm-unit">RPM</span>
        </div>
        <div class="rpm-bar">
          <div class="rpm-fill" :style="{ width: `${rpmPct * 100}%`, background: rpmBarColor }" />
        </div>
        <div class="speed">
          <span class="speed-num">{{ speed }}</span>
          <span class="speed-unit">km/h</span>
        </div>
      </div>
    </div>

    <div v-if="hint" class="hint">{{ hint }}</div>
    <div v-else-if="!connected" class="hint warn">backend offline</div>
    <div v-else-if="!live" class="hint dim">awaiting telemetry…</div>
  </div>
</template>

<style scoped>
.hud-root {
  position: relative;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-variant-numeric: tabular-nums;
  -webkit-font-smoothing: antialiased;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  -webkit-app-region: drag;
  transition: background 180ms, border-color 180ms, box-shadow 180ms;
}
.hud-root.disconnected {
  border-color: rgba(220, 38, 38, 0.45);
}

.hud-root.click-through {
  background: transparent;
  border-color: transparent;
  box-shadow: none;
  -webkit-app-region: no-drag;
  --ct-outline:
    -1px -1px 0 rgba(0, 0, 0, 0.95),
    1px -1px 0 rgba(0, 0, 0, 0.95),
    -1px 1px 0 rgba(0, 0, 0, 0.95),
    1px 1px 0 rgba(0, 0, 0, 0.95),
    0 0 6px rgba(0, 0, 0, 0.85);
  --ct-outline-soft:
    var(--ct-outline),
    0 0 2px rgba(255, 255, 255, 0.55);
}

.hud-root.click-through .mode-pill,
.hud-root.click-through .state-pill,
.hud-root.click-through .rpm-num,
.hud-root.click-through .rpm-unit,
.hud-root.click-through .speed-num,
.hud-root.click-through .speed-unit,
.hud-root.click-through .hint {
  text-shadow: var(--ct-outline-soft);
}

.hud-root.click-through .state-pill,
.hud-root.click-through .rpm-num,
.hud-root.click-through .speed-num {
  color: #ffffff;
}

.hud-root.click-through .rpm-unit,
.hud-root.click-through .speed-unit,
.hud-root.click-through .row.top {
  color: #e4e4e7;
}

.hud-root.click-through .mode-pill {
  background: transparent;
  border-color: transparent;
  filter: drop-shadow(0 0 1px rgba(0, 0, 0, 1)) drop-shadow(0 1px 3px rgba(0, 0, 0, 0.8));
}

.hud-root.click-through .state-pill {
  background: transparent;
}

.hud-root.click-through .state-pill.shifting {
  color: #ddd6fe;
}

.hud-root.click-through .gear {
  -webkit-text-stroke: 2.5px rgba(0, 0, 0, 0.92);
  paint-order: stroke fill;
  text-shadow:
    0 0 8px rgba(0, 0, 0, 0.9),
    0 2px 10px rgba(0, 0, 0, 0.65);
}

.hud-root.click-through .rpm-bar {
  background: transparent;
  filter: drop-shadow(0 0 2px rgba(0, 0, 0, 0.95)) drop-shadow(0 1px 3px rgba(0, 0, 0, 0.7));
}

.hud-root.click-through .rpm-fill {
  box-shadow:
    0 0 4px rgba(0, 0, 0, 0.9),
    0 0 8px currentColor;
}

.btn {
  -webkit-app-region: no-drag;
  background: #f4f4f5;
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #27272a;
  border-radius: 6px;
  width: 24px;
  height: 24px;
  font-size: 12px;
  line-height: 1;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background 120ms, border-color 120ms, color 120ms, box-shadow 120ms;
}
.btn:hover {
  background: #e4e4e7;
  border-color: rgba(0, 0, 0, 0.16);
}
.btn.active {
  background: #18181b;
  border-color: #18181b;
  color: #fafafa;
}

.hud-root.click-through .btn {
  background: rgba(0, 0, 0, 0.45);
  border-color: rgba(255, 255, 255, 0.35);
  color: #ffffff;
  box-shadow:
    0 0 0 1px rgba(0, 0, 0, 0.6),
    0 2px 8px rgba(0, 0, 0, 0.55);
  text-shadow: var(--ct-outline);
  backdrop-filter: blur(4px);
}
.hud-root.click-through .btn:hover {
  background: rgba(0, 0, 0, 0.6);
  border-color: rgba(255, 255, 255, 0.5);
}
.hud-root.click-through .btn.active {
  background: rgba(255, 255, 255, 0.22);
  border-color: rgba(255, 255, 255, 0.65);
  color: #ffffff;
  box-shadow:
    0 0 0 1px rgba(0, 0, 0, 0.7),
    0 0 10px rgba(255, 255, 255, 0.25),
    0 2px 8px rgba(0, 0, 0, 0.6);
}

.row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.row.top {
  font-size: 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #71717a;
}
.mode-pill {
  border: 1px solid currentColor;
  border-radius: 999px;
  padding: 2px 8px;
  font-weight: 700;
  font-size: 10px;
  background: rgba(255, 255, 255, 0.6);
}
.state-pill {
  background: #f4f4f5;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 10px;
  color: #52525b;
}
.state-pill.shifting {
  background: rgba(124, 58, 237, 0.12);
  color: #6d28d9;
}
.actions {
  margin-left: auto;
  display: flex;
  gap: 4px;
}

.row.main {
  flex: 1;
  align-items: center;
  gap: 12px;
}
.gear {
  font-size: 64px;
  font-weight: 900;
  line-height: 1;
  letter-spacing: -0.04em;
  min-width: 60px;
  text-align: center;
}
.metrics {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.rpm {
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.rpm-num {
  font-size: 20px;
  font-weight: 700;
  color: #18181b;
}
.rpm-unit {
  font-size: 9px;
  color: #a1a1aa;
  letter-spacing: 0.1em;
}
.rpm-bar {
  height: 4px;
  background: #e4e4e7;
  border-radius: 2px;
  overflow: hidden;
}
.rpm-fill {
  height: 100%;
  transition: width 75ms linear, background 150ms linear, box-shadow 150ms linear;
}
.speed {
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.speed-num {
  font-size: 16px;
  font-weight: 700;
  color: #18181b;
}
.speed-unit {
  font-size: 9px;
  color: #a1a1aa;
  letter-spacing: 0.1em;
}

.hint {
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #0891b2;
  text-align: center;
}
.hint.dim { color: #a1a1aa; }
.hint.warn { color: #dc2626; }
.hud-root.click-through .hint.dim { color: #d4d4d8; }
.hud-root.click-through .hint.warn { color: #fca5a5; }
</style>
