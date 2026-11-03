// Past calculations, newest first, saved in the browser.

const MAX_ENTRIES = 100
const STORAGE_KEY = 'calculator.history'

function browserStorage() {
  try {
    return window.localStorage
  } catch {
    return null
  }
}

const isEntry = (entry) =>
  typeof entry?.expression === 'string' && typeof entry?.result === 'string'

export function createHistory({
  storage = browserStorage(),
  maxEntries = MAX_ENTRIES,
} = {}) {
  let entries = read()

  function read() {
    try {
      const saved = JSON.parse(storage?.getItem(STORAGE_KEY) ?? '[]')
      return Array.isArray(saved) ? saved.filter(isEntry).slice(0, maxEntries) : []
    } catch {
      return []
    }
  }

  function save() {
    try {
      storage?.setItem(STORAGE_KEY, JSON.stringify(entries))
    } catch {
      // History still works for this visit; it just won't be remembered.
    }
  }

  return {
    entries: () => [...entries],
    add(expression, result) {
      entries = [{ expression, result }, ...entries].slice(0, maxEntries)
      save()
    },
    clear() {
      entries = []
      save()
    },
  }
}
