# Calculator

A calculator with a Vue interface and a Python engine. It runs locally and opens
in your browser.

## Features

- Add, subtract, multiply, divide, percent, sign toggle, parentheses and decimals
- Exact decimal arithmetic, so `0.1 + 0.2` gives `0.3`
- A car fun fact for the answer, when one matches it or is within 5% of it
- History panel you can open and close: click a past calculation to reuse it
- Light and dark themes
- Long numbers shrink to fit the display

## Run

All you need is Python 3.11 or newer. There is nothing to install.

```bash
git clone https://github.com/arnavmishra1/carculator.git
```

```bash
cd carculator
```

```bash
python3 main.py
```

This serves the app at `http://127.0.0.1:8765` and opens it in your browser.
Press Ctrl+C in the terminal to stop it. On Windows, use `py main.py` instead.

The server uses only Python's standard library, and the built frontend is
committed in `frontend/dist`, so Node isn't needed to run the app.

## Development

You only need these steps to run the tests or change the frontend. Python 3.11
and Node 24 are known to work.

### Python tests

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install -r requirements.txt
```

```bash
.venv/bin/python -m pytest
```

### Frontend

```bash
npm --prefix frontend install
```

```bash
npm --prefix frontend test
```

To work on the frontend with hot reload, keep `main.py` running and start Vite
in a second terminal:

```bash
npm --prefix frontend run dev
```

After changing the frontend, rebuild it and commit `frontend/dist` along with
your changes, so the app keeps running without Node:

```bash
npm --prefix frontend run build
```

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

- `calculator/engine.py`: parses and evaluates expressions, with no UI code
- `calculator/history.py`: stores past calculations for the session
- `calculator/facts.py`: picks a car fact for a result from `car_facts.json`
- `calculator/server.py`: local HTTP server for the API and the built frontend
- `frontend/src/calculator.js`: expression editing rules and app state
- `frontend/src/App.vue`: the display, keypad, history panel and keyboard handling
- `tests/`: tests for the engine, history, facts and server

Expressions are parsed with Python's `ast` module and only numbers and approved
operators are accepted, so typed input never runs as code.
