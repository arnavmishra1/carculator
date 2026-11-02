"""Safe expression evaluation using exact decimal arithmetic. No UI code here."""

import ast
import operator
import re
from decimal import Decimal, DecimalException, Overflow, localcontext

WORKING_PRECISION = 34
DISPLAY_PRECISION = 16
MAX_PLAIN_EXPONENT = 16
MIN_PLAIN_EXPONENT = -9

_ALLOWED_TEXT = re.compile(r"[0-9.+\-*/()%eE ]*")
_LEADING_ZEROS = re.compile(r"(?<![\d.])0+(?=\d)")
_TRAILING_NUMBER = re.compile(r"(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$")

_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class CalculationError(Exception):
    """An expression could not be evaluated. The message is shown to the user."""


def evaluate(expression):
    """Evaluate an arithmetic expression and return its value as a Decimal."""
    source = _normalize(expression)
    if not source:
        raise CalculationError("Enter an expression")

    try:
        tree = ast.parse(source, mode="eval")
        with localcontext(prec=WORKING_PRECISION):
            return _evaluate_node(tree.body, source)
    except (SyntaxError, ValueError):
        raise CalculationError("Invalid expression") from None
    except (RecursionError, MemoryError):
        raise CalculationError("Expression too complex") from None
    except Overflow:
        raise CalculationError("Number too large") from None
    except DecimalException:
        raise CalculationError("Invalid expression") from None


def format_result(value):
    """Round a Decimal for display, using scientific notation at extremes."""
    try:
        with localcontext(prec=DISPLAY_PRECISION):
            rounded = (+value).normalize()
    except Overflow:
        raise CalculationError("Number too large") from None

    if rounded.is_zero():
        return "0"
    if MIN_PLAIN_EXPONENT <= rounded.adjusted() < MAX_PLAIN_EXPONENT:
        return format(rounded, "f")
    return str(rounded)


def calculate(expression):
    """Evaluate an expression and return the formatted result."""
    return format_result(evaluate(expression))


def _normalize(expression):
    text = expression.replace("×", "*").replace("÷", "/").replace("−", "-").strip()
    if not _ALLOWED_TEXT.fullmatch(text):
        raise CalculationError("Invalid expression")
    return _LEADING_ZEROS.sub("", _expand_percent(text))


def _expand_percent(text):
    """Rewrite each postfix percent, so that 50% becomes (50/100)."""
    expanded = ""
    for character in text:
        if character != "%":
            expanded += character
            continue
        start = _operand_start(expanded.rstrip())
        expanded = f"{expanded[:start]}({expanded[start:]}/100)"
    return expanded


def _operand_start(text):
    if text.endswith(")"):
        depth = 0
        for index in range(len(text) - 1, -1, -1):
            depth += {")": 1, "(": -1}.get(text[index], 0)
            if depth == 0:
                return index

    number = _TRAILING_NUMBER.search(text)
    if number is None:
        raise CalculationError("Invalid expression")
    return number.start()


def _evaluate_node(node, source):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        # The literal's source text is used because the parsed float has
        # already lost the precision Decimal is here to keep.
        return Decimal(source[node.col_offset:node.end_col_offset])

    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate_node(node.operand, source))

    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate_node(node.left, source)
        right = _evaluate_node(node.right, source)
        if isinstance(node.op, ast.Div) and right.is_zero():
            raise CalculationError("Can't divide by zero")
        return _BINARY_OPERATORS[type(node.op)](left, right)

    raise CalculationError("Invalid expression")
