# Calculator

A calculator with a Vue interface and a Python engine. It runs locally and opens
in your browser.

## Features

- Add, subtract, multiply, divide, percent, sign toggle, parentheses and decimals
- Exact decimal arithmetic, so `0.1 + 0.2` gives `0.3`
- History panel: click a past calculation to reuse it
- Light and dark themes
- Long numbers shrink to fit the display

## Setup

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install -r requirements.txt
```

```bash
npm --prefix frontend install
```

```bash
npm --prefix frontend run build
```

Python 3.11 and Node 24 are known to work.

## Run

```bash
.venv/bin/python main.py
```

This serves the app at `http://127.0.0.1:8765` and opens it in your browser.
Press Ctrl+C in the terminal to stop it. Rebuild the frontend after changing it.

To work on the frontend with hot reload, keep `main.py` running and start Vite
in a second terminal:

```bash
npm --prefix frontend run dev
```

## Test

```bash
.venv/bin/python -m pytest
```

```bash
npm --prefix frontend test
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

## Layout

- `calculator/engine.py`: parses and evaluates expressions, with no UI code
- `calculator/history.py`: stores past calculations for the session
- `calculator/server.py`: local HTTP server for the API and the built frontend
- `frontend/src/calculator.js`: expression editing rules and app state
- `frontend/src/App.vue`: the display, keypad, history panel and keyboard handling
- `tests/`: tests for the engine, history and server

Expressions are parsed with Python's `ast` module and only numbers and approved
operators are accepted, so typed input never runs as code.
