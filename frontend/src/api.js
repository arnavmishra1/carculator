// The calculator's data operations, all run in the browser.

import { CalculationError, calculate } from './engine.js'
import { findFact } from './facts.js'
import { createHistory } from './history.js'

export function createApi(history = createHistory()) {
  return {
    async calculate(expression) {
      let result
      try {
        result = calculate(expression)
      } catch (error) {
        throw error instanceof CalculationError
          ? error
          : new CalculationError('Invalid expression')
      }
      history.add(expression, result)
      return { result, fact: findFact(result), history: history.entries() }
    },
    async loadHistory() {
      return { history: history.entries() }
    },
    async clearHistory() {
      history.clear()
      return { history: [] }
    },
  }
}

export const api = createApi()
