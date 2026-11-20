"""Contract tests for `words` (§2.2.1 response limits, §2.8 delivery)."""
from __future__ import annotations

import unittest

from lint_assessment.document import Bundle
from lint_assessment.rules import words

from . import support


def run(doc: dict[str, object]) -> list[str]:
    return [f"{d.path}: {d.message}" for d in words.check(Bundle(doc))]  # type: ignore[arg-type]


def bundle_with(limit: object = None, qtype: str = "short_answer") -> dict[str, object]:
    q = support.question("q1", qtype=qtype)
    if qtype == "single_choice":
        q["options"] = [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}]
        del q["response_lines"]
        key = {"q1": {"method": "choice", "correct_option_ids": ["a"]}}
    else:
        key = support.key_for(("q1",))
    if limit is not None:
        q["suggested_word_count"] = limit
    return support.bundle([q], key)


def with_delivery(block: object) -> list[str]:
    doc = support.bundle([support.question("q1")], support.key_for(("q1",)))
    assessment = doc["assessment"]
    assert isinstance(assessment, dict)
    assessment["delivery"] = block
    return run(doc)


class WordLimitTest(unittest.TestCase):
    def test_well_formed_range_is_silent(self) -> None:
        self.assertEqual(run(bundle_with({"min": 100, "max": 150})), [])

    def test_advisory_needs_no_note(self) -> None:
        self.assertEqual(run(bundle_with({"min": 1, "max": 300, "enforcement": "advisory"})), [])

    def test_recorded_needs_a_note(self) -> None:
        self.assertTrue(run(bundle_with({"min": 1, "max": 300, "enforcement": "recorded"})))
        self.assertEqual(
            run(bundle_with({"min": 1, "max": 300, "enforcement": "recorded", "note": "n"})), []
        )

    def test_enforcement_outside_the_vocabulary(self) -> None:
        self.assertTrue(run(bundle_with({"min": 1, "max": 3, "enforcement": "strict"})))

    def test_empty_range(self) -> None:
        self.assertTrue(run(bundle_with({"min": 300, "max": 100})))

    def test_non_positive_endpoints(self) -> None:
        self.assertTrue(run(bundle_with({"min": 0, "max": 100})))

    def test_not_an_object(self) -> None:
        self.assertTrue(run(bundle_with(150)))

    def test_on_a_choice_question(self) -> None:
        self.assertTrue(run(bundle_with({"min": 1, "max": 3}, qtype="single_choice")))


class DeliveryTest(unittest.TestCase):
    def test_absent_delivery_is_silent(self) -> None:
        # absence means closed book (§2.8) — a legal declaration, never a finding
        self.assertEqual(run(bundle_with()), [])

    def test_open_book_is_silent(self) -> None:
        self.assertEqual(with_delivery({"mode": "open_book"}), [])

    def test_missing_mode_is_an_error(self) -> None:
        self.assertTrue(with_delivery({}))

    def test_unknown_mode_is_an_error(self) -> None:
        self.assertTrue(with_delivery({"mode": "semi_open"}))


if __name__ == "__main__":
    unittest.main()
