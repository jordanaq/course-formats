"""Contract tests for the report arithmetic (§6, §8 checks 10 and 15).

Each case is a triple: bundle, submission, report. The counter-cases matter more than the
happy path — a cap that binds and is not recorded, and a cap that is recorded and did not
bind, are the two ways a report can misdescribe its own arithmetic.
"""
from __future__ import annotations

import unittest

from lint_assessment.document import Bundle
from lint_assessment.rules import report as report_rule

from . import support


def capped_bundle() -> dict[str, object]:
    q = support.group(points="5", choose_n=3, alternatives=("2", "2", "2"),
                      credit={"mode": "capped"})
    ids = tuple(a["id"] for a in q["alternatives"])  # type: ignore[attr-defined]
    return support.bundle([q], support.key_for(ids))


def group_report(awards: tuple[str, ...], uncapped: str | None) -> dict[str, object]:
    bundle = capped_bundle()
    q = bundle["assessment"]["sections"][0]["questions"][0]  # type: ignore[index]
    ids = [a["id"] for a in q["alternatives"]]
    results = [
        {
            "question_id": q["id"],
            "max_points": "5",
            "feedback": "f",
            "status": "graded",
            "review_reason": None,
            "answered_alternative_ids": ids[: len(awards)],
            "ignored_alternative_ids": [],
            "criterion_scores": [
                {
                    "criterion_id": "c1",
                    "points_awarded": p,
                    "evidence": "",
                    "justification": "j",
                    "alternative_id": aid,
                }
                for aid, p in zip(ids, awards)
            ],
            "awarded_points": "5" if sum(float(p) for p in awards) > 5 else str(int(sum(float(p) for p in awards))),
        }
    ]
    if uncapped is not None:
        results[0]["uncapped_awarded_points"] = uncapped
    return {
        "format_version": support.VERSION,
        "assessment_id": "t",
        "submission_id": "s",
        "grading_status": "graded",
        "total_possible_points": "5",
        "total_awarded_points": results[0]["awarded_points"],
        "results": results,
    }


submission = {"format_version": support.VERSION, "submission_id": "s", "assessment_id": "t",
              "responses": {}}


def run(rep: dict[str, object]) -> list[str]:
    diags = report_rule.check(Bundle(capped_bundle()), submission, rep)  # type: ignore[arg-type]
    return [f"{d.severity}: {d.message}" for d in diags]


class CappedArithmeticTest(unittest.TestCase):
    def test_cap_binding_with_the_uncapped_sum_recorded_is_clean(self) -> None:
        self.assertEqual(run(group_report(("2", "2", "2"), "6")), [])

    def test_cap_binding_without_the_uncapped_sum_is_an_error(self) -> None:
        self.assertTrue(any(d.startswith("error") for d in run(group_report(("2", "2", "2"), None))))

    def test_uncapped_sum_recorded_when_the_cap_did_not_bind_is_an_error(self) -> None:
        self.assertTrue(any(d.startswith("error") for d in run(group_report(("2", "2", "1"), "5"))))

    def test_cap_not_binding_without_the_field_is_clean(self) -> None:
        self.assertEqual(run(group_report(("2", "2", "1"), None)), [])


class EqualArithmeticTest(unittest.TestCase):
    def test_award_disagreeing_with_the_awards_is_an_error(self) -> None:
        rep = group_report(("2", "2", "2"), "6")
        rep["results"][0]["awarded_points"] = "4"  # type: ignore[index]
        self.assertTrue(any(d.startswith("error") for d in run(rep)))

    def test_uncapped_field_on_an_equal_group_is_an_error(self) -> None:
        bundle = support.bundle(
            [support.group(points="10", choose_n=2, alternatives=("5", "5"))],
            support.key_for(("qg_a1", "qg_a2")),
        )
        rep = {
            "format_version": support.VERSION, "assessment_id": "t", "submission_id": "s",
            "grading_status": "graded", "total_possible_points": "10",
            "total_awarded_points": "10",
            "results": [{
                "question_id": "qg", "max_points": "10", "feedback": "f",
                "status": "graded", "review_reason": None,
                "answered_alternative_ids": ["qg_a1", "qg_a2"],
                "ignored_alternative_ids": [],
                "criterion_scores": [
                    {"criterion_id": "c1", "points_awarded": "5", "evidence": "",
                     "justification": "j", "alternative_id": "qg_a1"},
                    {"criterion_id": "c1", "points_awarded": "5", "evidence": "",
                     "justification": "j", "alternative_id": "qg_a2"},
                ],
                "awarded_points": "10",
                "uncapped_awarded_points": "10",
            }],
        }
        diags = report_rule.check(Bundle(bundle), submission, rep)  # type: ignore[arg-type]
        self.assertTrue(any(d.severity == "error" for d in diags))


