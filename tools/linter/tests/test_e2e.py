"""End-to-end: every translated key must lint clean, and mutations of them must not.

The fixtures are real instructor keys translated into conforming v0.11.1 documents — three
papers with different shapes: a capped pool of eight terms, an MCQ-heavy paper whose choice
questions carry no rubric, and an essay paper with an equal-credit alternative set and a
full-weight floor. They live in the repo, not in a scratch directory: a fixture a cache
pruner can delete is a suite that silently stops testing.

The golden documents are evidence, not axioms. A translation can be wrong, and when the
linter and a fixture disagree the question is which one is wrong. Both disagreements found so
far were the linter's — a `single_choice` result carries no criterion awards (§3.2 is
all-or-nothing, not a rubric sum), and §2.7 lets a coverage entry cite an alternative — and
each is now pinned by its own module test rather than by relaxing the rule.

Env: `LINT_FIXTURES` overrides the fixture directory.
"""
from __future__ import annotations

import json
import os
import unittest
from typing import Any

from lint_assessment.document import Bundle
from lint_assessment.lint import lint_submission
from lint_assessment.spec import (
    latest_spec, latest_submission_spec, load_schemas, read_text,
)

FIXTURES = os.environ.get(
    "LINT_FIXTURES",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures"),
)
DESIGN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#: Files every fixture set must provide.
REQUIRED = ("bundle.json", "submission.json")


def newest_spec() -> str:
    """The current spec, found by version — not by hard-coded name (`spec.latest_spec`)."""
    return latest_spec(DESIGN) or os.path.join(DESIGN, "missing.md")


SPEC = newest_spec()


def fixture_sets() -> tuple[str, ...]:
    """Every fixture set: the directory itself, if it holds a triple, then each subdirectory."""
    found: list[str] = []
    if all(os.path.isfile(os.path.join(FIXTURES, name)) for name in REQUIRED):
        found.append(FIXTURES)
    for name in sorted(os.listdir(FIXTURES)):
        candidate = os.path.join(FIXTURES, name)
        if os.path.isdir(candidate) and all(
            os.path.isfile(os.path.join(candidate, required)) for required in REQUIRED
        ):
            found.append(candidate)
    return tuple(found)


def load(directory: str, name: str) -> Any:
    with open(os.path.join(directory, name), encoding="utf-8") as handle:
        return json.load(handle)


class GoldenTest(unittest.TestCase):
    """Each translated key is a conforming document triple."""

    def setUp(self) -> None:
        bundle_text = read_text(SPEC)
        submission_path = latest_submission_spec(DESIGN)
        submission_text = read_text(submission_path) if submission_path is not None else None
        if bundle_text is None or submission_text is None:
            self.skipTest("one of the specs is not readable")
        schemas = load_schemas(bundle_text, submission_text)
        if schemas is None:
            self.fail("the specs' bundle and submission schemas could not be extracted")
        self.schemas = schemas

    def test_every_fixture_set_is_clean(self) -> None:
        found = fixture_sets()
        if not found:
            self.skipTest("no golden fixtures present")
        for directory in found:
            with self.subTest(fixture=os.path.relpath(directory, FIXTURES)):
                result = lint_submission(
                    Bundle(load(directory, "bundle.json")),
                    load(directory, "submission.json"),
                    self.schemas,
                )
                self.assertEqual([d.message for d in result.diagnostics], [])

    def test_the_sets_cover_more_than_one_question_type(self) -> None:
        found = fixture_sets()
        if not found:
            self.skipTest("no golden fixtures present")
        types: set[str] = set()
        for directory in found:
            bundle = load(directory, "bundle.json")
            for section in bundle["assessment"]["sections"]:
                for question in section.get("questions", []):
                    types.add(question.get("type"))
        self.assertIn("alternative_set", types)
        self.assertIn("single_choice", types)
        self.assertIn("short_answer", types)


class MutationTest(unittest.TestCase):
    """A mutation of any fixture must produce at least one error."""

    def setUp(self) -> None:
        bundle_text = read_text(SPEC)
        submission_path = latest_submission_spec(DESIGN)
        submission_text = read_text(submission_path) if submission_path is not None else None
        if bundle_text is None or submission_text is None:
            self.skipTest("one of the specs is not readable")
        schemas = load_schemas(bundle_text, submission_text)
        if schemas is None:
            self.fail("the specs' bundle and submission schemas could not be extracted")
        self.schemas = schemas

    def test_a_wrong_total_is_rejected(self) -> None:
        found = fixture_sets()
        if not found:
            self.skipTest("no golden fixtures present")
        for directory in found:
            with self.subTest(fixture=os.path.relpath(directory, FIXTURES)):
                submission = load(directory, "submission.json")
                submission["total_possible_points"] = "0"
                result = lint_submission(
                    Bundle(load(directory, "bundle.json")),
                    submission,
                    self.schemas,
                )
                self.assertTrue(result.errors, "a stated total of 0 was accepted")

    def test_an_alternative_above_its_ceiling_is_rejected(self) -> None:
        found = fixture_sets()
        if not found:
            self.skipTest("no golden fixtures present")
        tested = False
        for directory in found:
            bundle = load(directory, "bundle.json")
            for section in bundle["assessment"]["sections"]:
                for question in section.get("questions", []):
                    if not isinstance(question.get("credit"), dict):
                        continue
                    question["alternatives"][0]["points"] = "999"
                    result = lint_submission(
                        Bundle(bundle),
                        load(directory, "submission.json"),
                        self.schemas,
                    )
                    self.assertTrue(result.errors, "an alternative above the ceiling was accepted")
                    tested = True
                    break
                if tested:
                    break
        self.assertTrue(tested, "no capped group in any fixture to mutate")

    def test_a_released_criterion_against_an_ungraded_one_is_not_flagged(
        self,
    ) -> None:
        # release is a display flag, never a reason to reject a marking record
        found = fixture_sets()
        if not found:
            self.skipTest("no golden fixtures present")
        directory = found[0]
        submission = load(directory, "submission.json")
        for entry in submission["responses"]:
            feedback = entry.get("feedback")
            if isinstance(feedback, dict):
                for criterion in feedback.get("criteria", []):
                    criterion["released"] = False
        result = lint_submission(
            Bundle(load(directory, "bundle.json")), submission, self.schemas
        )
        self.assertEqual([d.message for d in result.errors], [])


if __name__ == "__main__":
    unittest.main()
