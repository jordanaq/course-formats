"""Contract tests for `points` (§2.2, §2.3.1, §2.4.1, §2.4.5)."""
from __future__ import annotations

import unittest
from typing import Any

from lint_assessment.document import Bundle
from lint_assessment.rules import points

from . import support


def run(doc: dict[str, object]) -> list[str]:
    return [f"{d.path}: {d.message}" for d in points.check(Bundle(doc))]  # type: ignore[arg-type]


def one(question: dict[str, Any], key: dict[str, Any] | None = None) -> dict[str, object]:
    return support.bundle([question], key if key is not None else support.key_for(("q1",)))


class ShapeTest(unittest.TestCase):
    def test_conforming_question_is_silent(self) -> None:
        self.assertEqual(run(one(support.question("q1"))), [])

    def test_missing_type_is_one_error(self) -> None:
        q = support.question("q1")
        del q["type"]
        self.assertEqual(len(run(one(q))), 1)

    def test_unknown_type_is_one_error(self) -> None:
        self.assertEqual(len(run(one(support.question("q1", qtype="vibes")))), 1)

    def test_non_object_question_is_addressed_by_index(self) -> None:
        doc = one(support.question("q1"))
        doc["assessment"]["sections"][0]["questions"].append(5)  # type: ignore[index]
        messages = run(doc)
        self.assertTrue(any("questions[1]" in m for m in messages), messages)

    def test_group_needs_two_alternatives_and_a_usable_choose_n(self) -> None:
        single = support.group(qid="qg")
        single["alternatives"] = single["alternatives"][:1]  # type: ignore[index]
        self.assertTrue(any("at least two" in m for m in run(one(single, {}))))

        too_many = support.group(qid="qg", choose_n=9)
        self.assertTrue(any("choose_n" in m for m in run(one(too_many, {}))))

    def test_choose_n_true_is_not_an_integer(self) -> None:
        q = support.group(qid="qg")
        q["choose_n"] = True
        self.assertTrue(any("choose_n" in m for m in run(one(q, {}))))


class PointValuesTest(unittest.TestCase):
    def test_non_canonical_points(self) -> None:
        for bad in ("4.5", "2/4", "5/1", "05", "lots"):
            with self.subTest(bad=bad):
                q = support.question("q1")
                q["points"] = bad
                self.assertTrue(any("canonical" in m for m in run(one(q))))

    def test_zero_and_negative(self) -> None:
        q = support.question("q1")
        q["points"] = "0"
        self.assertTrue(any("positive" in m for m in run(one(q))))

    def test_canonical_fraction_passes(self) -> None:
        q = support.question("q1")
        q["points"] = "9/2"
        self.assertEqual(run(one(q)), [])

    def test_written_question_needs_response_lines(self) -> None:
        q = support.question("q1")
        del q["response_lines"]
        self.assertTrue(any("response_lines" in m for m in run(one(q))))

    def test_choice_question_needs_options(self) -> None:
        q = {
            "id": "q1",
            "type": "single_choice",
            "prompt": "p",
            "points": "2",
            "estimated_minutes": 1,
        }
        key = {"q1": {"method": "choice", "correct_option_ids": ["a"]}}
        self.assertTrue(any("options" in m for m in run(one(q, key))))

    def test_duplicate_option_ids(self) -> None:
        q = {
            "id": "q1",
            "type": "single_choice",
            "prompt": "p",
            "points": "2",
            "estimated_minutes": 1,
            "options": [{"id": "a", "text": "A"}, {"id": "a", "text": "B"}],
        }
        key = {"q1": {"method": "choice", "correct_option_ids": ["a"]}}
        self.assertTrue(any("unique" in m for m in run(one(q, key))))


if __name__ == "__main__":
    unittest.main()
