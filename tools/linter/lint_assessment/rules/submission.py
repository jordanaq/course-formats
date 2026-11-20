"""Submission rules — §8 of the submission spec, minus the arithmetic.

The projection in `projection.py` covers the grading arithmetic (§8 check 7) by running the
rules that were already tested against a report. Everything here is what a *submission* has
and a report never did: who submitted it, which paper they sat, whether every question was
answered in the paper's order, whether the feedback block is well formed for its question
type, and whether the grading state and the grader audit are consistent.

Each function is total: it reads with the `jsonview` accessors, which return `None` rather
than raising, and reports what it finds. Nothing here decides that a document is too broken to
check further — a rule that stops at the first anomaly hides the other nine.

Checks that need something the linter does not have are named in the docstring rather than
half-implemented: the filename stem (check 1) and `(username, attempt)` uniqueness (check 5)
require the directory a document lives in, and `paper.sha256` (check 2) needs the bundle's
bytes — the caller passes them as `digest` when it has them.
"""
from __future__ import annotations

import hashlib
import re
from typing import Iterator

from ..diagnostics import Diagnostic, error, warning
from ..document import Bundle
from ..jsonview import JsonObject, as_object, as_str, get_array, get_object, get_str

#: `submission_id` — a username, a hyphen, and the UTC instant with its separators stripped.
SUBMISSION_ID = re.compile(r"^[A-Za-z0-9._-]{2,64}-\d{8}T\d{6}Z$")
#: An ISO 8601 instant in UTC, to the second, as every timestamp in the format is written.
TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")

WRITTEN = ("short_answer", "essay")
CHOICE = ("single_choice", "multiple_select")
ROLES = ("primary", "reviewer", "approver")
#: The one field pair that must never appear in feedback: a locator is where the answer lives.
LOCATOR_KEYS = ("locator", "locators", "location", "positions")


def _questions(bundle: Bundle) -> list[tuple[str | None, str | None]]:
    """Requires: `bundle` is a parsed bundle.

    Ensures: `(id, type)` for every question in document order — the order check 3 requires.
    """
    return [(question.id, question.type) for question in bundle.questions()]


def _entries(submission: JsonObject) -> list[JsonObject]:
    """Requires: `submission` is a parsed document.

    Ensures: its `responses` entries that are objects, in order. A non-object entry is the
    schema's finding, not this module's.
    """
    value = get_array(submission, "responses")
    if value is None:
        return []
    return [entry for entry in (as_object(item) for item in value) if entry is not None]


def identity(bundle: Bundle, submission: JsonObject) -> Iterator[Diagnostic]:
    """Requires: both documents are parsed.

    Ensures: check 1 and the parts of check 5 that live inside the document — the id matches
    the bundle, the id is well formed, `submitted_at` agrees with it, and the submitter and
    attempt are usable. The *filename stem* equality is not checkable here: the linter is
    handed a document, not a path.
    """
    assessment = bundle.assessment or {}
    bundle_id = get_str(assessment, "id")
    submission_id = get_str(submission, "assessment_id")
    if bundle_id is not None and submission_id != bundle_id:
        yield error(
            "submission",
            "$.assessment_id",
            f"names {submission_id!r} but the bundle is {bundle_id!r}; every award in this "
            f"document would be measured against the wrong paper",
        )

    identifier = get_str(submission, "submission_id")
    if identifier is None:
        yield error("submission", "$.submission_id", "a submission must carry an id")
    elif not SUBMISSION_ID.match(identifier):
        yield error(
            "submission",
            "$.submission_id",
            f"{identifier!r} is not a username, a hyphen and a UTC instant "
            f"(<username>-YYYYMMDDTHHMMSSZ)",
        )

    submitted_at = get_str(submission, "submitted_at")
    if submitted_at is None:
        yield error("submission", "$.submitted_at", "a submission must record when it was sent")
    elif TIMESTAMP.match(submitted_at) is None:
        yield error(
            "submission",
            "$.submitted_at",
            f"{submitted_at!r} is not an ISO 8601 UTC instant to the second "
            f"(YYYY-MM-DDTHH:MM:SSZ)",
        )
    elif identifier is not None and SUBMISSION_ID.match(identifier):
        stamped = identifier.rsplit("-", 1)[-1][:-1]
        digits = submitted_at.replace("-", "").replace(":", "").rstrip("Z").replace("T", "T")
        if stamped != digits:
            yield error(
                "submission",
                "$.submitted_at",
                f"{submitted_at!r} is not the instant in the id ({identifier!r}): the id is "
                f"derived from this field, so the two cannot disagree",
            )

    submitter = get_object(submission, "submitter")
    if submitter is None:
        yield error("submission", "$.submitter", "a submission must name who sent it")
    else:
        for field in ("name", "username"):
            value = get_str(submitter, field)
            if value is None or not value.strip():
                yield error(
                    "submission", f"$.submitter.{field}", f"{field} must be a nonempty string"
                )
        username = get_str(submitter, "username")
        if username is not None and any(character.isspace() for character in username):
            yield error(
                "submission",
                "$.submitter.username",
                f"{username!r} contains whitespace; a username is one token, because it also "
                f"appears in the submission id and the filename",
            )

    attempt = submission.get("attempt")
    if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
        yield error("submission", "$.attempt", "attempt must be an integer of at least 1")


