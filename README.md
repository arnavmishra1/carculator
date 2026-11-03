# Calculator

A calculator with a Vue interface that runs entirely in your browser.

**Try it:** https://arnavmishra1.github.io/carculator/

## Features

- Add, subtract, multiply, divide, percent, sign toggle, parentheses and decimals
- Exact decimal arithmetic, so `0.1 + 0.2` gives `0.3`
- A car fun fact for the answer, when one matches it or is within 5% of it
- History panel you can open and close: click a past calculation to reuse it
- History is saved in your browser, so it's still there on your next visit
- Light and dark themes
- Long numbers shrink to fit the display

## Run locally

You need Node 24 or newer.

```bash
git clone https://github.com/arnavmishra1/carculator.git
```

```bash
cd carculator/frontend
```

```bash
npm install
```

```bash
npm run dev
```

This starts a dev server with hot reload and prints its address, usually
`http://localhost:5173`.

## Test and build

```bash
npm test
```

```bash
npm run build
```

The build goes to `frontend/dist`. It uses relative paths, so it works from any
folder on any static host.

## Deploy

Every push to `main` runs the tests, builds the app and publishes it to GitHub
Pages, using `.github/workflows/deploy.yml`. In the repository's
**Settings → Pages**, the source must be set to **GitHub Actions**.

## Keyboard

| Key | Action |
| --- | --- |
| `0`–`9`, `.` | Enter a number |
| `+` `-` `*` `/` | Operators (`x` also multiplies) |
| `(` `)` `%` | Parentheses and percent |
| Enter or `=` | Calculate |
| Backspace | Delete the last character |
| Esc | Clear |
| `H` | Show or hide history |

## Layout

All code is in `frontend/src`:

- `engine.js`: parses and evaluates expressions, with no UI code
- `facts.js`: picks a car fact for a result from `car_facts.json`
- `history.js`: stores past calculations in the browser's local storage
- `api.js`: connects the engine, facts and history for the interface
- `calculator.js`: expression editing rules and app state
- `App.vue`: the display, keypad, history panel and keyboard handling
- `*.test.js`: tests for each of the above

Expressions are read by a small parser that accepts only numbers and approved
operators, so typed input never runs as code. Arithmetic uses `decimal.js`, so
results are exact decimals rather than floating-point approximations.