class ChoiceScoringTest(unittest.TestCase):
    """A choice question carries no rubric: its award comes from §3, not from criteria."""

    def build(self, selected: tuple[str, ...], awarded: str) -> tuple[dict, dict, dict]:
        q = {
            "id": "q1", "type": "single_choice", "prompt": "p", "points": "1",
            "estimated_minutes": 1,
            "options": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"},
                        {"id": "c", "text": "C"}],
        }
        key = {"q1": {"method": "choice", "correct_option_ids": ["b"],
                      "explanation": "because"}}
        bundle = support.bundle([q], key)
        submission = {"format_version": support.VERSION, "assessment_id": "t",
                      "submission_id": "s",
                      "responses": {"q1": {"selected_option_ids": list(selected)}}}
        report = {
            "format_version": support.VERSION, "assessment_id": "t", "submission_id": "s",
            "grading_status": "graded", "total_possible_points": "1",
            "total_awarded_points": awarded,
            "results": [{
                "question_id": "q1", "max_points": "1", "feedback": "f",
                "status": "graded", "review_reason": None, "criterion_scores": [],
                "awarded_points": awarded,
            }],
        }
        return bundle, submission, report

    def run_case(self, selected: tuple[str, ...], awarded: str) -> list[str]:
        bundle, submission, report = self.build(selected, awarded)
        diags = report_rule.check(Bundle(bundle), submission, report)  # type: ignore[arg-type]
        return [f"{d.path}: {d.message}" for d in diags]

    def test_correct_selection_with_an_empty_rubric_is_clean(self) -> None:
        # the counter-case this rule exists for: summing criteria would report "0 awarded"
        self.assertEqual(self.run_case(("b",), "1"), [])

    def test_wrong_selection_awarded_full_marks_is_an_error(self) -> None:
        self.assertTrue(self.run_case(("a",), "1"))

    def test_wrong_selection_awarded_zero_is_clean(self) -> None:
        self.assertEqual(self.run_case(("a",), "0"), [])

    def test_partial_credit_uses_the_penalized_proportion(self) -> None:
        # 3 points, correct {a,b}, one distractor: one of two correct = 3 * (1/2 - 0) = 3/2
        q = {"id": "q1", "type": "multiple_select", "prompt": "p", "points": "3",
             "estimated_minutes": 1, "scoring_policy": "partial_credit",
             "options": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"},
                         {"id": "c", "text": "C"}]}
        key = {"q1": {"method": "choice", "correct_option_ids": ["a", "b"],
                      "explanation": "because"}}
        bundle = support.bundle([q], key)
        submission = {"format_version": support.VERSION, "assessment_id": "t",
                      "submission_id": "s",
                      "responses": {"q1": {"selected_option_ids": ["a"]}}}
        report = {"format_version": support.VERSION, "assessment_id": "t",
                  "submission_id": "s", "grading_status": "graded",
                  "total_possible_points": "3", "total_awarded_points": "3/2",
                  "results": [{"question_id": "q1", "max_points": "3", "feedback": "f",
                               "status": "graded", "review_reason": None,
                               "criterion_scores": [], "awarded_points": "3/2"}]}
        self.assertEqual(
            [d.message for d in report_rule.check(Bundle(bundle), submission, report)],  # type: ignore[arg-type]
            [],
        )
        report["total_awarded_points"] = "3"  # type: ignore[index]
        report["results"][0]["awarded_points"] = "3"  # type: ignore[index]
        self.assertTrue(
            [d for d in report_rule.check(Bundle(bundle), submission, report)]  # type: ignore[arg-type]
        )


if __name__ == "__main__":
    unittest.main()