def paper(submission: JsonObject, digest: str | None = None) -> Iterator[Diagnostic]:
    """Requires: `submission` is parsed; `digest` is the bundle's sha256 hex when the caller
    has its bytes.

    Ensures: check 2 — the commit is a 40-hex sha or `"uncommitted"`, the path is
    vault-relative, the digest is 64 hex, and a digest mismatch is a **warning**: a paper
    corrected after this submission is legal and worth seeing.
    """
    block = get_object(submission, "paper")
    if block is None:
        yield error("submission", "$.paper", "a submission must pin the paper it sat")
        return

    commit = get_str(block, "commit")
    if commit is None:
        yield error("submission", "$.paper.commit", "the commit of the paper is required")
    elif commit != "uncommitted" and COMMIT.match(commit) is None:
        yield error(
            "submission",
            "$.paper.commit",
            f"{commit!r} is neither a 40-character commit sha nor \"uncommitted\"",
        )

    path = get_str(block, "path")
    if path is None or not path.strip():
        yield error("submission", "$.paper.path", "the paper's path is required")
    elif path.startswith("/") or ".." in path.split("/"):
        yield error(
            "submission",
            "$.paper.path",
            f"{path!r} must be vault-relative: an absolute path or a parent hop names a file "
            f"outside the vault",
        )

    stated = get_str(block, "sha256")
    if stated is None:
        yield error("submission", "$.paper.sha256", "the paper's digest is required")
    elif DIGEST.match(stated) is None:
        yield error(
            "submission", "$.paper.sha256", f"{stated!r} is not a lowercase sha256 hex digest"
        )
    elif digest is not None and stated != digest and commit != "uncommitted":
        yield warning(
            "submission",
            "$.paper.sha256",
            f"the paper has changed since this submission: it recorded {stated[:12]}…, the "
            f"bundle now hashes to {digest[:12]}…",
        )


def coverage(bundle: Bundle, submission: JsonObject) -> Iterator[Diagnostic]:
    """Requires: both documents are parsed.

    Ensures: check 3 — exactly one entry per question, ids equal in both directions, and the
    order equal to the paper's. Order is checked because a submission is a mirror: a reader
    comparing it with the paper should not have to look up ids.
    """
    expected = [question_id for question_id, _ in _questions(bundle)]
    entries = _entries(submission)
    seen: list[str | None] = [get_str(entry, "question_id") for entry in entries]

    for index, question_id in enumerate(seen):
        if question_id is None:
            yield error(
                "submission", f"$.responses[{index}].question_id", "an entry must name its question"
            )
        elif question_id not in expected:
            yield error(
                "submission",
                f"$.responses[{index}].question_id",
                f"{question_id!r} is not a question of this paper",
            )
    for question_id in expected:
        if question_id is not None and question_id not in seen:
            yield error(
                "submission",
                "$.responses",
                f"no entry for {question_id!r}: a submission answers every question, and an "
                f"omitted entry is not the same as an unanswered one",
            )
    duplicates = {question_id for question_id in seen if seen.count(question_id) > 1}
    for question_id in sorted(str(item) for item in duplicates if item is not None):
        yield error("submission", "$.responses", f"{question_id!r} is answered more than once")

    common = [question_id for question_id in seen if question_id in expected]
    expected_common = [item for item in expected if item in common]
    for index, (have, want) in enumerate(zip(common, expected_common)):
        if have != want:
            yield error(
                "submission",
                f"$.responses[{index}].question_id",
                f"entries leave paper order here: expected {want!r}, found {have!r}",
            )
            break


