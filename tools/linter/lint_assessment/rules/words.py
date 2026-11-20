"""Response limits and delivery mode (§2.2.1, §2.8) — the two student-visible declarations.

Both exist because a student must be told: a paper's delivery mode, and a written question's
word range with what the range does. The linter's job for each is the same — the field is
legal, the pairing is complete, and the default that absence implies is the one §2.8 defines.
"""
from __future__ import annotations

from typing import Iterator

from .. import jsonview
from ..diagnostics import Diagnostic, error
from ..document import CHOICE_TYPES, Bundle

#: §2.2.1's enforcement vocabulary.
ENFORCEMENTS: frozenset[str] = frozenset({"advisory", "recorded", "capped"})
#: §2.8's delivery vocabulary.
DELIVERIES: frozenset[str] = frozenset({"open_book", "closed_book"})


def word_limits(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing.

    Ensures: for every `suggested_word_count`: an `error` when it is not an object, when
    `min` or `max` is not a positive integer, when `min > max`, when `enforcement` is
    outside the vocabulary, or when a non-`advisory` enforcement carries no nonempty
    `note` (§8 check 14). An `error` also when the field appears on a choice question or on
    a group, which have no written response to limit.
    """
    for section in bundle.sections():
        for question in section.questions():
            limit = question.raw.get("suggested_word_count")
            path = f"{question.path}.suggested_word_count"
            if limit is None:
                continue
            if question.is_group or question.type in CHOICE_TYPES:
                yield error(
                    "words",
                    path,
                    "suggested_word_count applies to a written response; this question is "
                    "neither a short_answer nor an essay (§2.2.1)",
                )
                continue
            body = jsonview.as_object(limit)
            if body is None:
                yield error("words", path, "suggested_word_count must be an object (§2.2.1)")
                continue
            low = jsonview.get_int(body, "min")
            high = jsonview.get_int(body, "max")
            if low is None or low < 1:
                yield error(
                    "words", f"{path}.min", "min must be a positive integer (§2.2.1)"
                )
            if high is None or high < 1:
                yield error(
                    "words", f"{path}.max", "max must be a positive integer (§2.2.1)"
                )
            if low is not None and high is not None and low > high:
                yield error(
                    "words",
                    f"{path}.max",
                    f"max {high} is below min {low}: the range is empty (§8 check 14)",
                )
            enforcement = jsonview.get_str(body, "enforcement")
            if "enforcement" in body:
                if enforcement is None or enforcement not in ENFORCEMENTS:
                    yield error(
                        "words",
                        f"{path}.enforcement",
                        f"enforcement {enforcement!r} is not one of "
                        f"{sorted(ENFORCEMENTS)} (§2.2.1)",
                    )
                elif enforcement != "advisory" and not (
                    jsonview.get_str(body, "note") or ""
                ).strip():
                    yield error(
                        "words",
                        f"{path}.note",
                        f"enforcement {enforcement!r} changes what a marker does, so it must "
                        f"carry a nonempty note telling the student what (§2.2.1)",
                    )


def delivery(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing.

    Ensures: an `error` when `delivery` is present but not an object, or its `mode` is
    absent or outside `open_book | closed_book`. Says nothing at all when `delivery` is
    absent — absence means `closed_book` (§2.8) and is a legal, deliberate declaration, so
    warning about it would punish the corpus's own convention.
    """
    assessment = bundle.assessment
    if assessment is None:
        return
    if "delivery" not in assessment:
        return
    delivery_block = jsonview.get_object(assessment, "delivery")
    if delivery_block is None:
        yield error(
            "delivery",
            "$.assessment.delivery",
            "delivery must be an object carrying `mode` (§2.8)",
        )
        return
    mode = jsonview.get_str(delivery_block, "mode")
    if mode is None or mode not in DELIVERIES:
        yield error(
            "delivery",
            "$.assessment.delivery.mode",
            f"delivery mode {mode!r} is not one of {sorted(DELIVERIES)} (§2.8)",
        )


def check(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing. Ensures: `word_limits` then `delivery`."""
    yield from word_limits(bundle)
    yield from delivery(bundle)
