import json
from decimal import Decimal

import pytest

from calculator.facts import FACTS_PATH, find_fact

MAX_FACT_LENGTH = 110

FACTS = {
    Decimal("181"): ["miata"],
    Decimal("5.0"): ["five"],
    Decimal("100"): ["hundred"],
    Decimal("102"): ["hundred and two"],
    Decimal("2002"): ["bmw"],
    Decimal("15007033"): ["model t"],
}


def first(options):
    return options[0]


@pytest.mark.parametrize(
    "result, expected",
    [
        ("181", "miata"),
        ("-181", "miata"),
        ("5", "five"),
        ("183", "Close to 181: miata"),
        ("190", "Close to 181: miata"),
        ("1990", "Close to 2002: bmw"),
        ("15000000", "Close to 15,007,033: model t"),
        ("101", "Close to 100: hundred"),
        ("100.4", "Close to 100: hundred"),
    ],
)
def test_matching(result, expected):
    assert find_fact(result, FACTS, first) == expected


@pytest.mark.parametrize("result", ["11", "200", "0", "0.3", "1E+20", "1E-12", "abc"])
def test_no_fact_when_nothing_is_close(result):
    assert find_fact(result, FACTS, first) is None


def test_no_fact_without_facts():
    assert find_fact("181", {}, first) is None


def test_picks_among_facts_for_the_same_number():
    facts = {Decimal("7"): ["a", "b", "c"]}
    assert find_fact("7", facts, lambda options: options[-1]) == "c"


def test_shipped_facts_are_valid():
    entries = json.loads(FACTS_PATH.read_text(encoding="utf-8"))
    assert len(entries) >= 200
    for entry in entries:
        assert set(entry) == {"value", "fact"}
        value = Decimal(entry["value"])
        assert value.is_finite() and value >= 0, entry
        assert 0 < len(entry["fact"]) <= MAX_FACT_LENGTH, entry
    facts = [entry["fact"] for entry in entries]
    assert len(facts) == len(set(facts)), "duplicate facts"


def test_shipped_facts_are_used_by_default():
    assert "181 horsepower" in find_fact("181")