def response_shapes(bundle: Bundle, submission: JsonObject) -> Iterator[Diagnostic]:
    """Requires: both documents are parsed.

    Ensures: check 4 — a response's shape matches its question's type, a single-choice question
    holds at most one id, and every id named is one the question or group declares. An absent
    response is legal (unanswered) and silent here; the award rules give it zero.
    """
    kinds = {question_id: kind for question_id, kind in _questions(bundle)}
    options: dict[str | None, set[str]] = {}
    for question in bundle.questions():
        declared: set[str] = set()
        for item in get_array(question.raw, "options") or []:
            option = as_object(item)
            if option is None:
                continue
            option_id = get_str(option, "id")
            if option_id is not None:
                declared.add(option_id)
        options[question.id] = declared
    alternatives = {
        question.id: {
            alternative.id
            for alternative in question.alternatives()
            if alternative.id is not None
        }
        for question in bundle.questions()
    }

    for index, entry in enumerate(_entries(submission)):
        question_id = get_str(entry, "question_id")
        if question_id is None or question_id not in kinds:
            continue
        kind = kinds[question_id]
        response = entry.get("response")
        if response is None:
            continue
        block = as_object(response)
        path = f"$.responses[{index}].response"
        if block is None:
            yield error("submission", path, f"{kind} answers an object, not a JSON scalar")
            continue
        if kind in CHOICE:
            selected = get_array(block, "selected_option_ids")
            if selected is None:
                yield error(
                    "submission",
                    f"{path}.selected_option_ids",
                    f"a {kind} response is {{ \"selected_option_ids\": [...] }}",
                )
                continue
            if kind == "single_choice" and len(selected) > 1:
                yield error(
                    "submission",
                    f"{path}.selected_option_ids",
                    f"{len(selected)} ids selected; a single_choice question takes at most one",
                )
            for position, value in enumerate(selected):
                option_id = as_str(value)
                if option_id is None:
                    yield error(
                        "submission",
                        f"{path}.selected_option_ids[{position}]",
                        "an option id must be a string",
                    )
                elif option_id not in options.get(question_id, set()):
                    yield error(
                        "submission",
                        f"{path}.selected_option_ids[{position}]",
                        f"{option_id!r} is not an option of {question_id!r}",
                    )
        elif kind in WRITTEN:
            if get_str(block, "text") is None:
                yield error(
                    "submission",
                    f"{path}.text",
                    f"a {kind} response is {{ \"text\": \"…\" }}",
                )
        elif kind == "alternative_set":
            known = alternatives.get(question_id, set())
            for key, value in block.items():
                if key not in known:
                    yield error(
                        "submission",
                        f"{path}.{key}",
                        f"{key!r} is not an alternative of {question_id!r}",
                    )
                elif as_object(value) is None:
                    yield error(
                        "submission",
                        f"{path}.{key}",
                        "an alternative's response is an object of its own",
                    )


