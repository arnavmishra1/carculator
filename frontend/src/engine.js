// Safe expression evaluation using exact decimal arithmetic. No UI code here.

import DecimalBase from 'decimal.js'

const WORKING_PRECISION = 34
const DISPLAY_PRECISION = 16
const MAX_PLAIN_EXPONENT = 16
const MIN_PLAIN_EXPONENT = -9
const MAX_EXPONENT = 999999
const MAX_NESTING = 200

const Decimal = DecimalBase.clone({
  precision: WORKING_PRECISION,
  rounding: DecimalBase.ROUND_HALF_EVEN,
  maxE: MAX_EXPONENT,
  minE: -MAX_EXPONENT,
})

const TOKEN = /\s*(?:((?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)|([-+*/()%]))/y

/** An expression could not be evaluated. The message is shown to the user. */
export class CalculationError extends Error {}

/** Evaluate an arithmetic expression and return its value as a Decimal. */
export function evaluate(expression) {
  const source = expression
    .replaceAll('×', '*')
    .replaceAll('÷', '/')
    .replaceAll('−', '-')
    .trim()
  if (!source) throw new CalculationError('Enter an expression')

  // The whole expression is parsed before any of it runs, so a typo is
  // reported as invalid even if an earlier part would divide by zero.
  return run(new Parser(tokenize(source)).parse())
}

/** Round a Decimal for display, using scientific notation at extremes. */
export function formatResult(value) {
  const rounded = value.toSignificantDigits(DISPLAY_PRECISION)
  if (!rounded.isFinite()) throw new CalculationError('Number too large')

  if (rounded.isZero()) return '0'
  if (MIN_PLAIN_EXPONENT <= rounded.e && rounded.e < MAX_PLAIN_EXPONENT) {
    return rounded.toFixed()
  }
  return rounded.toExponential().replace('e', 'E')
}

/** Evaluate an expression and return the formatted result. */
export const calculate = (expression) => formatResult(evaluate(expression))

function tokenize(source) {
  const tokens = []
  TOKEN.lastIndex = 0
  while (TOKEN.lastIndex < source.length) {
    const match = TOKEN.exec(source)
    if (!match) throw invalid()
    tokens.push(match[1] ? { number: match[1] } : { symbol: match[2] })
  }
  return tokens
}

const invalid = () => new CalculationError('Invalid expression')

function finite(value) {
  if (!value.isFinite()) throw new CalculationError('Number too large')
  return value
}

const BINARY = {
  '+': (left, right) => left.plus(right),
  '-': (left, right) => left.minus(right),
  '*': (left, right) => left.times(right),
  '/': (left, right) => {
    if (right.isZero()) throw new CalculationError("Can't divide by zero")
    return left.dividedBy(right)
  },
}

/** Run the parser's steps, in postfix order, on a stack of values. */
function run(steps) {
  const stack = []
  for (const step of steps) {
    if (step.number !== undefined) {
      stack.push(finite(new Decimal(step.number)))
    } else if (step.binary) {
      const right = stack.pop()
      stack.push(finite(BINARY[step.binary](stack.pop(), right)))
    } else if (step.negate) {
      stack.push(stack.pop().negated().toSignificantDigits())
    } else {
      stack.push(stack.pop().dividedBy(100))
    }
  }
  return stack.pop()
}

// Grammar, loosest binding first:
//   sum     = product (("+" | "-") product)*
//   product = signed (("*" | "/") signed)*
//   signed  = ("+" | "-")* percent
//   percent = primary "%"*          (50% means 50/100)
//   primary = number | "(" sum ")"
//
// The parser checks the syntax and returns the steps to compute the value.
class Parser {
  constructor(tokens) {
    this.tokens = tokens
    this.position = 0
    this.depth = 0
    this.steps = []
  }

  parse() {
    this.sum()
    if (this.position < this.tokens.length) throw invalid()
    return this.steps
  }

  take(...symbols) {
    const symbol = this.tokens[this.position]?.symbol
    if (!symbols.includes(symbol)) return null
    this.position += 1
    return symbol
  }

  sum() {
    this.product()
    for (let symbol; (symbol = this.take('+', '-')); ) {
      this.product()
      this.steps.push({ binary: symbol })
    }
  }

  product() {
    this.signed()
    for (let symbol; (symbol = this.take('*', '/')); ) {
      this.signed()
      this.steps.push({ binary: symbol })
    }
  }

  signed() {
    let negative = false
    for (let symbol; (symbol = this.take('+', '-')); ) {
      if (symbol === '-') negative = !negative
    }
    this.percent()
    if (negative) this.steps.push({ negate: true })
  }

  percent() {
    this.primary()
    while (this.take('%')) this.steps.push({ percent: true })
  }

  primary() {
    const token = this.tokens[this.position]
    if (token?.number) {
      this.position += 1
      this.steps.push({ number: token.number })
      return
    }
    if (!this.take('(')) throw invalid()

    if (++this.depth > MAX_NESTING) {
      throw new CalculationError('Expression too complex')
    }
    this.sum()
    if (!this.take(')')) throw invalid()
    this.depth -= 1
  }
}
