"""Criterion weights (§4.2.1, §8 check 8).

Three rules and one non-rule. The three: a rubric is fully weighted or unweighted, its weights
sum to the owner's `points` exactly, and each weight is canonical. The non-rule is the one
worth pinning hardest — an unweighted rubric is **not** equally weighted, so it must produce no
diagnostic at all, even when one criterion takes the whole question.
"""
from __future__ import annotations

import unittest
from typing import Any

from lint_assessment.document import Bundle
from lint_assessment.rules import report as report_rule
from lint_assessment.rules import weights

from . import support


def rubric(points: list[str | None]) -> dict[str, Any]:
    """A short-answer question whose criteria optionally carry the given weights."""
    criteria: list[dict[str, Any]] = []
    for index, weight in enumerate(points, start=1):
        criterion: dict[str, Any] = {"id": f"c{index}", "description": "d"}
        if weight is not None:
            criterion["points"] = weight
        criteria.append(criterion)
    return {"method": "analytic_rubric", "reference_answer": "r", "criteria": criteria}


def bundle(question_points: str, weights_: list[str | None]) -> Bundle:
    question = support.question("q1", points=question_points)
    return Bundle(
        support.bundle(
            [question],
            {"q1": rubric(weights_)},
        )
    )


def messages(built: Bundle) -> list[str]:
    return [d.message for d in weights.check(built)]


class WeightedTest(unittest.TestCase):
    def test_a_partition_that_sums_to_the_question_is_clean(self) -> None:
        self.assertEqual(messages(bundle("5", ["2", "2", "1"])), [])

    def test_a_fractional_weight_is_clean(self) -> None:
        self.assertEqual(messages(bundle("5", ["5/2", "5/2"])), [])

    def test_a_full_marks_essay_split_is_clean(self) -> None:
        self.assertEqual(messages(bundle("10", ["4", "3", "3"])), [])

    def test_an_alternative_set_uses_the_alternative_s_points(self) -> None:
        # a pool: each alternative's own rubric carries that alternative's weight
        question = {
            "id": "q1",
            "type": "alternative_set",
            "prompt": "p",
            "points": "5",
            "choose_n": 3,
            "credit": {"mode": "capped"},
            "estimated_minutes": 5,
            "alternatives": [
                {
                    "id": f"a{index}",
                    "type": "short_answer",
                    "prompt": "p",
                    "points": "2",
                    "estimated_minutes": 1,
                    "response_lines": 3,
                }
                for index in range(1, 9)
            ],
        }
        key = {f"a{index}": rubric(["2"]) for index in range(1, 9)}
        self.assertEqual(messages(Bundle(support.bundle([question], key))), [])


class WeightedViolationTest(unittest.TestCase):
    def test_a_short_sum_is_an_error(self) -> None:
        found = messages(bundle("5", ["2", "2", "1/2"]))
        self.assertEqual(len(found), 1)
        self.assertIn("sum to 9/2", found[0])
        self.assertIn("worth 5", found[0])

    def test_an_over_sum_is_an_error(self) -> None:
        found = messages(bundle("5", ["2", "2", "1", "2"]))
        self.assertEqual(len(found), 1)
        self.assertIn("sum to 7", found[0])

    def test_a_half_weighted_rubric_is_an_error(self) -> None:
        found = messages(bundle("5", ["2", None, "1"]))
        self.assertEqual(len(found), 1)
        self.assertIn("2 of 3 criteria declare a weight", found[0])
        self.assertIn("'c2'", found[0])

    def test_a_non_canonical_weight_is_an_error(self) -> None:
        found = messages(bundle("5", ["5/1", "2", "2"]))
        self.assertTrue(found)
        self.assertTrue(all("canonical rational" in message for message in found))


class UnweightedIsNotEqualTest(unittest.TestCase):
    """The non-rule: silence means the author did not partition, not that the shares are even."""

    def test_an_unweighted_rubric_is_clean(self) -> None:
        self.assertEqual(messages(bundle("5", [None, None, None])), [])

    def test_an_unweighted_rubric_is_clean_even_when_one_criterion_is_the_whole_question(self) -> None:
        # nothing here declares a weight, so nothing is violated; the report rule is what
        # bounds an award, and it has no weight to bound against
        self.assertEqual(messages(bundle("5", [None, None])), [])


if __name__ == "__main__":
    unittest.main()


class ReportBoundTest(unittest.TestCase):
    """The report rule bounds an award against a weight the bundle actually declares."""

    def _triple(self, weights_: list[str | None], awards: list[str]) -> tuple[Bundle, dict[str, Any]]:
        question = support.question("q1", points="5")
        built = Bundle(
            support.bundle(
                [question],
                {
                    "q1": {
                        "method": "analytic_rubric",
                        "reference_answer": "r",
                        "criteria": [
                            dict(
                                {"id": f"c{index}", "description": "d"},
                                **({"points": weight} if weight is not None else {}),
                            )
                            for index, weight in enumerate(weights_, start=1)
                        ],
                    }
                },
            )
        )
        total = sum((__import__("fractions").Fraction(a) for a in awards), __import__("fractions").Fraction(0))
        report = {
            "format_version": support.VERSION,
            "assessment_id": "t",
            "submission_id": "s",
            "grading_status": "graded",
            "total_possible_points": "5",
            "total_awarded_points": str(total),
            "results": [
                {
                    "question_id": "q1",
                    "max_points": "5",
                    "status": "graded",
                    "awarded_points": str(total),
                    "feedback": "f",
                    "criterion_scores": [
                        {
                            "criterion_id": f"c{index}",
                            "points_awarded": award,
                            "justification": "j",
                        }
                        for index, award in enumerate(awards, start=1)
                    ],
                }
            ],
        }
        return built, report

    def test_an_award_above_the_weight_is_reported(self) -> None:
        built, report = self._triple(["2", "2", "1"], ["3", "1", "1"])
        found = [d.message for d in report_rule.criterion_weights(built, report)]
        self.assertEqual(len(found), 1)
        self.assertIn("declared by criterion 'c1'", found[0])
        self.assertIn("the weight 2", found[0])

    def test_an_award_at_the_weight_is_clean(self) -> None:
        built, report = self._triple(["2", "2", "1"], ["2", "2", "1"])
        self.assertEqual(list(report_rule.criterion_weights(built, report)), [])

    def test_an_unweighted_rubric_has_no_bound_to_apply(self) -> None:
        built, report = self._triple([None, None, None], ["5", "0", "0"])
        self.assertEqual(list(report_rule.criterion_weights(built, report)), [])
