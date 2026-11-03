import { describe, expect, it } from 'vitest'
import { createApi } from './api.js'
import { createHistory } from './history.js'

function memoryStorage(initial = {}) {
  const data = { ...initial }
  return {
    getItem: (key) => data[key] ?? null,
    setItem: (key, value) => {
      data[key] = value
    },
  }
}

describe('history', () => {
  it('is newest first', () => {
    const history = createHistory({ storage: memoryStorage() })
    history.add('1+1', '2')
    history.add('2+2', '4')
    expect(history.entries().map((entry) => entry.expression)).toEqual(['2+2', '1+1'])
  })

  it('drops the oldest entries', () => {
    const history = createHistory({ storage: memoryStorage(), maxEntries: 2 })
    for (const number of ['0', '1', '2']) history.add(number, number)
    expect(history.entries().map((entry) => entry.expression)).toEqual(['2', '1'])
  })

  it('clears', () => {
    const history = createHistory({ storage: memoryStorage() })
    history.add('1+1', '2')
    history.clear()
    expect(history.entries()).toEqual([])
  })

  it('is remembered between visits', () => {
    const storage = memoryStorage()
    createHistory({ storage }).add('1+1', '2')
    expect(createHistory({ storage }).entries()).toEqual([
      { expression: '1+1', result: '2' },
    ])
  })

  it.each(['not json', '{"a": 1}', '[1, {"expression": 2}]'])(
    'ignores bad saved data: %s',
    (saved) => {
      const storage = memoryStorage({ 'calculator.history': saved })
      expect(createHistory({ storage }).entries()).toEqual([])
    },
  )

  it('works without storage', () => {
    const broken = {
      getItem() {
        throw new Error('blocked')
      },
      setItem() {
        throw new Error('blocked')
      },
    }
    const history = createHistory({ storage: broken })
    history.add('1+1', '2')
    expect(history.entries()).toHaveLength(1)
  })
})

describe('api', () => {
  it('returns the result, fact and history', async () => {
    const api = createApi(createHistory({ storage: memoryStorage() }))
    const response = await api.calculate('180+1')
    expect(response.result).toBe('181')
    expect(response.fact).toContain('181 horsepower')
    expect(response.history).toEqual([{ expression: '180+1', result: '181' }])
  })

  it('does not record failed calculations', async () => {
    const api = createApi(createHistory({ storage: memoryStorage() }))
    await expect(api.calculate('1/0')).rejects.toThrow("Can't divide by zero")
    expect((await api.loadHistory()).history).toEqual([])
  })

  it('clears history', async () => {
    const api = createApi(createHistory({ storage: memoryStorage() }))
    await api.calculate('1+1')
    expect((await api.clearHistory()).history).toEqual([])
    expect((await api.loadHistory()).history).toEqual([])
  })
})
