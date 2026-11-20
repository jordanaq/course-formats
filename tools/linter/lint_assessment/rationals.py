"""Canonical rational strings (§2.3.1), exactly.

A point value in this format is a canonical rational string: `"0"`, a positive integer with
no leading zeros, or a positive integer over a positive integer in **lowest terms**. `"5/1"`,
`"2/4"`, `"05"` and `"4.5"` are all non-canonical; `"9/2"` is what `4.5` becomes
(§10's migration rule, which converts by exact value and never by string surgery).

Arithmetic is `fractions.Fraction` throughout, so `"5" / 3` stays `5/3` and a sum of awards
is compared to a ceiling without a float ever existing.
"""
from __future__ import annotations

import re
from fractions import Fraction

#: The canonical spelling, as a whole-string match.
CANONICAL = re.compile(r"^(?:0|[1-9][0-9]*)(?:/(?:[1-9][0-9]*))?$")


def parse(text: str) -> Fraction | None:
    """Requires: `text` is a string.

    Ensures: the exact value of `text` if it is a canonical rational string, else `None`.
    Never rounds, never accepts a decimal point, never accepts `"5/1"` or an unreduced
    fraction.
    """
    if not CANONICAL.match(text):
        return None
    if "/" in text:
        num, den = text.split("/", 1)
        value = Fraction(int(num), int(den))
    else:
        value = Fraction(int(text))
    # the pattern cannot decide lowest terms, so canonicality is settled by round-trip:
    # "5/1" and "2/4" parse to values whose canonical spelling differs from the input
    return value if format(value) == text else None


def is_canonical(text: str) -> bool:
    """Requires: `text` is a string.

    Ensures: `True` exactly when `parse(text)` is not `None` — including the lowest-terms
    rule, which a pure pattern match cannot decide.
    """
    return parse(text) is not None


def format(value: Fraction) -> str:
    """Requires: `value` is a `Fraction` with `value >= 0`.

    Ensures: the canonical rational string for exactly that value — `"0"` for zero, a bare
    integer when the denominator is 1 (never `"n/1"`), otherwise `"n/d"` in lowest terms.
    """
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def parse_many(texts: list[str]) -> tuple[Fraction, ...] | None:
    """Requires: nothing.

    Ensures: the values in order when every element is canonical, else `None` — rules that
    need several values report one diagnostic for the whole set rather than one per
    element.
    """
    values = []
    for text in texts:
        value = parse(text)
        if value is None:
            return None
        values.append(value)
    return tuple(values)
