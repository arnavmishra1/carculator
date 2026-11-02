"""Car fun facts matched to calculation results. No UI or web code here."""

import json
import random
from decimal import Decimal, InvalidOperation
from functools import cache
from pathlib import Path

FACTS_PATH = Path(__file__).with_name("car_facts.json")
CLOSE_MATCH_TOLERANCE = Decimal("0.05")
GROUPING_THRESHOLD = 10_000


def load_facts(path=FACTS_PATH):
    """Read a fact file into a {value: [facts]} mapping."""
    facts = {}
    for entry in json.loads(Path(path).read_text(encoding="utf-8")):
        facts.setdefault(Decimal(entry["value"]), []).append(entry["fact"])
    return facts


@cache
def _default_facts():
    return load_facts()


def find_fact(result, facts=None, choose=random.choice):
    """Return a car fact for a formatted result, or None if no fact is close.

    An exact match wins. Otherwise the nearest fact within 5% is used and
    labelled with its own number. Negative results use their absolute value.
    """
    facts = _default_facts() if facts is None else facts
    try:
        value = abs(Decimal(result))
    except InvalidOperation:
        return None
    if not value.is_finite():
        return None

    if value in facts:
        return choose(facts[value])
    if value.is_zero() or not facts:
        return None

    nearest = min(facts, key=lambda candidate: (abs(candidate - value), candidate))
    if abs(nearest - value) > value * CLOSE_MATCH_TOLERANCE:
        return None
    return f"Close to {_label(nearest)}: {choose(facts[nearest])}"


def _label(value):
    return f"{value:,f}" if value >= GROUPING_THRESHOLD else f"{value:f}"
