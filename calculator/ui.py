"""CustomTkinter window: display, keypad, keyboard input, history and theme."""

import re

import customtkinter as ctk

from calculator.engine import CalculationError, calculate
from calculator.history import History

PLUS, MINUS, TIMES, DIVIDE = "+", "−", "×", "÷"
OPERATORS = PLUS + MINUS + TIMES + DIVIDE

BACKGROUND = ("#F4F5F7", "#17181C")
PANEL = ("#EBEDF0", "#1F2025")
TEXT = ("#1C1E23", "#F2F3F5")
MUTED_TEXT = ("#6B7078", "#9AA0AA")
ERROR_TEXT = ("#C62828", "#FF8A80")
NUMBER_STYLE = {
    "fg_color": ("#FFFFFF", "#26282E"),
    "hover_color": ("#ECEEF2", "#32353D"),
    "text_color": TEXT,
}
FUNCTION_STYLE = {
    "fg_color": ("#E3E6EB", "#343740"),
    "hover_color": ("#D5D9E0", "#41454F"),
    "text_color": TEXT,
}
OPERATOR_STYLE = {
    "fg_color": ("#FFE6D1", "#5A3214"),
    "hover_color": ("#FFD8B8", "#70401C"),
    "text_color": ("#B84E08", "#FFB681"),
}
EQUALS_STYLE = {
    "fg_color": ("#C2570C", "#D9650A"),
    "hover_color": ("#A34909", "#EC7A1F"),
    "text_color": "#FFFFFF",
}

DISPLAY_FONT_SIZES = range(44, 15, -2)
HISTORY_TEXT_LIMIT = 24

_TRAILING_NUMBER = re.compile(r"(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$")

_CHARACTER_KEYS = {
    "+": PLUS,
    "-": MINUS,
    "*": TIMES,
    "x": TIMES,
    "X": TIMES,
    "/": DIVIDE,
}
_COMMAND_OR_CONTROL_STATE = 0x8 | 0x4


class CalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BACKGROUND)
        ctk.set_appearance_mode("dark")

        self.title("Calculator")
        self.geometry("660x620")
        self.minsize(580, 520)

        self.history = History()
        self.expression = ""
        self.caption = ""
        self.error = ""
        self.showing_result = False

        self.grid_columnconfigure(0, weight=3, uniform="columns")
        self.grid_columnconfigure(1, weight=2, uniform="columns")
        self.grid_rowconfigure(0, weight=1)

        self._build_calculator()
        self._build_history_panel()
        self._render_history()
        self._refresh_display()

        self.bind("<Key>", self._on_key)

    # Layout

    def _build_calculator(self):
        calculator = ctk.CTkFrame(self, fg_color="transparent")
        calculator.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)
        calculator.grid_columnconfigure(0, weight=1)
        calculator.grid_rowconfigure(1, weight=1)

        display = ctk.CTkFrame(calculator, fg_color="transparent")
        display.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        display.grid_columnconfigure(0, weight=1)

        self.caption_label = ctk.CTkLabel(
            display,
            text="",
            anchor="e",
            height=24,
            text_color=MUTED_TEXT,
            font=ctk.CTkFont(size=16),
        )
        self.caption_label.grid(row=0, column=0, sticky="ew")

        self.display_font = ctk.CTkFont(size=DISPLAY_FONT_SIZES[0], weight="bold")
        self.display_label = ctk.CTkLabel(
            display, text="0", anchor="e", height=64, font=self.display_font
        )
        self.display_label.grid(row=1, column=0, sticky="ew")
        self.display_label.bind("<Configure>", lambda _event: self._fit_display())

        self.keypad = ctk.CTkFrame(calculator, fg_color="transparent")
        self.keypad.grid(row=1, column=0, sticky="nsew")
        self._build_keypad()

    def _build_keypad(self):
        digit = NUMBER_STYLE
        function = FUNCTION_STYLE
        operator = OPERATOR_STYLE
        rows = [
            [("C", self.clear, function, 1), ("⌫", self.backspace, function, 1),
             ("(", self.open_parenthesis, function, 1),
             (")", self.close_parenthesis, function, 1)],
            [("7", None, digit, 1), ("8", None, digit, 1), ("9", None, digit, 1),
             (DIVIDE, None, operator, 1)],
            [("4", None, digit, 1), ("5", None, digit, 1), ("6", None, digit, 1),
             (TIMES, None, operator, 1)],
            [("1", None, digit, 1), ("2", None, digit, 1), ("3", None, digit, 1),
             (MINUS, None, operator, 1)],
            [("±", self.toggle_sign, function, 1), ("0", None, digit, 1),
             (".", self.decimal_point, digit, 1), (PLUS, None, operator, 1)],
            [("%", self.percent, function, 1), ("=", self.equals, EQUALS_STYLE, 3)],
        ]

        self.buttons = {}
        font = ctk.CTkFont(size=22)
        for column in range(4):
            self.keypad.grid_columnconfigure(column, weight=1, uniform="keys")
        for row_index, row in enumerate(rows):
            self.keypad.grid_rowconfigure(row_index, weight=1, uniform="keys")
            column = 0
            for label, command, style, span in row:
                button = ctk.CTkButton(
                    self.keypad,
                    text=label,
                    width=0,
                    height=0,
                    corner_radius=14,
                    font=font,
                    command=command or self._default_command(label),
                    **style,
                )
                button.grid(
                    row=row_index, column=column, columnspan=span,
                    sticky="nsew", padx=4, pady=4,
                )
                self.buttons[label] = button
                column += span

    def _default_command(self, label):
        if label in OPERATORS:
            return lambda: self.press_operator(label)
        return lambda: self.press_digit(label)

    def _build_history_panel(self):
        panel = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=16)
        panel.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            panel,
            text="History",
            anchor="w",
            text_color=TEXT,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="ew", padx=(16, 4), pady=(12, 4))

        self.clear_history_button = ctk.CTkButton(
            panel,
            text="Clear",
            width=56,
            height=28,
            corner_radius=8,
            command=self.clear_history,
            **FUNCTION_STYLE,
        )
        self.clear_history_button.grid(row=0, column=1, padx=(4, 12), pady=(12, 4))

        self.history_list = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.history_list.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=4)
        self.history_list.grid_columnconfigure(0, weight=1)

        self.theme_switch = ctk.CTkSwitch(
            panel,
            text="Dark theme",
            text_color=TEXT,
            progress_color=EQUALS_STYLE["fg_color"],
            command=self._apply_theme,
        )
        self.theme_switch.select()
        self.theme_switch.grid(
            row=2, column=0, columnspan=2, sticky="w", padx=16, pady=12
        )

    # Input

    def press_digit(self, digit):
        self._begin_edit(replace_result=True)
        if self.expression.endswith(")"):
            self.expression += TIMES
        self.expression += digit
        self._refresh_display()

    def decimal_point(self):
        self._begin_edit(replace_result=True)
        number = _TRAILING_NUMBER.search(self.expression)
        if number is None:
            if self.expression.endswith(")"):
                self.expression += TIMES
            self.expression += "0."
        elif "." not in number.group() and not re.search("[eE]", number.group()):
            self.expression += "."
        self._refresh_display()

    def press_operator(self, operator):
        self._begin_edit()
        if operator == MINUS and self.expression[-1:] in ("", "(", TIMES, DIVIDE):
            self.expression += operator
        else:
            base = self.expression.rstrip(OPERATORS)
            if base and not base.endswith("("):
                self.expression = base + operator
        self._refresh_display()

    def open_parenthesis(self):
        self._begin_edit(replace_result=True)
        if self.expression[-1:].isdigit() or self.expression[-1:] in (")", ".", "%"):
            self.expression += TIMES
        self.expression += "("
        self._refresh_display()

    def close_parenthesis(self):
        self._begin_edit()
        last = self.expression[-1:]
        has_open = self.expression.count("(") > self.expression.count(")")
        if has_open and last and last not in OPERATORS and last != "(":
            self.expression += ")"
        self._refresh_display()

    def percent(self):
        self._begin_edit()
        last = self.expression[-1:]
        if last.isdigit() or last in (")", ".", "%"):
            self.expression += "%"
        self._refresh_display()

    def toggle_sign(self):
        self._begin_edit()
        number = _TRAILING_NUMBER.search(self.expression)
        if number is None:
            if not self.expression or self.expression[-1] in OPERATORS + "(":
                self.expression += MINUS
        else:
            start = number.start()
            before = self.expression[:start]
            is_unary_minus = before.endswith(MINUS) and (
                len(before) == 1 or before[-2] in OPERATORS + "("
            )
            if is_unary_minus:
                self.expression = before[:-1] + number.group()
            else:
                self.expression = before + MINUS + number.group()
        self._refresh_display()

    def backspace(self):
        if self.showing_result:
            self.clear()
            return
        self._begin_edit()
        self.expression = self.expression[:-1]
        self._refresh_display()

    def clear(self):
        self.expression = ""
        self.caption = ""
        self.error = ""
        self.showing_result = False
        self._refresh_display()

    def equals(self):
        if self.showing_result or not self.expression:
            return
        try:
            result = calculate(self.expression)
        except CalculationError as error:
            self.error = str(error)
            self.caption = self.expression
        else:
            self.history.add(self.expression, result)
            self.caption = f"{self.expression} ="
            self.expression = self._as_display_text(result)
            self.error = ""
            self.showing_result = True
            self._render_history()
        self._refresh_display()

    def _begin_edit(self, replace_result=False):
        if self.showing_result and replace_result:
            self.expression = ""
        self.showing_result = False
        self.caption = ""
        self.error = ""

    @staticmethod
    def _as_display_text(result):
        return MINUS + result[1:] if result.startswith("-") else result

    def _on_key(self, event):
        if event.state & _COMMAND_OR_CONTROL_STATE:
            return
        if event.keysym in ("Return", "KP_Enter"):
            self.equals()
        elif event.keysym == "Escape":
            self.clear()
        elif event.keysym == "BackSpace":
            self.backspace()
        elif event.char.isascii() and event.char.isdigit():
            self.press_digit(event.char)
        elif event.char in _CHARACTER_KEYS:
            self.press_operator(_CHARACTER_KEYS[event.char])
        elif event.char == "=":
            self.equals()
        elif event.char == ".":
            self.decimal_point()
        elif event.char == "(":
            self.open_parenthesis()
        elif event.char == ")":
            self.close_parenthesis()
        elif event.char == "%":
            self.percent()

    # Display

    def _refresh_display(self):
        self.caption_label.configure(text=self._tail(self.caption, 40))
        self.display_label.configure(
            text_color=ERROR_TEXT if self.error else TEXT
        )
        self._fit_display()

    def _fit_display(self):
        """Shrink the display font to fit, then show the end of the text."""
        text = self.error or self.expression or "0"
        available = self.display_label.winfo_width() - 12
        if available <= 1:
            self.display_label.configure(text=text)
            return

        for size in DISPLAY_FONT_SIZES:
            self.display_font.configure(size=size)
            if self.display_font.measure(text) <= available:
                break
        while len(text) > 1 and self.display_font.measure(text) > available:
            text = "…" + text[2:]
        self.display_label.configure(text=text)

    @staticmethod
    def _tail(text, limit):
        return text if len(text) <= limit else "…" + text[-(limit - 1):]

    # History

    def _render_history(self):
        for widget in self.history_list.winfo_children():
            widget.destroy()

        if not len(self.history):
            ctk.CTkLabel(
                self.history_list, text="No calculations yet", text_color=MUTED_TEXT
            ).grid(row=0, column=0, sticky="ew", pady=12)
            return

        for row, entry in enumerate(self.history):
            text = (
                f"{self._tail(entry.expression, HISTORY_TEXT_LIMIT)}\n"
                f"= {self._tail(entry.result, HISTORY_TEXT_LIMIT)}"
            )
            ctk.CTkButton(
                self.history_list,
                text=text,
                anchor="w",
                height=48,
                corner_radius=8,
                fg_color="transparent",
                hover_color=FUNCTION_STYLE["hover_color"],
                text_color=TEXT,
                command=lambda selected=entry: self._reuse_entry(selected),
            ).grid(row=row, column=0, sticky="ew", pady=2)

    def _reuse_entry(self, entry):
        self.expression = entry.expression
        self.caption = ""
        self.error = ""
        self.showing_result = False
        self._refresh_display()

    def clear_history(self):
        self.history.clear()
        self._render_history()

    def _apply_theme(self):
        ctk.set_appearance_mode("dark" if self.theme_switch.get() else "light")
