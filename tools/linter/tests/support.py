"""Document builders for the tests.

Tests construct documents literally rather than loading fixtures, so that a test states the
shape it is testing and a failure names a shape rather than a filename. The E2E test is the
one exception: it uses the translated key, because the point there *is* a real document.
"""
from __future__ import annotations

import os
from typing import Any


#: The version the documents under test declare — read from the newest spec, never pinned.
#: A literal here goes stale on every spec bump and looks like a rule regression.
def _version() -> str:
    from lint_assessment.spec import (
        latest_spec, latest_submission_spec, load_schemas, read_text,
    )

    design = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    bundle_path = latest_spec(design)
    submission_path = latest_submission_spec(design)
    bundle_text = read_text(bundle_path) if bundle_path is not None else None
    submission_text = read_text(submission_path) if submission_path is not None else None
    if bundle_text is None or submission_text is None:
        return "unknown"
    schemas = load_schemas(bundle_text, submission_text)
    return schemas.version if schemas is not None else "unknown"


VERSION = _version()


def question(qid: str, points: str = "5", qtype: str = "short_answer") -> dict[str, Any]:
    """A minimal conforming written question."""
    return {
        "id": qid,
        "type": qtype,
        "prompt": "p",
        "points": points,
        "estimated_minutes": 1,
        "response_lines": 3,
    }


def group(
    qid: str = "qg",
    points: str = "5",
    choose_n: int = 3,
    alternatives: tuple[str, ...] = ("2", "2", "2", "2"),
    credit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """A group whose alternatives carry the given point strings."""
    q: dict[str, Any] = {
        "id": qid,
        "type": "alternative_set",
        "prompt": "Answer some.",
        "points": points,
        "choose_n": choose_n,
        "estimated_minutes": 1,
        "alternatives": [
            {
                "id": f"{qid}_a{i}",
                "type": "short_answer",
                "prompt": "p",
                "points": p,
                "estimated_minutes": 1,
                "response_lines": 2,
            }
            for i, p in enumerate(alternatives, 1)
        ],
    }
    if credit is not None:
        q["credit"] = credit
    return q


def key_for(ids: tuple[str, ...]) -> dict[str, Any]:
    """An analytic_rubric key entry for each id, with one criterion each."""
    return {
        i: {
            "method": "analytic_rubric",
            "reference_answer": "r",
            "criteria": [{"id": f"{i}_c1", "description": "d"}],
        }
        for i in ids
    }


def bundle(questions: list[dict[str, Any]], key: dict[str, Any]) -> dict[str, Any]:
    """A minimal bundle holding the given questions in one section."""
    return {
        "format_version": VERSION,
        "assessment": {
            "id": "t",
            "title": "t",
            "subject": "t",
            "audience": "t",
            "instructions": "t",
            "time_limit_minutes": 30,
            "sections": [
                {"id": "s1", "title": "t", "instructions": "i", "questions": questions}
            ],
        },
        "answer_key": key,
    }
