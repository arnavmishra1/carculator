# Calculator

A desktop calculator written in Python with a CustomTkinter interface.

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

## Run

```bash
.venv/bin/python main.py
```

## Test

```bash
.venv/bin/python -m pytest
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
- `calculator/ui.py`: the window, keypad and keyboard handling
- `tests/test_engine.py`: tests for the engine and history

Expressions are parsed with Python's `ast` module and only numbers and approved
operators are accepted, so typed input never runs as code.
