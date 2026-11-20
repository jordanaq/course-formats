"""Report integrity and the graded arithmetic (§6, §8 checks 10 and 15).

A report is checked against its bundle and its submission, never alone: an award means
nothing without the question it belongs to, and a total means nothing without the awards it
sums. Three arithmetics are decided here, and each has a counter-case that must be rejected:

    equal group   awarded == exact sum of the counted alternatives' awards
    capped group  awarded == min(sum, group.points), with `uncapped_awarded_points` present
                  exactly when the cap bound and absent otherwise
    everything else  criterion awards sum to `awarded_points`, and must not exceed the
                  question's `points` (§4.1's ceiling)

`uncapped_awarded_points` on a group whose cap did not bind is an `error`, not a warning: it
claims a cap was applied when the numbers say it was not, which is the one thing a report may
never do — misdescribe its own arithmetic.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Iterator

from .. import jsonview, rationals
from ..diagnostics import Diagnostic, error
from ..document import CHOICE_TYPES, Bundle, Question
from ..jsonview import JsonObject


def _awards(result: JsonObject) -> tuple[list[tuple[str | None, Fraction]], bool]:
    """Every criterion award of one result, with its alternative id, and whether all parsed."""
    scores = jsonview.get_array(result, "criterion_scores") or []
    awards: list[tuple[str | None, Fraction]] = []
    ok = True
    for item in scores:
        member = jsonview.as_object(item)
        if member is None:
            ok = False
            continue
        text = jsonview.get_str(member, "points_awarded")
        value = rationals.parse(text) if text is not None else None
        if value is None:
            ok = False
            continue
        awards.append((jsonview.get_str(member, "alternative_id"), value))
    return awards, ok


def structure(
    bundle: Bundle, submission: JsonObject, report: JsonObject
) -> Iterator[Diagnostic]:
    """Requires: the three documents are parsed objects.

    Ensures: an `error` when the report's `assessment_id` or `submission_id` does not match,
    when the result count differs from the question count, when results are not in question
    order, when a `max_points` differs from its question's `points`, when a graded result
    has no rational `awarded_points`, or when a group result's `answered_alternative_ids`
    and `ignored_alternative_ids` do not partition the answers in the paper's order.
    """
    assessment = bundle.assessment
    if assessment is None:
        return
    assessment_id = jsonview.get_str(assessment, "id")
    reported_id = jsonview.get_str(report, "assessment_id")
    if reported_id != assessment_id:
        yield error(
            "report",
            "$.assessment_id",
            f"report names assessment {reported_id!r} but the bundle is {assessment_id!r}; "
            f"every number below would be measured against the wrong paper (§6)",
        )
    submitted_id = jsonview.get_str(submission, "submission_id")
    reported_submission = jsonview.get_str(report, "submission_id")
    if submitted_id is not None and reported_submission != submitted_id:
        yield error(
            "report",
            "$.submission_id",
            f"report names submission {reported_submission!r} but the submission is "
            f"{submitted_id!r} (§6)",
        )

    questions = list(bundle.questions())
    results = jsonview.get_array(report, "results")
    if results is None:
        yield error("report", "$.results", "a report must carry a `results` array (§6)")
        return
    if len(results) != len(questions):
        yield error(
            "report",
            "$.results",
            f"{len(results)} results for {len(questions)} questions; a report carries one "
            f"result per question, in the paper's order (§6)",
        )

    for position, question in enumerate(questions):
        path = f"$.results[{position}]"
        if position >= len(results):
            yield error(
                "report",
                path,
                f"no result for question {question.id!r}; results must follow the paper's "
                f"order (§6)",
            )
            continue
        member = jsonview.as_object(results[position])
        if member is None:
            yield error("report", path, "a result must be an object (§6)")
            continue
        result_id = jsonview.get_str(member, "question_id")
        if result_id != question.id:
            yield error(
                "report",
                f"{path}.question_id",
                f"result {position} names {result_id!r} but question {position} is "
                f"{question.id!r}; results must follow the paper's order (§6)",
            )
            continue
        max_points = jsonview.get_str(member, "max_points")
        if max_points != question.points:
            yield error(
                "report",
                f"{path}.max_points",
                f"max_points {max_points!r} differs from the question's points "
                f"{question.points!r} (§6)",
            )
        if jsonview.get_str(member, "status") == "graded":
            awarded = jsonview.get_str(member, "awarded_points")
            if awarded is None or rationals.parse(awarded) is None:
                yield error(
                    "report",
                    f"{path}.awarded_points",
                    "a graded result must carry `awarded_points` as a canonical rational "
                    "string (§6)",
                )
        if question.is_group:
            yield from _group_ids(question, member, path)


def _group_ids(question: Question, result: JsonObject, path: str) -> Iterator[Diagnostic]:
    """The answered/ignored partition of a group result, judged against the group's alts."""
    known = {alternative.id for alternative in question.alternatives() if alternative.id}
    answered = jsonview.get_array(result, "answered_alternative_ids")
    answer_ids: list[str] = []
    if answered is not None:
        for position, item in enumerate(answered):
            text = jsonview.as_str(item)
            if text is None or text not in known:
                yield error(
                    "report",
                    f"{path}.answered_alternative_ids[{position}]",
                    f"{text!r} names no alternative of group {question.id!r} (§6)",
                )
                continue
            answer_ids.append(text)
    if len(set(answer_ids)) != len(answer_ids):
        yield error(
            "report",
            f"{path}.answered_alternative_ids",
            "an alternative is counted twice in one group result (§6)",
        )
    for position, item in enumerate(jsonview.get_array(result, "ignored_alternative_ids") or []):
        text = jsonview.as_str(item)
        if text is None or text not in known:
            yield error(
                "report",
                f"{path}.ignored_alternative_ids[{position}]",
                f"{text!r} names no alternative of group {question.id!r} (§6)",
            )
        elif text in answer_ids:
            yield error(
                "report",
                f"{path}.ignored_alternative_ids[{position}]",
                f"{text!r} is both answered and ignored (§6)",
            )
    choose_n = question.choose_n
    if choose_n is not None and len(answer_ids) > choose_n:
        yield error(
            "report",
            f"{path}.answered_alternative_ids",
            f"{len(answer_ids)} alternatives counted, but the group lets a student answer "
            f"{choose_n} (§2.4.5)",
        )


