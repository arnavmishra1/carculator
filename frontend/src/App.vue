<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch, watchEffect } from 'vue'
import { api } from './api.js'
import {
  DIVIDE,
  MINUS,
  PLUS,
  TIMES,
  createCalculator,
} from './calculator.js'

const MAX_FONT_SIZE = 44
const MIN_FONT_SIZE = 16
const FONT_SIZE_STEP = 2
const DISPLAY_PADDING = 12
const CAPTION_LIMIT = 40
const HISTORY_TEXT_LIMIT = 24
const HISTORY_OPEN_KEY = 'calculator.historyOpen'

const calculator = createCalculator(api)
const { state } = calculator

const digit = (label) => ({
  label,
  style: 'digit',
  press: () => calculator.pressDigit(label),
})
const operator = (label) => ({
  label,
  style: 'operator',
  press: () => calculator.pressOperator(label),
})
const fn = (label, press, name = label) => ({
  label,
  name,
  style: 'function',
  press,
})

const keys = [
  fn('C', calculator.clear, 'Clear'),
  fn('⌫', calculator.backspace, 'Backspace'),
  fn('(', calculator.openParenthesis),
  fn(')', calculator.closeParenthesis),
  digit('7'),
  digit('8'),
  digit('9'),
  operator(DIVIDE),
  digit('4'),
  digit('5'),
  digit('6'),
  operator(TIMES),
  digit('1'),
  digit('2'),
  digit('3'),
  operator(MINUS),
  fn('±', calculator.toggleSign, 'Toggle sign'),
  digit('0'),
  { label: '.', style: 'digit', press: calculator.decimalPoint },
  operator(PLUS),
  fn('%', calculator.percent),
  { label: '=', style: 'equals', press: calculator.equals },
]

function readHistoryOpen() {
  try {
    return localStorage.getItem(HISTORY_OPEN_KEY) === 'true'
  } catch {
    return false
  }
}

const historyOpen = ref(readHistoryOpen())
const toggleHistory = () => {
  historyOpen.value = !historyOpen.value
}
watch(historyOpen, (open) => {
  try {
    localStorage.setItem(HISTORY_OPEN_KEY, String(open))
  } catch {
    // The panel still works; it just won't remember its state.
  }
})

const characterKeys = {
  h: toggleHistory,
  H: toggleHistory,
  '+': () => calculator.pressOperator(PLUS),
  '-': () => calculator.pressOperator(MINUS),
  '*': () => calculator.pressOperator(TIMES),
  x: () => calculator.pressOperator(TIMES),
  X: () => calculator.pressOperator(TIMES),
  '/': () => calculator.pressOperator(DIVIDE),
  '=': calculator.equals,
  Enter: calculator.equals,
  Escape: calculator.clear,
  Backspace: calculator.backspace,
  '.': calculator.decimalPoint,
  '(': calculator.openParenthesis,
  ')': calculator.closeParenthesis,
  '%': calculator.percent,
}

function onKeydown(event) {
  if (event.metaKey || event.ctrlKey) return
  // Enter on a button reached with Tab should press that button.
  if (event.key === 'Enter' && event.target.closest?.('button')) return

  const action = /^[0-9]$/.test(event.key)
    ? () => calculator.pressDigit(event.key)
    : characterKeys[event.key]
  if (action) {
    event.preventDefault()
    action()
  }
}

const tail = (text, limit) =>
  text.length <= limit ? text : `…${text.slice(-(limit - 1))}`

const caption = computed(() => tail(state.caption, CAPTION_LIMIT))

// Display fitting: shrink the font, then show the end of the text.
const displayElement = ref(null)
const displayWidth = ref(0)
const displayFontSize = ref(MAX_FONT_SIZE)
const displayText = ref('0')
const measureContext = document.createElement('canvas').getContext('2d')

function fitDisplay() {
  const text = state.error || state.expression || '0'
  const available = displayWidth.value - DISPLAY_PADDING
  const family = displayElement.value
    ? getComputedStyle(displayElement.value).fontFamily
    : 'sans-serif'
  const measure = (value, size) => {
    measureContext.font = `700 ${size}px ${family}`
    return measureContext.measureText(value).width
  }

  let size = MAX_FONT_SIZE
  while (size > MIN_FONT_SIZE && measure(text, size) > available) {
    size -= FONT_SIZE_STEP
  }
  let fitted = text
  while (fitted.length > 1 && measure(fitted, size) > available) {
    fitted = `…${fitted.slice(2)}`
  }
  displayFontSize.value = size
  displayText.value = fitted
}

watchEffect(fitDisplay)

const resizeObserver = new ResizeObserver(([entry]) => {
  displayWidth.value = entry.contentRect.width
})

const dark = ref(true)
watch(
  dark,
  (isDark) => {
    document.documentElement.dataset.theme = isDark ? 'dark' : 'light'
  },
  { immediate: true },
)

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  resizeObserver.observe(displayElement.value)
  calculator.loadHistory()
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  resizeObserver.disconnect()
})
</script>

<template>
  <main class="app" :class="{ 'history-open': historyOpen }">
    <section class="calculator" aria-label="Calculator">
      <div class="toolbar">
        <button
          type="button"
          class="toolbar-button"
          aria-controls="history-panel"
          :aria-expanded="historyOpen"
          title="Show or hide history (H)"
          @mousedown.prevent
          @click="toggleHistory"
        >
          <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
            <circle cx="12" cy="12" r="9" />
            <path d="M12 7v5l3 2" />
          </svg>
          History
        </button>

        <label class="theme-switch">
          <input v-model="dark" type="checkbox" role="switch" />
          <span class="track" aria-hidden="true"></span>
          Dark theme
        </label>
      </div>

      <div class="caption">{{ caption }}</div>
      <output
        ref="displayElement"
        class="display"
        :class="{ error: state.error }"
        :style="{ fontSize: `${displayFontSize}px` }"
        >{{ displayText }}</output
      >

      <p class="fact" :class="{ visible: state.fact }" aria-live="polite">
        <span v-if="state.fact" class="fact-icon" aria-hidden="true">🚗</span>
        <span>{{ state.fact }}</span>
      </p>

      <div class="keypad" @mousedown.prevent>
        <button
          v-for="key in keys"
          :key="key.label"
          type="button"
          class="key"
          :class="key.style"
          :aria-label="key.name"
          @click="key.press()"
        >
          {{ key.label }}
        </button>
      </div>
    </section>

    <aside
      v-show="historyOpen"
      id="history-panel"
      class="panel"
      aria-label="History"
    >
      <header class="panel-header">
        <h1>History</h1>
        <button
          type="button"
          class="panel-button"
          @mousedown.prevent
          @click="calculator.clearHistory()"
        >
          Clear
        </button>
        <button
          type="button"
          class="panel-button close-history"
          aria-label="Close history"
          @mousedown.prevent
          @click="historyOpen = false"
        >
          ✕
        </button>
      </header>

      <div class="history-list" @mousedown.prevent>
        <p v-if="!state.history.length" class="empty">No calculations yet</p>
        <button
          v-for="(entry, index) in state.history"
          :key="`${state.history.length - index}`"
          type="button"
          class="history-entry"
          @click="calculator.reuseEntry(entry)"
        >
          <span>{{ tail(entry.expression, HISTORY_TEXT_LIMIT) }}</span>
          <span>= {{ tail(entry.result, HISTORY_TEXT_LIMIT) }}</span>
        </button>
      </div>
    </aside>
  </main>
</template>