def _feedback_block(
    entry: JsonObject, index: int, kind: str | None
) -> tuple[JsonObject | None, list[Diagnostic]]:
    """Requires: `entry` is one `responses` element.

    Ensures: its feedback block, plus the diagnostics that keep it from being inspected
    further (a locator, a wrong-typed flag). One function rather than ten guards, because the
    block is read the same way for every rule.
    """
    out: list[Diagnostic] = []
    feedback = get_object(entry, "feedback")
    if feedback is None:
        return None, out
    path = f"$.responses[{index}].feedback"

    for key in LOCATOR_KEYS:
        if key in feedback:
            out.append(
                error(
                    "submission",
                    f"{path}.{key}",
                    f"feedback may not carry {key!r}: a locator names where the answer lives, "
                    f"which is the answer. Locators stay in the bundle's answer key",
                )
            )
    for flag in ("released", "include_reference_answer"):
        if not isinstance(feedback.get(flag), bool):
            out.append(error("submission", f"{path}.{flag}", f"{flag} must be a boolean"))

    award = feedback.get("points_awarded")
    review = feedback.get("review_reason")
    if award is None:
        if not (isinstance(review, str) and review.strip()):
            out.append(
                error(
                    "submission",
                    f"{path}.review_reason",
                    "a question with no award must say why in review_reason",
                )
            )
    elif review is not None:
        if not isinstance(review, str):
            out.append(
                error("submission", f"{path}.review_reason", "review_reason is a string or null")
            )
        elif review.strip():
            out.append(
                error(
                    "submission",
                    f"{path}.review_reason",
                    "a question with an award exists is not awaiting review; review_reason "
                    "belongs to the questions that have none",
                )
            )

    overall = feedback.get("overall_feedback")
    if overall is not None:
        if not isinstance(overall, str) or not overall.strip():
            out.append(
                error(
                    "submission",
                    f"{path}.overall_feedback",
                    "overall_feedback must be a nonempty string when present",
                )
            )

    criteria = feedback.get("criteria")
    if criteria is not None:
        items = get_array(feedback, "criteria") or []
        if kind == "alternative_set" and items:
            # a counted pool is graded per criterion, and each criterion belongs to the
            # alternative it was earned on — an ignored alternative is never graded
            counted = get_array(feedback, "counted_alternative_ids") or []
            counted_ids = {as_str(value) for value in counted}
            for position, value in enumerate(items):
                scoped = as_object(value)
                if scoped is None:
                    continue
                alternative_id = get_str(scoped, "alternative_id")
                if alternative_id is not None and alternative_id not in counted_ids:
                    out.append(
                        error(
                            "submission",
                            f"{path}.criteria[{position}].alternative_id",
                            f"{alternative_id!r} is not among the counted alternatives; an "
                            f"ignored alternative is never graded",
                        )
                    )
        if kind in WRITTEN and award is not None and not items:
            out.append(
                error(
                    "submission",
                    f"{path}.criteria",
                    "a graded written question carries one entry per rubric criterion",
                )
            )
        for position, value in enumerate(items):
            criterion = as_object(value)
            if criterion is None:
                out.append(
                    error(
                        "submission",
                        f"{path}.criteria[{position}]",
                        "a criterion entry is an object",
                    )
                )
            else:
                for key in LOCATOR_KEYS:
                    if key in criterion:
                        out.append(
                            error(
                                "submission",
                                f"{path}.criteria[{position}].{key}",
                                f"a criterion's feedback may not carry {key!r} either: a locator "
                                f"names where the answer lives",
                            )
                        )
            if isinstance(criterion, dict) and "released" in criterion and not isinstance(criterion["released"], bool):
                out.append(
                    error(
                        "submission",
                        f"{path}.criteria[{position}].released",
                        "a criterion's released is a boolean when present",
                    )
                )
    return feedback, out


def feedback(bundle: Bundle, submission: JsonObject) -> Iterator[Diagnostic]:
    """Requires: both documents are parsed.

    Ensures: check 6 and the parts of check 8 that are per question — feedback is all or
    nothing, each block is well formed for its question's type, and a review reason sits on
    exactly the questions without an award. The arithmetic is not repeated here: `projection`
    runs the report rules for that (§8 check 7).
    """
    entries = _entries(submission)
    carrying = [
        index for index, entry in enumerate(entries) if get_object(entry, "feedback") is not None
    ]
    if carrying and len(carrying) != len(entries):
        missing = [
            get_str(entry, "question_id") or f"responses[{index}]"
            for index, entry in enumerate(entries)
            if index not in carrying
        ]
        yield error(
            "submission",
            "$.responses",
            f"feedback is all or nothing per document; these questions carry none: "
            f"{', '.join(str(item) for item in missing)}",
        )
        return

    kinds = {question_id: kind for question_id, kind in _questions(bundle)}
    for index, entry in enumerate(entries):
        kind = kinds.get(get_str(entry, "question_id") or "")
        _, diagnostics = _feedback_block(entry, index, kind)
        yield from diagnostics


