// Car fun facts matched to calculation results. No UI code here.

import Decimal from 'decimal.js'
import entries from './car_facts.json'

const CLOSE_MATCH_TOLERANCE = new Decimal('0.05')
const GROUPING_THRESHOLD = 10_000

/** Group fact entries into a Map of value text to { value, facts }. */
export function loadFacts(list = entries) {
  const facts = new Map()
  for (const entry of list) {
    const value = new Decimal(entry.value)
    const key = value.toString()
    if (!facts.has(key)) facts.set(key, { value, facts: [] })
    facts.get(key).facts.push(entry.fact)
  }
  return facts
}

const pickRandom = (options) =>
  options[Math.floor(Math.random() * options.length)]

let defaultFacts

/**
 * Return a car fact for a formatted result, or null if no fact is close.
 *
 * An exact match wins. Otherwise the nearest fact within 5% is used and
 * labelled with its own number. Negative results use their absolute value.
 */
export function findFact(result, facts, choose = pickRandom) {
  facts ??= defaultFacts ??= loadFacts()
  let value
  try {
    value = new Decimal(result).abs()
  } catch {
    return null
  }
  if (!value.isFinite()) return null

  const exact = facts.get(value.toString())
  if (exact) return choose(exact.facts)
  if (value.isZero() || !facts.size) return null

  let nearest
  for (const candidate of facts.values()) {
    const distance = candidate.value.minus(value).abs()
    const order = nearest && distance.comparedTo(nearest.distance)
    if (
      !nearest ||
      order < 0 ||
      (order === 0 && candidate.value.lessThan(nearest.value))
    ) {
      nearest = { ...candidate, distance }
    }
  }
  if (nearest.distance.greaterThan(value.times(CLOSE_MATCH_TOLERANCE))) {
    return null
  }
  return `Close to ${label(nearest.value)}: ${choose(nearest.facts)}`
}

function label(value) {
  const text = value.toFixed()
  if (value.lessThan(GROUPING_THRESHOLD)) return text
  const [whole, fraction] = text.split('.')
  const grouped = whole.replace(/\B(?=(\d{3})+$)/g, ',')
  return fraction ? `${grouped}.${fraction}` : grouped
}
