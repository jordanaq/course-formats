"""Contract tests for `rules.submission` — §8 of the submission spec, minus the arithmetic.

One test per check, and for each check one conforming case and one that must be rejected. The
conforming case is not decoration: a rule that fires on a legal document is worse than a rule
that is missing, because the noise teaches a grader to ignore the linter.
"""
from __future__ import annotations

import copy
import unittest
from typing import Any

from lint_assessment.document import Bundle
from lint_assessment.rules import submission as rules

from . import support

DIGEST = "a" * 64


def choice(qid: str = "q1") -> dict[str, Any]:
    """A single-choice question with two options."""
    return {
        "id": qid,
        "type": "single_choice",
        "prompt": "p",
        "points": "2",
        "estimated_minutes": 1,
        "options": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}],
    }


def written(qid: str = "q2") -> dict[str, Any]:
    """A short-answer question with one rubric criterion."""
    return support.question(qid)


def pool(qid: str = "q3") -> dict[str, Any]:
    """A choose-two pool with two alternatives."""
    return support.group(qid=qid, points="4", choose_n=2, alternatives=("2", "2"))


def bundle() -> Bundle:
    """A bundle with one of each question shape the rules care about."""
    key = support.key_for(("q1", "q2")) | {
        "q1": {"method": "choice", "correct_option_ids": ["a"]},
        "q3_q3_a1": {"method": "analytic_rubric", "reference_answer": "r",
                     "criteria": [{"id": "q3_q3_a1_c1", "description": "d"}]},
        "q3_q3_a2": {"method": "analytic_rubric", "reference_answer": "r",
                     "criteria": [{"id": "q3_q3_a2_c1", "description": "d"}]},
    }
    return Bundle(support.bundle([choice(), written(), pool()], key))


def feedback(points: str, max_points: str = "2", **extra: Any) -> dict[str, Any]:
    """A well-formed feedback block, plus whatever a test adds."""
    block: dict[str, Any] = {
        "released": True,
        "points_awarded": points,
        "max_points": max_points,
        "review_reason": None,
        "include_reference_answer": False,
    }
    block.update(extra)
    return block


def conforming() -> dict[str, Any]:
    """A submission that every rule below must accept."""
    return {
        "format_version": support.VERSION,
        "assessment_id": "t",
        "submission_id": "ada-20261003T092530Z",
        "submitter": {"name": "Ada Lovelace", "username": "ada"},
        "attempt": 1,
        "submitted_at": "2026-10-03T09:25:30Z",
        "paper": {"commit": "0" * 40, "path": "Agents/Courses/x/Exam 01.json", "sha256": DIGEST},
        "responses": [
            {
                "question_id": "q1",
                "response": {"selected_option_ids": ["a"]},
                "feedback": feedback("2", correct=True, correct_option_ids=["a"]),
            },
            {
                "question_id": "q2",
                "response": {"text": "an answer"},
                "feedback": feedback(
                    "5",
                    max_points="5",
                    criteria=[
                        {
                            "criterion_id": "q2_c1",
                            "points_awarded": "5",
                            "evidence": "e",
                            "justification": "j",
                        }
                    ],
                ),
            },
            {
                "question_id": "q3",
                "response": {"q3_a1": {"text": "one"}, "q3_a2": {"text": "two"}},
                "feedback": feedback(
                    "4",
                    points_awarded="4",
                    max_points="4",
                    counted_alternative_ids=["q3_a1", "q3_a2"],
                    ignored_alternative_ids=[],
                    criteria=[
                        {
                            "criterion_id": "q3_a1_c1",
                            "alternative_id": "q3_a1",
                            "points_awarded": "2",
                            "evidence": "e",
                            "justification": "j",
                        },
                        {
                            "criterion_id": "q3_a2_c1",
                            "alternative_id": "q3_a2",
                            "points_awarded": "2",
                            "evidence": "e",
                            "justification": "j",
                        },
                    ],
                ),
            },
        ],
        "grading": {"complete": True, "completed_at": "2026-10-03T10:15:30Z"},
        "graders": [{"username": "tutor", "role": "primary", "at": "2026-10-03T10:15:30Z"}],
        "total_possible_points": "11",
        "total_awarded_points": "11",
    }