def arithmetic(
    bundle: Bundle, submission: JsonObject, report: JsonObject
) -> Iterator[Diagnostic]:
    """Requires: the three documents are parsed objects.

    Ensures: the three arithmetics above, exactly, in `Fraction`; `uncapped_awarded_points`
    present iff the cap bound; `total_possible_points` equal to the exact sum of question
    points; and `total_awarded_points` equal to the exact sum of the awards when every
    result is graded, `null` otherwise (§6).
    """
    questions = list(bundle.questions())
    results = jsonview.get_array(report, "results") or []

    possible = Fraction(0)
    for question in questions:
        value = question.points_value()
        if value is not None:
            possible += value
    stated_possible = jsonview.get_str(report, "total_possible_points")
    stated_value = rationals.parse(stated_possible) if stated_possible is not None else None
    if stated_value is None:
        yield error(
            "report",
            "$.total_possible_points",
            "a report must state `total_possible_points` as a canonical rational (§6)",
        )
    elif stated_value != possible:
        yield error(
            "report",
            "$.total_possible_points",
            f"total_possible_points is {rationals.format(stated_value)} but the questions "
            f"sum to {rationals.format(possible)} (§6)",
        )

    total = Fraction(0)
    all_graded = True
    for position, question in enumerate(questions):
        if position >= len(results):
            all_graded = False
            continue
        member = jsonview.as_object(results[position])
        if member is None:
            all_graded = False
            continue
        awarded_text = jsonview.get_str(member, "awarded_points")
        if jsonview.get_str(member, "status") != "graded" or awarded_text is None:
            all_graded = False
            continue
        awarded = rationals.parse(awarded_text)
        if awarded is None:
            all_graded = False
            continue
        total += awarded
        yield from _result_arithmetic(
            bundle, submission, question, member, f"$.results[{position}]", awarded
        )

    stated_total = report.get("total_awarded_points")
    if all_graded:
        text = jsonview.as_str(stated_total)
        value = rationals.parse(text) if text is not None else None
        if value is None or value != total:
            yield error(
                "report",
                "$.total_awarded_points",
                f"total_awarded_points is {text!r} but the results sum to "
                f"{rationals.format(total)} (§6)",
            )
    elif stated_total is not None:
        yield error(
            "report",
            "$.total_awarded_points",
            "total_awarded_points must be null while any result is ungraded: a total that "
            "excludes an ungraded question is not a total (§6)",
        )


