import Decimal from 'decimal.js'
import { describe, expect, it } from 'vitest'
import entries from './car_facts.json'
import { findFact, loadFacts } from './facts.js'

const MAX_FACT_LENGTH = 110

const FACTS = loadFacts([
  { value: '181', fact: 'miata' },
  { value: '5.0', fact: 'five' },
  { value: '100', fact: 'hundred' },
  { value: '102', fact: 'hundred and two' },
  { value: '2002', fact: 'bmw' },
  { value: '15007033', fact: 'model t' },
])

const first = (options) => options[0]

describe('findFact', () => {
  it.each([
    ['181', 'miata'],
    ['-181', 'miata'],
    ['5', 'five'],
    ['183', 'Close to 181: miata'],
    ['190', 'Close to 181: miata'],
    ['1990', 'Close to 2002: bmw'],
    ['15000000', 'Close to 15,007,033: model t'],
    ['101', 'Close to 100: hundred'],
    ['100.4', 'Close to 100: hundred'],
  ])('%s gives %s', (result, expected) => {
    expect(findFact(result, FACTS, first)).toBe(expected)
  })

  it.each(['11', '200', '0', '0.3', '1E+20', '1E-12', 'abc'])(
    'has no fact for %s',
    (result) => {
      expect(findFact(result, FACTS, first)).toBeNull()
    },
  )

  it('has no fact without facts', () => {
    expect(findFact('181', new Map(), first)).toBeNull()
  })

  it('picks among facts for the same number', () => {
    const facts = loadFacts(['a', 'b', 'c'].map((fact) => ({ value: '7', fact })))
    expect(findFact('7', facts, (options) => options.at(-1))).toBe('c')
  })

  it('uses the shipped facts by default', () => {
    expect(findFact('181')).toContain('181 horsepower')
  })
})

describe('shipped facts', () => {
  it('are valid', () => {
    expect(entries.length).toBeGreaterThanOrEqual(200)
    for (const entry of entries) {
      expect(Object.keys(entry).sort()).toEqual(['fact', 'value'])
      const value = new Decimal(entry.value)
      expect(value.isFinite() && value.gte(0), entry.value).toBe(true)
      expect(entry.fact.length).toBeGreaterThan(0)
      expect(entry.fact.length).toBeLessThanOrEqual(MAX_FACT_LENGTH)
    }
    const facts = entries.map((entry) => entry.fact)
    expect(new Set(facts).size, 'duplicate facts').toBe(facts.length)
  })
})