def messages(document: dict[str, Any], digest: str | None = DIGEST) -> list[str]:
    """Every diagnostic the rules produce, rendered `path: message`."""
    return [
        f"{diagnostic.path}: {diagnostic.message}"
        for diagnostic in rules.check(bundle(), document, digest)
    ]


def mutated(**changes: Any) -> dict[str, Any]:
    """A deep copy of the conforming document with top-level members replaced."""
    document = copy.deepcopy(conforming())
    document.update(changes)
    return document


class ConformingTest(unittest.TestCase):
    def test_a_conforming_submission_is_silent(self) -> None:
        self.assertEqual(messages(conforming()), [])

    def test_marking_in_progress_is_silent(self) -> None:
        # all-or-nothing still holds: every question carries feedback, one awaits a review
        document = copy.deepcopy(conforming())
        document["grading"] = {"complete": False}
        del document["total_awarded_points"]
        document["responses"][1]["feedback"]["points_awarded"] = None
        document["responses"][1]["feedback"]["review_reason"] = "second marker wanted"
        document["responses"][1]["feedback"]["criteria"] = []
        self.assertEqual(messages(document), [])

    def test_an_unanswered_question_is_silent(self) -> None:
        document = copy.deepcopy(conforming())
        del document["responses"][1]["response"]
        self.assertEqual(messages(document), [])


class IdentityTest(unittest.TestCase):
    def test_a_foreign_assessment_is_one_error(self) -> None:
        self.assertEqual(len(messages(mutated(assessment_id="other"))), 1)

    def test_a_malformed_submission_id_is_one_error(self) -> None:
        self.assertEqual(
            len(messages(mutated(submission_id="ada"))), 1, messages(mutated(submission_id="ada"))
        )

    def test_the_id_and_the_instant_must_agree(self) -> None:
        found = messages(mutated(submitted_at="2026-10-03T09:25:31Z"))
        self.assertTrue(any("instant in the id" in message for message in found), found)

    def test_a_zero_attempt_is_one_error(self) -> None:
        self.assertEqual(len(messages(mutated(attempt=0))), 1)

    def test_a_username_with_whitespace_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["submitter"]["username"] = "ada lovelace"
        self.assertEqual(len(messages(document)), 1)


class PaperTest(unittest.TestCase):
    def test_a_short_commit_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["paper"]["commit"] = "abc"
        self.assertEqual(len(messages(document)), 1)

    def test_uncommitted_is_legal(self) -> None:
        document = copy.deepcopy(conforming())
        document["paper"]["commit"] = "uncommitted"
        self.assertEqual(messages(document), [])

    def test_an_absolute_path_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["paper"]["path"] = "/home/x/Exam 01.json"
        self.assertEqual(len(messages(document)), 1)

    def test_a_changed_paper_is_a_warning_not_an_error(self) -> None:
        diagnostics = list(rules.check(bundle(), conforming(), "b" * 64))
        self.assertEqual([d.severity for d in diagnostics], ["warning"])

    def test_an_uncommitted_paper_cannot_disagree_about_its_hash(self) -> None:
        document = copy.deepcopy(conforming())
        document["paper"]["commit"] = "uncommitted"
        diagnostics = list(rules.check(bundle(), document, "b" * 64))
        self.assertEqual([d.severity for d in diagnostics], [])


class CoverageTest(unittest.TestCase):
    def test_a_missing_question_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        del document["responses"][2]
        self.assertEqual(len(messages(document)), 1)

    def test_a_duplicate_question_is_two_errors(self) -> None:
        document = copy.deepcopy(conforming())
        document["responses"][2] = copy.deepcopy(document["responses"][1])
        found = messages(document)
        self.assertTrue(any("more than once" in message for message in found), found)
        self.assertTrue(any("no entry for 'q3'" in message for message in found), found)

    def test_transposed_entries_are_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["responses"][0], document["responses"][1] = (
            document["responses"][1],
            document["responses"][0],
        )
        found = messages(document)
        self.assertTrue(any("paper order" in message for message in found), found)

    def test_an_unknown_question_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["responses"][2]["question_id"] = "q9"
        self.assertTrue(any("not a question of this paper" in m for m in messages(document)))


