import { reactive } from 'vue'

export const PLUS = '+'
export const MINUS = '−'
export const TIMES = '×'
export const DIVIDE = '÷'

const OPERATORS = [PLUS, MINUS, TIMES, DIVIDE]
const TRAILING_NUMBER = /(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$/
const TRAILING_OPERATORS = /[+−×÷]+$/

const isOperator = (character) => OPERATORS.includes(character)
const isDigit = (character) => /^\d$/.test(character)
const canTakePercent = (last) => isDigit(last) || [')', '.', '%'].includes(last)
const asDisplayText = (result) =>
  result.startsWith('-') ? MINUS + result.slice(1) : result

export function createCalculator(api) {
  const state = reactive({
    expression: '',
    caption: '',
    error: '',
    fact: '',
    showingResult: false,
    history: [],
  })

  function beginEdit({ replaceResult = false } = {}) {
    if (state.showingResult && replaceResult) state.expression = ''
    state.showingResult = false
    state.caption = ''
    state.error = ''
    state.fact = ''
  }

  function clear() {
    state.expression = ''
    state.caption = ''
    state.error = ''
    state.fact = ''
    state.showingResult = false
  }

  const actions = {
    clear,

    pressDigit(digit) {
      beginEdit({ replaceResult: true })
      if (state.expression.endsWith(')')) state.expression += TIMES
      state.expression += digit
    },

    decimalPoint() {
      beginEdit({ replaceResult: true })
      const number = state.expression.match(TRAILING_NUMBER)
      if (!number) {
        if (state.expression.endsWith(')')) state.expression += TIMES
        state.expression += '0.'
      } else if (!/[.eE]/.test(number[0])) {
        state.expression += '.'
      }
    },

    pressOperator(operator) {
      beginEdit()
      const last = state.expression.slice(-1)
      if (operator === MINUS && ['', '(', TIMES, DIVIDE].includes(last)) {
        state.expression += operator
        return
      }
      const base = state.expression.replace(TRAILING_OPERATORS, '')
      if (base && !base.endsWith('(')) state.expression = base + operator
    },

    openParenthesis() {
      beginEdit({ replaceResult: true })
      if (canTakePercent(state.expression.slice(-1))) state.expression += TIMES
      state.expression += '('
    },

    closeParenthesis() {
      beginEdit()
      const last = state.expression.slice(-1)
      const count = (character) => state.expression.split(character).length - 1
      const hasOpen = count('(') > count(')')
      if (hasOpen && last && !isOperator(last) && last !== '(') {
        state.expression += ')'
      }
    },

    percent() {
      beginEdit()
      if (canTakePercent(state.expression.slice(-1))) state.expression += '%'
    },

    toggleSign() {
      beginEdit()
      const number = state.expression.match(TRAILING_NUMBER)
      if (!number) {
        const last = state.expression.slice(-1)
        if (!last || isOperator(last) || last === '(') {
          state.expression += MINUS
        }
        return
      }
      const before = state.expression.slice(0, number.index)
      const beforeMinus = before.slice(-2, -1)
      const isUnaryMinus =
        before.endsWith(MINUS) &&
        (before.length === 1 || isOperator(beforeMinus) || beforeMinus === '(')
      state.expression = isUnaryMinus
        ? before.slice(0, -1) + number[0]
        : before + MINUS + number[0]
    },

    backspace() {
      if (state.showingResult) {
        clear()
        return
      }
      beginEdit()
      state.expression = state.expression.slice(0, -1)
    },

    async equals() {
      if (state.showingResult || !state.expression) return
      const expression = state.expression
      try {
        const { result, fact, history } = await api.calculate(expression)
        state.history = history
        state.caption = `${expression} =`
        state.expression = asDisplayText(result)
        state.error = ''
        state.fact = fact ?? ''
        state.showingResult = true
      } catch (error) {
        state.error = error.message
        state.fact = ''
        state.caption = expression
      }
    },

    reuseEntry(entry) {
      clear()
      state.expression = entry.expression
    },

    async loadHistory() {
      try {
        state.history = (await api.loadHistory()).history
      } catch (error) {
        state.error = error.message
      }
    },

    async clearHistory() {
      try {
        state.history = (await api.clearHistory()).history
      } catch (error) {
        state.error = error.message
      }
    },
  }

  // Actions run strictly in order, so keys typed right after "=" apply to the
  // result rather than racing the calculation.
  let queue = Promise.resolve()
  const queued = Object.fromEntries(
    Object.entries(actions).map(([name, action]) => [
      name,
      (...args) => (queue = queue.then(() => action(...args))),
    ]),
  )

  return { state, ...queued }
}
