"""Project a 0.12.0 submission onto the two shapes the 0.11.x rules already understand.

Why this exists: from 0.12.0 the grading record lives *inside* the submission — feedback on
each answer, totals on the document — instead of in a separate report. The rules that check
that arithmetic (one criterion entry per criterion, counted alternatives, recomputed awards,
totals, word-limit records) were written against the 0.11.3 submission/report pair and are
correct; rewriting them would trade tested code for untested code. So a submission is
projected onto both old shapes and the same rules run:

    submission (responses[] of {question_id, response, feedback})
        → legacy submission: {"assessment_id", "submission_id", "responses": {id: response}}
        → report:            {"grading_status", "results": [...], "total_*", "process_notes"}

A projection is lossy by design and says so: fields with no 0.11.3 counterpart (`submitter`,
`attempt`, `submitted_at`, `paper`, `graders`, release flags) are not invented into the old
shape. A rule that needs them reads the submission itself.
"""
from __future__ import annotations

from .jsonview import JsonObject, as_array, get_object


def responses_array(submission: JsonObject) -> list[JsonObject]:
    """Requires: `submission` is a parsed submission document.

    Ensures: its `responses` entries in document order, objects only. An entry that is not an
    object is skipped here and reported by the schema pass, not by this function.
    """
    entries = as_array(submission.get("responses"))
    if entries is None:
        return []
    return [entry for entry in entries if isinstance(entry, dict)]


def legacy_submission(submission: JsonObject) -> JsonObject:
    """Requires: `submission` is a parsed submission document.

    Ensures: the 0.11.3 submission shape — `responses` keyed by question id — so the submission
    rules read it unchanged. A pool response passes through as it stands: its entries keyed by
    alternative id are already that shape.
    """
    keyed: JsonObject = {}
    for entry in responses_array(submission):
        question_id = entry.get("question_id")
        response = entry.get("response")
        if isinstance(question_id, str) and isinstance(response, dict):
            keyed[question_id] = response
    return {
        "format_version": submission.get("format_version"),
        "assessment_id": submission.get("assessment_id"),
        "submission_id": submission.get("submission_id"),
        "responses": keyed,
    }


def result(entry: JsonObject) -> JsonObject:
    """Requires: `entry` is one `responses[]` entry.

    Ensures: the 0.11.3 result shape for that entry, mapping the names the submission uses
    (`points_awarded` → `awarded_points`, `criteria` → `criterion_scores`) and carrying the
    group fields a rule may need. A missing feedback block projects to a graded result with
    null awards, which is what the rules check for.
    """
    block = get_object(entry, "feedback")
    feedback: JsonObject = block if block is not None else {}
    projected: JsonObject = {
        "question_id": entry.get("question_id"),
        "status": "needs_review" if feedback.get("review_reason") else "graded",
        "awarded_points": feedback.get("points_awarded"),
        "max_points": feedback.get("max_points"),
        "feedback": feedback.get("overall_feedback", ""),
        "criterion_scores": feedback.get("criteria", []),
        "review_reason": feedback.get("review_reason"),
    }
    for name in ("counted_alternative_ids", "ignored_alternative_ids", "uncapped_awarded_points"):
        if name in feedback:
            projected[name] = feedback[name]
    return projected


def as_report(submission: JsonObject) -> JsonObject:
    """Requires: `submission` is a parsed submission document.

    Ensures: the 0.11.3 report shape. `grading_status` is derived — `graded` exactly when
    `grading.complete` is true — so a half-marked submission cannot project to a complete
    report, and the totals are passed through, `null` included.
    """
    grading = get_object(submission, "grading")
    report: JsonObject = {
        "format_version": submission.get("format_version"),
        "assessment_id": submission.get("assessment_id"),
        "submission_id": submission.get("submission_id"),
        "grading_status": "graded" if (grading or {}).get("complete") is True else "needs_review",
        "results": [result(entry) for entry in responses_array(submission)],
    }
    for name in ("total_possible_points", "total_awarded_points", "process_notes"):
        if name in submission:
            report[name] = submission[name]
    return report
