#!/usr/bin/env python3
"""Validate this fixture set against the current specs.

From 0.12.0 a graded assessment is **two** documents, not three: the bundle, and the submission
that carries its own feedback. So the layers here are:

  a) the bundle schema, from the newest `assessment-format-spec-v*.md`;
  b) the submission schema, from the newest `submission-format-spec-v*.md` — the assessment spec
     deliberately no longer defines a submission, and validating one against it would be
     validating against a shape the current spec does not contain;
  c) both schemas' `format_version` consts must agree with each other and with both documents;
  d) each graded answer's criterion awards must sum to its `points_awarded`, and the per-question
     awards must sum to `total_awarded_points` — the arithmetic §8 states, checked here on the
     fixture bytes rather than through the linter, so a disagreement names this file.

The semantic rules themselves (§8 of the assessment spec, §11 of the submission spec) are the
linter's job: `python3 -m lint_assessment bundle.json --submission submission.json`.

Read-only: nothing is written. Exit code 0 iff every layer is clean.
"""
from __future__ import annotations

import json
import os
import re
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = "/home/tsiru/Documents/Obsidian-Vault"
DESIGN = os.path.join(VAULT, "Agents/Design")
BLOCK = re.compile(r"```json\n(.*?)\n```", re.S)
BUNDLE_SPEC = re.compile(r"assessment-format-spec-v(\d+)\.(\d+)(?:\.(\d+))?\.md$")
SUBMISSION_SPEC = re.compile(r"submission-format-spec-v(\d+)\.(\d+)(?:\.(\d+))?\.md$")


def newest(pattern: re.Pattern[str]) -> str:
    """The newest spec matching `pattern`, compared as numeric version components."""
    best: tuple[tuple[int, ...], str] | None = None
    for name in os.listdir(DESIGN):
        match = pattern.match(name)
        if match is None:
            continue
        version = tuple(int(part) if part else 0 for part in match.groups())
        if best is None or version > best[0]:
            best = (version, os.path.join(DESIGN, name))
    if best is None:
        raise SystemExit(f"no spec matching {pattern.pattern} in {DESIGN}")
    return best[1]


def extract(path: str) -> dict[str, dict[str, object]]:
    """The Bundle and Submission schemas carried by one spec's fenced json blocks."""
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    found: dict[str, dict[str, object]] = {}
    for body in BLOCK.findall(text):
        try:
            block = json.loads(body)
        except json.JSONDecodeError:
            continue
        title = block.get("title") if isinstance(block, dict) else None
        if not isinstance(title, str):
            continue
        for kind in ("Bundle", "Submission"):
            if kind in title:
                found.setdefault(kind, block)
    return found


def main() -> int:
    bundle_spec = newest(BUNDLE_SPEC)
    submission_spec = newest(SUBMISSION_SPEC)
    schemas = extract(bundle_spec) | extract(submission_spec)
    problems: list[str] = []

    for kind in ("Bundle", "Submission"):
        if kind in schemas:
            Draft202012Validator.check_schema(schemas[kind])
            print(f"schema {kind:10s}: {schemas[kind]['title']!r} extracted and meta-valid")
        else:
            problems.append(f"no {kind} schema in the specs beside this fixture")

    def load(name: str) -> dict[str, object]:
        with open(os.path.join(HERE, name), encoding="utf-8") as handle:
            return json.load(handle)

    bundle = load("bundle.json")
    submission = load("submission.json")

    if problems:
        for problem in problems:
            print("  FAIL:", problem)
        print(f"\nRESULT: FAILED ({len(problems)} problem(s))")
        return 1

    consts = {
        kind: schemas[kind]["properties"]["format_version"]["const"]  # type: ignore[index]
        for kind in ("Bundle", "Submission")
    }
    if len(set(consts.values())) != 1:
        problems.append(f"the spec versions disagree: {consts}")
    expected = next(iter(consts.values()))
    for name, document in (("bundle.json", bundle), ("submission.json", submission)):
        if document.get("format_version") != expected:
            problems.append(
                f"{name} declares {document.get('format_version')!r}, the specs say {expected!r}"
            )

    print()
    for kind, name, document in (
        ("Bundle", "bundle.json", bundle),
        ("Submission", "submission.json", submission),
    ):
        errors = sorted(
            Draft202012Validator(schemas[kind]).iter_errors(document),  # type: ignore[arg-type]
            key=lambda e: list(e.absolute_path),
        )
        for error in errors:
            path = "/".join(map(str, error.absolute_path)) or "<root>"
            problems.append(f"{name}: {path}: {error.message}")
        if not errors:
            print(f"schema {kind.lower():10s}: OK  ({name})")

    # (d) the arithmetic, on the bytes.
    responses = submission.get("responses")
    if isinstance(responses, list):
        awarded = Fraction(0)
        for entry in responses:
            if not isinstance(entry, dict):
                continue
            feedback = entry.get("feedback")
            if not isinstance(feedback, dict):
                continue
            points = feedback.get("points_awarded")
            if not isinstance(points, str):
                continue
            criteria = feedback.get("criteria")
            if isinstance(criteria, list) and criteria:
                total = sum(
                    (Fraction(c["points_awarded"]) for c in criteria
                     if isinstance(c, dict) and isinstance(c.get("points_awarded"), str)),
                    Fraction(0),
                )
                if total != Fraction(points):
                    problems.append(
                        f"{entry.get('question_id')}: criteria sum to {total}, "
                        f"points_awarded is {points}"
                    )
            awarded += Fraction(points)
        stated = submission.get("total_awarded_points")
        if isinstance(stated, str):
            if awarded != Fraction(str(stated)):
                problems.append(
                    f"total_awarded_points is {stated}, the per-question awards sum to {awarded}"
                )
            else:
                print(f"arithmetic         : OK  (awarded {awarded})")

    a = bundle["assessment"]
    assert isinstance(a, dict)
    questions = [q for s in a["sections"] for q in s.get("questions", [])]
    possible = sum(
        (Fraction(str(q["points"])) for q in questions if isinstance(q.get("points"), str)),
        Fraction(0),
    )
    if isinstance(submission.get("total_possible_points"), str):
        if Fraction(str(submission["total_possible_points"])) != possible:
            problems.append(
                f"total_possible_points is {submission['total_possible_points']}, "
                f"the questions sum to {possible}"
            )
    print(
        f"questions          : {len(questions)} "
        f"({sum(1 for q in questions if q['type'] == 'alternative_set')} alternative_set); "
        f"possible {possible}"
    )

    print()
    for problem in problems:
        print("  FAIL:", problem)
    if problems:
        print(f"RESULT: FAILED ({len(problems)} problem(s))")
        return 1
    print("RESULT: ALL CLEAN — 2/2 schema valid, version agreed, awards and totals reconcile")
    return 0


if __name__ == "__main__":
    sys.exit(main())