class ResponseShapeTest(unittest.TestCase):
    def test_two_selections_in_a_single_choice_are_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["responses"][0]["response"]["selected_option_ids"] = ["a", "b"]
        self.assertEqual(len(messages(document)), 1)

    def test_an_unknown_option_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["responses"][0]["response"]["selected_option_ids"] = ["z"]
        self.assertEqual(len(messages(document)), 1)

    def test_a_choice_answered_with_prose_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["responses"][0]["response"] = {"text": "a"}
        self.assertEqual(len(messages(document)), 1)

    def test_a_pool_keyed_by_a_foreign_id_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["responses"][2]["response"]["q3_a9"] = {"text": "three"}
        self.assertEqual(len(messages(document)), 1)


class FeedbackTest(unittest.TestCase):
    def test_half_marked_feedback_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        del document["responses"][0]["feedback"]
        found = messages(document)
        self.assertTrue(any("all or nothing" in message for message in found), found)

    def test_a_review_reason_on_a_graded_question_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["responses"][0]["feedback"]["review_reason"] = "checked twice"
        self.assertEqual(len(messages(document)), 1)

    def test_a_locator_in_feedback_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["responses"][0]["feedback"]["locators"] = [{"source_id": "s"}]
        self.assertEqual(len(messages(document)), 1)

    def test_a_locator_in_a_criterion_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["responses"][1]["feedback"]["criteria"][0]["locators"] = [{"source_id": "s"}]
        self.assertEqual(len(messages(document)), 1)

    def test_a_criterion_on_an_ignored_alternative_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["responses"][2]["feedback"]["ignored_alternative_ids"] = ["q3_a2"]
        document["responses"][2]["feedback"]["counted_alternative_ids"] = ["q3_a1"]
        found = messages(document)
        self.assertTrue(any("not among the counted" in message for message in found), found)

    def test_a_non_boolean_released_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["responses"][0]["feedback"]["released"] = "yes"
        self.assertEqual(len(messages(document)), 1)


class GradingStateTest(unittest.TestCase):
    def test_complete_without_completed_at_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        del document["grading"]["completed_at"]
        self.assertEqual(len(messages(document)), 1)

    def test_complete_with_a_question_awaiting_review_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["responses"][0]["feedback"]["points_awarded"] = None
        document["responses"][0]["feedback"]["review_reason"] = "second marker"
        found = messages(document)
        self.assertTrue(any("awaiting review" in message for message in found), found)

    def test_approval_needs_an_approver(self) -> None:
        document = copy.deepcopy(conforming())
        document["grading"]["approved"] = True
        document["grading"]["approved_at"] = "2026-10-04T08:00:00Z"
        found = messages(document)
        self.assertTrue(any("approved_by" in message for message in found), found)

    def test_complete_needs_both_totals(self) -> None:
        document = copy.deepcopy(conforming())
        del document["total_awarded_points"]
        self.assertEqual(len(messages(document)), 1)


class GradersTest(unittest.TestCase):
    def test_two_primaries_are_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["graders"].append(
            {"username": "other", "role": "primary", "at": "2026-10-03T11:00:00Z"}
        )
        self.assertEqual(len(messages(document)), 1)

    def test_an_unknown_role_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["graders"][0]["role"] = "supreme"
        self.assertEqual(len(messages(document)), 1)

    def test_a_backwards_audit_trail_is_one_error(self) -> None:
        document = copy.deepcopy(conforming())
        document["graders"].append(
            {"username": "reviewer", "role": "reviewer", "at": "2026-10-02T10:00:00Z"}
        )
        self.assertEqual(len(messages(document)), 1)


if __name__ == "__main__":
    unittest.main()