def grading_state(submission: JsonObject) -> Iterator[Diagnostic]:
    """Requires: `submission` is parsed.

    Ensures: check 9 — `complete: true` requires feedback everywhere, no question awaiting
    review, `completed_at` and both totals; `approved: true` requires `approved_at` and
    `approved_by`. `complete: false` is legal with partial feedback, which is the state while
    marking is in progress.
    """
    grading = get_object(submission, "grading")
    if grading is None:
        return
    complete = grading.get("complete")
    if not isinstance(complete, bool):
        yield error("submission", "$.grading.complete", "complete must be a boolean")

    completed_at = get_str(grading, "completed_at")
    if completed_at is not None and TIMESTAMP.match(completed_at) is None:
        yield error(
            "submission",
            "$.grading.completed_at",
            f"{completed_at!r} is not an ISO 8601 UTC instant to the second",
        )

    if complete is True:
        unmarked = [
            get_str(entry, "question_id") or f"responses[{index}]"
            for index, entry in enumerate(_entries(submission))
            if get_object(entry, "feedback") is None
        ]
        if unmarked:
            yield error(
                "submission",
                "$.grading.complete",
                f"complete is true but these questions carry no feedback: "
                f"{', '.join(str(item) for item in unmarked)}",
            )
        if completed_at is None:
            yield error(
                "submission",
                "$.grading.completed_at",
                "a complete grading records when it completed",
            )
        for field in ("total_possible_points", "total_awarded_points"):
            if not isinstance(submission.get(field), str):
                yield error(
                    "submission",
                    f"$.{field}",
                    f"a complete grading states {field} as a canonical rational",
                )
        for entry in _entries(submission):
            block = get_object(entry, "feedback")
            if block is None:
                continue
            reason = block.get("review_reason")
            awaiting = (
                block.get("points_awarded") is None
                and isinstance(reason, str)
                and bool(reason.strip())
            )
            # a reason on an *awarded* question is the feedback rule's finding; this one is
            # about the state, and reporting the other defect twice would double a diagnostic
            if awaiting:
                yield error(
                    "submission",
                    "$.grading.complete",
                    f"complete is true but {get_str(entry, 'question_id')!r} is awaiting review: "
                    f"{reason}",
                )

    approved = grading.get("approved")
    if approved is not None and not isinstance(approved, bool):
        yield error("submission", "$.grading.approved", "approved must be a boolean")
    if approved is True:
        for field in ("approved_at", "approved_by"):
            value = get_str(grading, field)
            if value is None or not value.strip():
                yield error(
                    "submission",
                    f"$.grading.{field}",
                    f"approved is true, so {field} is required",
                )
        approved_at = get_str(grading, "approved_at")
        if approved_at is not None and TIMESTAMP.match(approved_at) is None:
            yield error(
                "submission",
                "$.grading.approved_at",
                f"{approved_at!r} is not an ISO 8601 UTC instant to the second",
            )


def graders(submission: JsonObject) -> Iterator[Diagnostic]:
    """Requires: `submission` is parsed.

    Ensures: check 10 — every entry names a grader, a known role and a parseable instant; at
    most one `primary`; and the entries are in non-decreasing time order, because the array is
    the audit trail and an audit trail that reorders is not one.
    """
    value = get_array(submission, "graders")
    if value is None:
        return
    previous: str | None = None
    primaries = 0
    for index, item in enumerate(value):
        path = f"$.graders[{index}]"
        entry = as_object(item)
        if entry is None:
            yield error("submission", path, "a graders entry is an object")
            continue
        username = get_str(entry, "username")
        if username is None or not username.strip():
            yield error("submission", f"{path}.username", "every graders entry names a grader")
        role = get_str(entry, "role")
        if role is None:
            yield error("submission", f"{path}.role", "every graders entry states a role")
        elif role not in ROLES:
            yield error(
                "submission", f"{path}.role", f"{role!r} is not one of {', '.join(ROLES)}"
            )
        elif role == "primary":
            primaries += 1
        at = get_str(entry, "at")
        if at is None or TIMESTAMP.match(at) is None:
            yield error(
                "submission", f"{path}.at", "every graders entry records an ISO 8601 UTC instant"
            )
        elif previous is not None and at < previous:
            yield error(
                "submission",
                f"{path}.at",
                f"{at!r} is earlier than the entry before it ({previous!r}); the audit trail "
                f"is in time order",
            )
        if at is not None and TIMESTAMP.match(at):
            previous = at
    if primaries > 1:
        yield error(
            "submission", "$.graders", f"{primaries} entries claim the primary role; one does"
        )


def check(
    bundle: Bundle, submission: JsonObject, digest: str | None = None
) -> Iterator[Diagnostic]:
    """Requires: both documents are parsed; `digest` is the bundle's sha256 when known.

    Ensures: every submission rule, in the order the spec states them, one diagnostic per
    violation and none for a conforming document.
    """
    yield from identity(bundle, submission)
    yield from paper(submission, digest)
    yield from coverage(bundle, submission)
    yield from response_shapes(bundle, submission)
    yield from feedback(bundle, submission)
    yield from grading_state(submission)
    yield from graders(submission)


def digest_of(text: str) -> str:
    """Requires: `text` is the bundle file's decoded contents.

    Ensures: its sha256 hex. Re-encoding UTF-8 after decoding reproduces the file's bytes for
    any document that parsed, which is the only time this is called.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
