import { describe, expect, it } from 'vitest'
import { calculate } from './engine.js'

describe('calculate', () => {
  it.each([
    ['2+3', '5'],
    ['10-4', '6'],
    ['6*7', '42'],
    ['9/3', '3'],
    ['2+3*4', '14'],
    ['(2+3)*4', '20'],
    ['((1+2)*(3+4))', '21'],
    ['-5+2', '-3'],
    ['--5', '5'],
    ['2*-3', '-6'],
    ['0.1+0.2', '0.3'],
    ['.5+.5', '1'],
    ['5.', '5'],
    ['007+1', '8'],
    ['1/3', '0.3333333333333333'],
    ['1/3*3', '1'],
    ['2/3', '0.6666666666666667'],
    ['1-1', '0'],
    ['-1+1', '0'],
    ['-0', '0'],
    ['6×7', '42'],
    ['8÷2', '4'],
    ['5−2', '3'],
    [' 1 + 1 ', '2'],
    ['10-2-3', '5'],
    ['16/4/2', '2'],
  ])('%s = %s', (expression, expected) => {
    expect(calculate(expression)).toBe(expected)
  })

  it.each([
    ['50%', '0.5'],
    ['10/50%', '20'],
    ['200*10%', '20'],
    ['(20+30)%', '0.5'],
    ['2*(1+1)%', '0.04'],
    ['50%%', '0.005'],
    ['-5%', '-0.05'],
  ])('percent: %s = %s', (expression, expected) => {
    expect(calculate(expression)).toBe(expected)
  })

  it.each([
    ['12345678901234567890*10', '1.234567890123457E+20'],
    ['1/1000000000000', '1E-12'],
    ['1E+20+1', '1E+20'],
    ['-1E+20', '-1E+20'],
    ['1000000', '1000000'],
    ['0.000001', '0.000001'],
    ['0.000000001', '0.000000001'],
    ['999999999999999.9', '999999999999999.9'],
  ])('large and small: %s = %s', (expression, expected) => {
    expect(calculate(expression)).toBe(expected)
  })

  it('keeps the precision of decimal literals', () => {
    expect(calculate('1234567890.123456+0')).toBe('1234567890.123456')
  })

  it.each(['1/0', '0/0', '1/(2-2)', '1/0%'])('%s divides by zero', (expression) => {
    expect(() => calculate(expression)).toThrow("Can't divide by zero")
  })

  it.each(['2+', '*2', '(1+2', '1+2)', '1.2.3', '%', '()', '2(3)', 'E', '1e', '5%3'])(
    '%s is invalid',
    (expression) => {
      expect(() => calculate(expression)).toThrow('Invalid expression')
    },
  )

  it.each([
    '2**3',
    '7//2',
    "__import__('os')",
    'alert(1)',
    'Math.abs(1)',
    '[1]',
    "'a'",
    '0x10',
    '1_000',
    'Infinity',
    'NaN',
  ])('%s is rejected', (expression) => {
    expect(() => calculate(expression)).toThrow('Invalid expression')
  })

  it('asks for an expression when empty', () => {
    expect(() => calculate('   ')).toThrow('Enter an expression')
  })

  it.each(['1E999999*10', '1E9999999'])('%s is too large', (expression) => {
    expect(() => calculate(expression)).toThrow('Number too large')
  })

  it('reports deep nesting', () => {
    expect(() => calculate('('.repeat(5000) + '1' + ')'.repeat(5000))).toThrow(
      'Expression too complex',
    )
  })

  it('handles long runs of signs', () => {
    expect(calculate('-'.repeat(10001) + '1')).toBe('-1')
  })
})