def _choice_score(
    bundle: Bundle, question: Question, submission: JsonObject
) -> Fraction | None:
    """§3's score for a choice question, from the submission and the key.

    A choice question carries no rubric: its award is computed from the selected options, so
    a report for one legitimately has an empty `criterion_scores` array. Summing criteria
    there would report "0 awarded" for a perfectly graded item — the mistake this helper
    exists to prevent.
    """
    key = bundle.key_entry(question.id or "")
    if key is None:
        return None
    correct = jsonview.get_array(key, "correct_option_ids")
    options = jsonview.get_array(question.raw, "options")
    weight = question.points_value()
    if correct is None or options is None or weight is None:
        return None
    correct_ids = {text for text in (jsonview.as_str(c) for c in correct) if text is not None}
    all_ids = {
        text
        for text in (
            jsonview.get_str(jsonview.as_object(option) or {}, "id") for option in options
        )
        if text is not None
    }
    responses = jsonview.get_object(submission, "responses") or {}
    response = jsonview.get_object(responses, question.id or "") or {}
    selected = jsonview.get_array(response, "selected_option_ids") or []
    selected_ids = {text for text in (jsonview.as_str(s) for s in selected) if text is not None}
    if question.type == "single_choice":
        return weight if selected_ids == correct_ids else Fraction(0)
    policy = jsonview.get_str(question.raw, "scoring_policy")
    if policy == "all_or_nothing" or policy is None:
        return weight if selected_ids == correct_ids else Fraction(0)
    distractors = len(all_ids - correct_ids)
    if not correct_ids or distractors == 0:
        return None
    true_positive = len(selected_ids & correct_ids)
    false_positive = len(selected_ids - correct_ids)
    raw = Fraction(true_positive, len(correct_ids)) - Fraction(false_positive, distractors)
    return max(Fraction(0), weight * raw)


def _result_arithmetic(
    bundle: Bundle,
    submission: JsonObject,
    question: Question,
    result: JsonObject,
    path: str,
    awarded: Fraction,
) -> Iterator[Diagnostic]:
    """One result's award, judged against its question's credit rule."""
    weight = question.points_value()
    if weight is None:
        return
    if question.type in CHOICE_TYPES:
        total = _choice_score(bundle, question, submission)
        if total is None:
            return
        if awarded != total:
            yield error(
                "report",
                f"{path}.awarded_points",
                f"awarded_points is {rationals.format(awarded)} but §3's scoring of the "
                f"selected options gives {rationals.format(total)} (§6)",
            )
        return

    awards, parsed = _awards(result)
    if not parsed:
        yield error(
            "report",
            f"{path}.criterion_scores",
            "every criterion award must be a canonical rational string (§6)",
        )
        return
    summed = sum((value for _, value in awards), Fraction(0))

    if question.is_group and question.credit_mode == "capped":
        expected = min(summed, weight)
        recorded = result.get("uncapped_awarded_points")
        if summed > weight:
            text = jsonview.as_str(recorded)
            value = rationals.parse(text) if text is not None else None
            if value is None or value != summed:
                yield error(
                    "report",
                    f"{path}.uncapped_awarded_points",
                    f"the cap bound: the awards sum to {rationals.format(summed)} against a "
                    f"{rationals.format(weight)}-point ceiling, so the uncapped sum must be "
                    f"recorded as {rationals.format(summed)} (§6)",
                )
        elif recorded is not None:
            yield error(
                "report",
                f"{path}.uncapped_awarded_points",
                f"uncapped_awarded_points is recorded but the awards sum to "
                f"{rationals.format(summed)}, at or below the "
                f"{rationals.format(weight)}-point ceiling: no cap bound, so the field must "
                f"be absent (§6)",
            )
    else:
        expected = summed
        if "uncapped_awarded_points" in result:
            yield error(
                "report",
                f"{path}.uncapped_awarded_points",
                "uncapped_awarded_points only exists where a capped ceiling clipped the "
                "award; this question has no cap (§6)",
            )
        if summed > weight:
            yield error(
                "report",
                f"{path}.criterion_scores",
                f"criterion awards sum to {rationals.format(summed)}, above the question's "
                f"{rationals.format(weight)} points (§4.1)",
            )
            return

    if awarded != expected:
        yield error(
            "report",
            f"{path}.awarded_points",
            f"awarded_points is {rationals.format(awarded)} but the awards give "
            f"{rationals.format(expected)} (§6)",
        )


