import { describe, expect, it, vi } from 'vitest'
import { DIVIDE, MINUS, PLUS, TIMES, createCalculator } from './calculator.js'

function setup(api = {}) {
  return createCalculator({
    calculate: vi.fn(async (expression) => ({
      result: '5',
      fact: 'A car fact',
      history: [{ expression, result: '5' }],
    })),
    loadHistory: vi.fn(async () => ({ history: [] })),
    clearHistory: vi.fn(async () => ({ history: [] })),
    ...api,
  })
}

function type(calculator, ...keys) {
  const special = {
    '.': 'decimalPoint',
    '(': 'openParenthesis',
    ')': 'closeParenthesis',
    '%': 'percent',
    '±': 'toggleSign',
    '⌫': 'backspace',
    '=': 'equals',
  }
  let finished
  for (const key of keys) {
    if (/\d/.test(key)) finished = calculator.pressDigit(key)
    else if (special[key]) finished = calculator[special[key]]()
    else finished = calculator.pressOperator(key)
  }
  return finished
}

async function expressionAfter(...keys) {
  const calculator = setup()
  await type(calculator, ...keys)
  return calculator.state.expression
}

describe('editing', () => {
  it.each([
    [['1', PLUS, TIMES, '2'], `1${TIMES}2`],
    [[PLUS], ''],
    [[MINUS, '5'], `${MINUS}5`],
    [['2', TIMES, MINUS, '3'], `2${TIMES}${MINUS}3`],
    [['2', MINUS, MINUS], `2${MINUS}`],
    [['(', PLUS], '('],
    [['(', MINUS, '1'], `(${MINUS}1`],
    [['.', '5'], '0.5'],
    [['1', '.', '.', '2', '.'], '1.2'],
    [['(', '1', ')', '.'], `(1)${TIMES}0.`],
    [['(', '1', ')', '2'], `(1)${TIMES}2`],
    [['2', '('], `2${TIMES}(`],
    [['5', '%', '('], `5%${TIMES}(`],
    [[')'], ''],
    [['(', ')'], '('],
    [['(', '1', PLUS, ')'], `(1${PLUS}`],
    [['(', '1', ')', ')'], '(1)'],
    [['%'], ''],
    [['5', '%', '%'], '5%%'],
    [['1', PLUS, '%'], `1${PLUS}`],
    [['±'], MINUS],
    [['5', '±'], `${MINUS}5`],
    [['5', '±', '±'], '5'],
    [['1', MINUS, '5', '±'], `1${MINUS}${MINUS}5`],
    [['1', TIMES, MINUS, '5', '±'], `1${TIMES}5`],
    [['(', MINUS, '5', '±'], '(5'],
    [['1', '2', '⌫'], '1'],
    [['⌫'], ''],
  ])('%j gives %s', async (keys, expected) => {
    expect(await expressionAfter(...keys)).toBe(expected)
  })
})

describe('equals', () => {
  it('shows the result, caption and history', async () => {
    const calculator = setup()
    await type(calculator, '2', PLUS, '3', '=')
    expect(calculator.state).toMatchObject({
      expression: '5',
      caption: `2${PLUS}3 =`,
      error: '',
      fact: 'A car fact',
      showingResult: true,
      history: [{ expression: `2${PLUS}3`, result: '5' }],
    })
  })

  it('shows negative results with the display minus', async () => {
    const calculator = setup({
      calculate: async () => ({ result: '-3', history: [] }),
    })
    calculator.pressDigit('1')
    await calculator.equals()
    expect(calculator.state.expression).toBe(`${MINUS}3`)
  })

  it('applies keys typed right after equals to the result', async () => {
    const calculator = setup()
    calculator.pressDigit('2')
    calculator.equals()
    calculator.pressOperator(PLUS)
    await calculator.pressDigit('1')
    expect(calculator.state.expression).toBe(`5${PLUS}1`)
    expect(calculator.state.showingResult).toBe(false)
  })

  it('starts a new number when a digit follows a result', async () => {
    const calculator = setup()
    calculator.pressDigit('2')
    calculator.equals()
    await calculator.pressDigit('7')
    expect(calculator.state.expression).toBe('7')
  })

  it('clears a result on backspace', async () => {
    const calculator = setup()
    calculator.pressDigit('2')
    calculator.equals()
    await calculator.backspace()
    expect(calculator.state.expression).toBe('')
    expect(calculator.state.caption).toBe('')
  })

  it('does nothing on empty input or a shown result', async () => {
    const calculate = vi.fn(async () => ({ result: '5', history: [] }))
    const calculator = setup({ calculate })
    await calculator.equals()
    expect(calculate).not.toHaveBeenCalled()
    calculator.pressDigit('2')
    calculator.equals()
    await calculator.equals()
    expect(calculate).toHaveBeenCalledTimes(1)
  })

  it('keeps the expression and shows the error on failure', async () => {
    const calculator = setup({
      calculate: async () => {
        throw new Error("Can't divide by zero")
      },
    })
    calculator.pressDigit('1')
    calculator.pressOperator(DIVIDE)
    calculator.pressDigit('0')
    await calculator.equals()
    expect(calculator.state).toMatchObject({
      expression: `1${DIVIDE}0`,
      caption: `1${DIVIDE}0`,
      error: "Can't divide by zero",
      showingResult: false,
    })
    await calculator.pressDigit('2')
    expect(calculator.state.error).toBe('')
  })
})

describe('fact', () => {
  async function withFact() {
    const calculator = setup()
    calculator.pressDigit('2')
    await calculator.equals()
    expect(calculator.state.fact).toBe('A car fact')
    return calculator
  }

  it.each([
    ['a digit', (calculator) => calculator.pressDigit('1')],
    ['an operator', (calculator) => calculator.pressOperator(PLUS)],
    ['percent', (calculator) => calculator.percent()],
    ['clear', (calculator) => calculator.clear()],
    ['backspace', (calculator) => calculator.backspace()],
    [
      'reusing history',
      (calculator) => calculator.reuseEntry({ expression: '1', result: '1' }),
    ],
  ])('is cleared by %s', async (_name, act) => {
    const calculator = await withFact()
    await act(calculator)
    expect(calculator.state.fact).toBe('')
  })

  it('is empty when no fact matches', async () => {
    const calculator = setup({
      calculate: async () => ({ result: '0.3', fact: null, history: [] }),
    })
    calculator.pressDigit('1')
    await calculator.equals()
    expect(calculator.state.fact).toBe('')
  })

  it('is not shown with an error', async () => {
    const calculator = setup({
      calculate: async () => {
        throw new Error('Invalid expression')
      },
    })
    calculator.pressDigit('1')
    await calculator.equals()
    expect(calculator.state.fact).toBe('')
  })
})

describe('history', () => {
  it('reuses an entry for editing', async () => {
    const calculator = setup()
    calculator.pressDigit('2')
    calculator.equals()
    await calculator.reuseEntry({ expression: `1${PLUS}1`, result: '2' })
    expect(calculator.state).toMatchObject({
      expression: `1${PLUS}1`,
      caption: '',
      showingResult: false,
    })
  })

  it('keeps entries when clearing fails', async () => {
    const calculator = setup({
      clearHistory: async () => {
        throw new Error("Storage failed")
      },
    })
    calculator.pressDigit('2')
    calculator.equals()
    await calculator.clearHistory()
    expect(calculator.state.history).toHaveLength(1)
    expect(calculator.state.error).toBe("Storage failed")
  })
})
