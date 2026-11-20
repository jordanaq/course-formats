"""Criterion weights — a rubric's own partition of its question (§4.2.1, §8 check 8).

A criterion MAY declare `points`: its share of the question. Three rules, one rule family,
because they only make sense together:

* **all or none** — a rubric either weights every criterion or none. A half-weighted rubric
  has no defined remainder: reading an undeclared criterion as the leftover invents a number,
  reading it as zero erases a criterion.
* **the sum is the question** — the declared weights add up to exactly the owner's `points`,
  as rationals. A short sum leaves marks unreachable; an over-sum makes full marks impossible;
  neither is repaired by scaling.
* **canonical** — a weight is a point value like any other (§2.3.1), so `"5/1"` is not a weight.

Absence is not a violation: an unweighted rubric is legal and is *not* equal weighting — each
criterion is awardable up to the question's own points, which is what every 0.4.1–0.11.2
rubric does. This rule therefore reports nothing for it, and the report rule bounds an award
only against a weight that is written down.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Iterator

from ..diagnostics import Diagnostic, error
from ..document import Bundle
from ..jsonview import get_array, get_str, objects
from ..rationals import format as format_rational
from ..rationals import parse


def _points_of(bundle: Bundle) -> dict[str, tuple[str, str]]:
    """Requires: nothing.

    Ensures: owner id → (raw `points` text, path) for every question and every alternative. A
    group is its own owner for `points`, but a group has no answer key (§2.4.5), so its entry
    is never read here.
    """
    found: dict[str, tuple[str, str]] = {}
    for section in bundle.sections():
        for question in section.questions():
            question_id = question.id
            raw = question.points
            if question_id is not None and raw is not None:
                found[question_id] = (raw, question.path)
            for alternative in question.alternatives():
                alternative_id = alternative.id
                alternative_points = alternative.points
                if alternative_id is not None and alternative_points is not None:
                    found[alternative_id] = (alternative_points, alternative.path)
    return found


def check(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing.

    Ensures: one `error` per rubric that is half-weighted, per rubric whose weights do not sum
    to its owner's `points`, and per weight that is not a canonical rational. A rubric that
    declares no weights yields nothing, and a malformed weight is reported once — the
    sum cannot be checked honestly while a member is unreadable, so it is not also reported.
    """
    points_of = _points_of(bundle)
    key = bundle.answer_key
    for owner_id in key:
        entry = key.get(owner_id)
        if not isinstance(entry, dict):
            continue
        members = get_array(entry, "criteria")
        criteria = objects(members) if members is not None else ()
        if not criteria:
            continue

        # "declares a weight" and "declares a readable weight" are different facts: an
        # unreadable weight still counts as declared, or one bad value would look like a
        # half-weighted rubric as well.
        declaring = [
            index for index, criterion in enumerate(criteria) if criterion.get("points") is not None
        ]
        if not declaring:
            continue
        if len(declaring) != len(criteria):
            silent = [
                get_str(criteria[index], "id") or f"#{index + 1}"
                for index in range(len(criteria))
                if index not in declaring
            ]
            yield error(
                "weights",
                f"$.answer_key['{owner_id}'].criteria",
                f"{len(declaring)} of {len(criteria)} criteria declare a weight; a rubric is "
                f"either fully weighted or unweighted (§4.2.1), so "
                f"{', '.join(repr(s) for s in silent)} would have no defined share",
            )
            continue

        weights: list[Fraction] = []
        for index in declaring:
            criterion = criteria[index]
            criterion_id = get_str(criterion, "id") or f"#{index + 1}"
            raw = criterion.get("points")
            value = parse(raw) if isinstance(raw, str) else None
            if value is None:
                yield error(
                    "weights",
                    f"$.answer_key['{owner_id}'].criteria[{index}].points",
                    f"criterion {criterion_id!r} declares a weight {raw!r} that is not a "
                    f"canonical rational (§2.3.1): a positive integer or a lowest-terms "
                    f'fraction such as "2" or "3/2"',
                )
            else:
                weights.append(value)

        owner = points_of.get(owner_id)
        if owner is None or len(weights) != len(declaring):
            # an unreadable weight makes the sum meaningless; it was reported above
            continue
        total_points = parse(owner[0])
        if total_points is None:
            continue
        total = sum(weights, Fraction(0))
        if total != total_points:
            yield error(
                "weights",
                f"$.answer_key['{owner_id}'].criteria",
                f"criterion weights sum to {format_rational(total)} but {owner_id!r} is worth "
                f"{owner[0]} (§4.2.1): the parts must add up to the whole, exactly",
            )