def _weight_of(bundle: Bundle, owner_id: str, criterion_id: str | None) -> Fraction | None:
    """Requires: `owner_id` names a key entry, possibly a group's alternative.

    Ensures: the weight that criterion declares, or `None` when the rubric is unweighted or
    the criterion cannot be found — an unweighted rubric has no bound to apply, and a missing
    criterion is `identity`'s finding, not this rule's (§4.2.1).
    """
    entry = bundle.key_entry(owner_id)
    if entry is None:
        return None
    criteria = jsonview.get_array(entry, "criteria")
    if criteria is None:
        return None
    for member in criteria:
        criterion = jsonview.as_object(member)
        if criterion is None:
            continue
        if jsonview.get_str(criterion, "id") != criterion_id:
            continue
        text = jsonview.get_str(criterion, "points")
        return rationals.parse(text) if text is not None else None
    return None


def criterion_weights(bundle: Bundle, report: JsonObject) -> Iterator[Diagnostic]:
    """Requires: the bundle and report are parsed objects.

    Ensures: an `error` per award that exceeds the weight its criterion declares (§4.2.1). A
    rubric that declares no weights yields nothing: silence is not a claim that the criteria
    are worth the same, and this rule must not invent a bound the document does not state.
    """
    results = jsonview.get_array(report, "results")
    if results is None:
        return
    for index, member in enumerate(results):
        result = jsonview.as_object(member)
        if result is None:
            continue
        question_id = jsonview.get_str(result, "question_id")
        if question_id is None:
            continue
        scores = jsonview.get_array(result, "criterion_scores")
        if scores is None:
            continue
        for position, item in enumerate(scores):
            score = jsonview.as_object(item)
            if score is None:
                continue
            criterion_id = jsonview.get_str(score, "criterion_id")
            alternative_id = jsonview.get_str(score, "alternative_id")
            owner = alternative_id if alternative_id is not None else question_id
            weight = _weight_of(bundle, owner, criterion_id)
            if weight is None:
                continue
            text = jsonview.get_str(score, "points_awarded")
            award = rationals.parse(text) if text is not None else None
            if award is None or award <= weight:
                continue
            yield error(
                "report",
                f"$.results[{index}].criterion_scores[{position}].points_awarded",
                f"award {rationals.format(award)} exceeds the weight {rationals.format(weight)} "
                f"declared by criterion {criterion_id!r} (§4.2.1): a weighted criterion is awarded "
                f"0 … its own share, and the parts were declared to add up to the question",
            )


def check(
    bundle: Bundle, submission: JsonObject, report: JsonObject
) -> Iterator[Diagnostic]:
    """Requires: the three documents are parsed objects.

    Ensures: `structure` then `arithmetic`. Empty when the triple is conforming.
    """
    yield from structure(bundle, submission, report)
    yield from criterion_weights(bundle, report)
    yield from arithmetic(bundle, submission, report)
