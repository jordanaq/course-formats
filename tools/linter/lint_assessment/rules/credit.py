"""The group credit rule (§2.4.2, §8 check 15) — the rule v0.11.0 exists for.

Two arithmetics live here and they must never blend:

    equal   every alternative's points == group.points / choose_n    exactly
    capped  every alternative's points <= group.points
            and full marks must be reachable: the choose_n largest alternatives sum to
            at least group.points — a **warning**, not an error, because a paper can be
            internally consistent and still unable to award its own weight.

The mode is read, never inferred: a group that says nothing is `equal`, and a group whose
alternatives merely happen to be unequal is reported as a broken `equal` group rather than
quietly reinterpreted as a pool. That is the whole reason `credit` is a field.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Iterator

from .. import rationals
from ..diagnostics import Diagnostic, error, warning
from ..document import CREDIT_MODES, Bundle, Question


def credit_mode(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing.

    Ensures: an `error` for a group whose `credit` is present but is not an object, whose
    `mode` is missing, or whose `mode` is outside `equal | capped`; and an `error` for a
    `credit` node on a question that is not a group, since a non-group has no credit rule to
    apply.
    """
    for section in bundle.sections():
        for question in section.questions():
            if not question.is_group:
                if "credit" in question.raw:
                    yield error(
                        "credit",
                        f"{question.path}.credit",
                        "credit applies to an alternative_set only; this question is not a "
                        "group and has no credit rule to apply (§2.4.2)",
                    )
                continue
            if "credit" not in question.raw:
                continue
            mode = question.credit_mode
            if mode is None:
                yield error(
                    "credit",
                    f"{question.path}.credit",
                    "credit must be an object carrying a string `mode` (§2.4.2)",
                )
            elif mode not in CREDIT_MODES:
                yield error(
                    "credit",
                    f"{question.path}.credit.mode",
                    f"credit mode {mode!r} is not one of {sorted(CREDIT_MODES)} (§2.4.2)",
                )


def _readable(group: Question) -> tuple[Fraction, int, list[tuple[str, Fraction]]] | None:
    """The group's weight, `choose_n`, and each alternative's points — or `None`.

    `None` means a field is malformed; the caller then says nothing, because the defect is
    already one diagnostic from `points` or `credit_mode` and two reports of one fault read
    as two faults.
    """
    weight = group.points_value()
    choose_n = group.choose_n
    if weight is None or choose_n is None or choose_n < 1:
        return None
    alternatives: list[tuple[str, Fraction]] = []
    for alternative in group.alternatives():
        alternative_id = alternative.id
        text = alternative.points
        if alternative_id is None or text is None:
            return None
        value = rationals.parse(text)
        if value is None:
            return None
        alternatives.append((alternative_id, value))
    if not alternatives:
        return None
    return weight, choose_n, alternatives


def equal_shares(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing.

    Ensures: for every `equal` group (mode absent or `equal`) whose points and alternatives
    are all well-formed, an `error` for each alternative whose `points` is not exactly
    `group.points / choose_n` as a rational — including the case where the division is not
    representable in integers but both strings are canonical, which is a legitimately
    unequal group and not a non-canonical value.
    """
    for section in bundle.sections():
        for question in section.questions():
            if not question.is_group or question.credit_mode != "equal":
                continue
            readable = _readable(question)
            if readable is None:
                continue
            weight, choose_n, alternatives = readable
            share = weight / choose_n
            for alternative_id, value in alternatives:
                if value != share:
                    yield error(
                        "credit",
                        f"{question.path}.alternatives",
                        f"alternative {alternative_id!r} is worth {rationals.format(value)} "
                        f"but this group is equal-credit: each of {choose_n} alternatives "
                        f"must be exactly {rationals.format(share)} "
                        f"({rationals.format(weight)} / {choose_n}) (§2.4.2)",
                    )


def capped_ceiling(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing.

    Ensures: for every `capped` group whose fields are well-formed, an `error` for each
    alternative whose `points` exceeds the group's `points`, and at most one `warning` per
    group when the `choose_n` largest alternatives sum to less than the group's weight —
    the unreachable-purse smell of §8 check 15, whose message states the reachable maximum.
    """
    for section in bundle.sections():
        for question in section.questions():
            if not question.is_group or question.credit_mode != "capped":
                continue
            readable = _readable(question)
            if readable is None:
                continue
            weight, choose_n, alternatives = readable
            over = False
            for alternative_id, value in alternatives:
                if value > weight:
                    over = True
                    yield error(
                        "credit",
                        f"{question.path}.alternatives",
                        f"alternative {alternative_id!r} is worth "
                        f"{rationals.format(value)}, above the group's "
                        f"{rationals.format(weight)}-point ceiling (§2.4.2)",
                    )
            if over:
                continue
            best = sum(
                sorted((value for _, value in alternatives), reverse=True)[:choose_n],
                Fraction(0),
            )
            if best < weight:
                yield warning(
                    "credit",
                    question.path,
                    f"a capped pool of {len(alternatives)} alternatives, choosing "
                    f"{choose_n}, can reach at most {rationals.format(best)} of its "
                    f"{rationals.format(weight)} points; no selection of answers can earn "
                    f"full marks on this question (§8 check 15)",
                )


def check(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing.

    Ensures: `credit_mode`, then `equal_shares`, then `capped_ceiling`. A group whose mode
    is invalid is not passed to the arithmetic rules, so one broken field produces one
    diagnostic.
    """
    yield from credit_mode(bundle)
    yield from equal_shares(bundle)
    yield from capped_ceiling(bundle)
