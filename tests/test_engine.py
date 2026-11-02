import pytest

from calculator.engine import CalculationError, calculate
from calculator.history import History


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("2+3", "5"),
        ("10-4", "6"),
        ("6*7", "42"),
        ("9/3", "3"),
        ("2+3*4", "14"),
        ("(2+3)*4", "20"),
        ("((1+2)*(3+4))", "21"),
        ("-5+2", "-3"),
        ("--5", "5"),
        ("2*-3", "-6"),
        ("0.1+0.2", "0.3"),
        (".5+.5", "1"),
        ("5.", "5"),
        ("007+1", "8"),
        ("1/3", "0.3333333333333333"),
        ("1/3*3", "1"),
        ("2/3", "0.6666666666666667"),
        ("1-1", "0"),
        ("-1+1", "0"),
        ("6×7", "42"),
        ("8÷2", "4"),
        ("5−2", "3"),
        (" 1 + 1 ", "2"),
    ],
)
def test_arithmetic(expression, expected):
    assert calculate(expression) == expected


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("50%", "0.5"),
        ("10/50%", "20"),
        ("200*10%", "20"),
        ("(20+30)%", "0.5"),
        ("2*(1+1)%", "0.04"),
        ("50%%", "0.005"),
    ],
)
def test_percent(expression, expected):
    assert calculate(expression) == expected


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("12345678901234567890*10", "1.234567890123457E+20"),
        ("1/1000000000000", "1E-12"),
        ("1E+20+1", "1E+20"),
        ("1000000", "1000000"),
        ("0.000001", "0.000001"),
    ],
)
def test_large_and_small_numbers(expression, expected):
    assert calculate(expression) == expected


def test_decimal_literals_keep_their_precision():
    assert calculate("1234567890.123456+0") == "1234567890.123456"


@pytest.mark.parametrize("expression", ["1/0", "0/0", "1/(2-2)", "1/0%"])
def test_division_by_zero(expression):
    with pytest.raises(CalculationError, match="divide by zero"):
        calculate(expression)


@pytest.mark.parametrize(
    "expression",
    [
        "2+",
        "*2",
        "(1+2",
        "1+2)",
        "1.2.3",
        "%",
        "()",
        "2(3)",
        "E",
    ],
)
def test_invalid_expressions(expression):
    with pytest.raises(CalculationError, match="Invalid expression"):
        calculate(expression)


@pytest.mark.parametrize(
    "expression",
    [
        "2**3",
        "7//2",
        "__import__('os')",
        "print(1)",
        "abs(1)",
        "1 if 1 else 2",
        "[1]",
        "'a'",
        "1j",
        "0x10",
        "1_000",
    ],
)
def test_python_features_are_rejected(expression):
    with pytest.raises(CalculationError, match="Invalid expression"):
        calculate(expression)


def test_empty_expression():
    with pytest.raises(CalculationError, match="Enter an expression"):
        calculate("   ")


def test_overflow_is_reported():
    with pytest.raises(CalculationError, match="too large"):
        calculate("1E999999*10")


def test_deep_nesting_is_reported():
    with pytest.raises(CalculationError):
        calculate("(" * 5000 + "1" + ")" * 5000)


def test_history_is_newest_first():
    history = History()
    history.add("1+1", "2")
    history.add("2+2", "4")
    assert [entry.expression for entry in history] == ["2+2", "1+1"]


def test_history_drops_oldest_entries():
    history = History(max_entries=2)
    for number in range(3):
        history.add(str(number), str(number))
    assert [entry.expression for entry in history] == ["2", "1"]


def test_history_clear():
    history = History()
    history.add("1+1", "2")
    history.clear()
    assert len(history) == 0
