"""Points, types and option shapes (§2.3, §2.4, §8 checks 1 and 2).

Every point value in a bundle is a canonical rational string; a question's type decides
which other fields it must and must not carry; a choice question's options are a list of
objects with unique ids. These are shape facts a JSON Schema partly covers, so this rule
duplicates the schema deliberately: a linter that only runs the schema cannot say *why* a
document is non-conforming, and its diagnostics are unreadable to a person fixing a key.
"""
from __future__ import annotations

from typing import Iterator

from .. import jsonview, rationals
from ..diagnostics import Diagnostic, error
from ..document import CHOICE_TYPES, WRITTEN_TYPES, Bundle

#: Question types §2.2 defines. A type outside this set is an error, never ignored.
QUESTION_TYPES: frozenset[str] = frozenset(
    {"single_choice", "multiple_select", "short_answer", "essay", "alternative_set"}
)


def _option_ids(raw: jsonview.JsonObject, path: str) -> list[str] | None:
    """The option ids of a choice question, or `None` when `options` is unusable."""
    options = jsonview.get_array(raw, "options")
    if options is None:
        return None
    ids: list[str] = []
    for item in options:
        member = jsonview.as_object(item)
        if member is None:
            return None
        option_id = jsonview.get_str(member, "id")
        if option_id is None:
            return None
        ids.append(option_id)
    return ids


def question_shapes(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing.

    Ensures: an `error` per question with an unknown or missing `type`, each question that
    is not an object (addressed by index), and each group whose `choose_n` is not an
    integer in `1 … len(alternatives)` (§2.4.5), or that has fewer than two alternatives.
    A document with a malformed question yields at most one diagnostic per defect — not
    one per rule that happens to touch it.
    """
    for section in bundle.sections():
        items = jsonview.get_array(section.raw, "questions") or []
        for index, item in enumerate(items):
            path = f"{section.path}.questions[{index}]"
            raw = jsonview.as_object(item)
            if raw is None:
                yield error("points", path, "a question must be a JSON object (§2.2)")
                continue
            question_type = jsonview.get_str(raw, "type")
            if question_type is None:
                yield error("points", f"{path}.type", "a question must declare `type` (§2.2)")
                continue
            if question_type not in QUESTION_TYPES:
                yield error(
                    "points",
                    f"{path}.type",
                    f"question type {question_type!r} is not one of "
                    f"{sorted(QUESTION_TYPES)} (§2.2)",
                )
                continue
            if question_type != "alternative_set":
                continue
            alternatives = jsonview.get_array(raw, "alternatives")
            if alternatives is None or len(alternatives) < 2:
                yield error(
                    "points",
                    f"{path}.alternatives",
                    "an alternative_set needs at least two alternatives (§2.4.5)",
                )
                continue
            choose_n = jsonview.get_int(raw, "choose_n")
            if choose_n is None or not 1 <= choose_n <= len(alternatives):
                yield error(
                    "points",
                    f"{path}.choose_n",
                    f"choose_n must be an integer in 1..{len(alternatives)} (§2.4.5)",
                )


def _points_errors(raw: jsonview.JsonObject, path: str, owner: str) -> Iterator[Diagnostic]:
    """The `points` member, judged once, for one question or alternative."""
    text = jsonview.get_str(raw, "points")
    if text is None:
        yield error(
            "points",
            f"{path}.points",
            f"{owner} must carry `points` as a canonical rational string (§2.3.1)",
        )
        return
    value = rationals.parse(text)
    if value is None:
        yield error(
            "points",
            f"{path}.points",
            f"points {text!r} is not a canonical rational string — expected \"0\", a bare "
            f"positive integer, or n/d in lowest terms (§2.3.1)",
        )
        return
    if value <= 0:
        yield error(
            "points",
            f"{path}.points",
            f"points {text} must be positive; only a report may record a zero award "
            f"(§2.3.1)",
        )


def point_values(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing.

    Ensures: an `error` for every `points` that is absent, not a string, non-canonical, or
    zero-or-negative where the spec requires a positive value; for a written question that
    carries no `response_lines` when the type demands one; and for a choice question whose
    `options` is absent, empty, or has duplicate option ids.
    """
    for section in bundle.sections():
        for question in section.questions():
            question_id = question.id or question.path
            yield from _points_errors(question.raw, question.path, f"question {question_id!r}")

            question_type = question.type
            if question_type in WRITTEN_TYPES:
                lines = jsonview.get_int(question.raw, "response_lines")
                if lines is None or lines < 1:
                    yield error(
                        "points",
                        f"{question.path}.response_lines",
                        f"a {question_type} question must carry `response_lines` as a "
                        f"positive integer (§2.2)",
                    )
            elif question_type in CHOICE_TYPES:
                ids = _option_ids(question.raw, question.path)
                if ids is None or not ids:
                    yield error(
                        "points",
                        f"{question.path}.options",
                        f"a {question_type} question must carry `options` as objects with "
                        f"string ids (§2.2)",
                    )
                elif len(set(ids)) != len(ids):
                    yield error(
                        "points",
                        f"{question.path}.options",
                        "option ids must be unique within a question (§2.4.1)",
                    )
            elif question_type == "alternative_set":
                for alternative in question.alternatives():
                    yield from _points_errors(
                        alternative.raw,
                        alternative.path,
                        f"alternative {alternative.id!r}",
                    )


def check(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing. Ensures: `question_shapes` then `point_values`."""
    yield from question_shapes(bundle)
    yield from point_values(bundle)
