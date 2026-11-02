const UNREACHABLE = "Can't reach the server"

async function request(path, options) {
  let response, body
  try {
    response = await fetch(path, options)
    body = await response.json()
  } catch {
    throw new Error(UNREACHABLE)
  }
  if (!response.ok) throw new Error(body.error ?? UNREACHABLE)
  return body
}

export const api = {
  calculate: (expression) =>
    request('/api/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ expression }),
    }),
  loadHistory: () => request('/api/history'),
  clearHistory: () => request('/api/history', { method: 'DELETE' }),
}
