"""Contract tests for the group credit rule (§2.4.2, §8 check 15).

The two modes are tested against each other deliberately: the same alternatives are legal
under `capped` and illegal under `equal`, and the tests pin that the mode — not the numbers —
decides which arithmetic applies.
"""
from __future__ import annotations

import unittest

from lint_assessment.document import Bundle
from lint_assessment.rules import credit

from . import support


def run(doc: dict[str, object]) -> list[str]:
    """Diagnostics from `credit.check`, as `severity: message` strings, for assertion."""
    diags = list(credit.check(Bundle(doc)))  # type: ignore[arg-type]
    return [f"{d.severity}: {d.message}" for d in diags]


class EqualModeTest(unittest.TestCase):
    def test_equal_shares_are_clean(self) -> None:
        q = support.group(points="10", choose_n=2, alternatives=("5", "5", "5"))
        ids = tuple(a["id"] for a in q["alternatives"])  # type: ignore[attr-defined]
        self.assertEqual(run(support.bundle([q], support.key_for(ids))), [])

    def test_unequal_shares_are_an_error_in_equal_mode(self) -> None:
        q = support.group(points="10", choose_n=2, alternatives=("5", "4", "5"))
        ids = tuple(a["id"] for a in q["alternatives"])  # type: ignore[attr-defined]
        diags = run(support.bundle([q], support.key_for(ids)))
        self.assertTrue(any(d.startswith("error") for d in diags), diags)

    def test_undivisible_weight_is_an_error(self) -> None:
        # 10 / 3 has no integer spelling, so no alternative can be "5/3" and be equal-weight
        q = support.group(points="10", choose_n=3, alternatives=("3", "3", "3"))
        ids = tuple(a["id"] for a in q["alternatives"])  # type: ignore[attr-defined]
        self.assertTrue(any(d.startswith("error") for d in run(support.bundle([q], support.key_for(ids)))))

    def test_explicit_equal_mode_behaves_like_absence(self) -> None:
        q = support.group(points="10", choose_n=2, alternatives=("5", "5"),
                          credit={"mode": "equal"})
        ids = tuple(a["id"] for a in q["alternatives"])  # type: ignore[attr-defined]
        self.assertEqual(run(support.bundle([q], support.key_for(ids))), [])


class CappedModeTest(unittest.TestCase):
    def test_pool_with_purse_below_the_sum_is_clean(self) -> None:
        q = support.group(points="5", choose_n=3, alternatives=("2", "2", "2", "2"),
                          credit={"mode": "capped"})
        ids = tuple(a["id"] for a in q["alternatives"])  # type: ignore[attr-defined]
        self.assertEqual(run(support.bundle([q], support.key_for(ids))), [])

    def test_alternative_above_the_ceiling_is_an_error(self) -> None:
        q = support.group(points="5", choose_n=2, alternatives=("6", "2"),
                          credit={"mode": "capped"})
        ids = tuple(a["id"] for a in q["alternatives"])  # type: ignore[attr-defined]
        self.assertTrue(any(d.startswith("error") for d in run(support.bundle([q], support.key_for(ids)))))

    def test_unreachable_purse_is_a_warning_not_an_error(self) -> None:
        q = support.group(points="5", choose_n=2, alternatives=("2", "2", "2"),
                          credit={"mode": "capped"})
        ids = tuple(a["id"] for a in q["alternatives"])  # type: ignore[attr-defined]
        diags = run(support.bundle([q], support.key_for(ids)))
        self.assertTrue(any(d.startswith("warning") for d in diags), diags)
        self.assertFalse(any(d.startswith("error") for d in diags), diags)

    def test_reachable_purse_raises_nothing(self) -> None:
        q = support.group(points="6", choose_n=3, alternatives=("2", "2", "2"),
                          credit={"mode": "capped"})
        ids = tuple(a["id"] for a in q["alternatives"])  # type: ignore[attr-defined]
        self.assertEqual(run(support.bundle([q], support.key_for(ids))), [])


class ModeVocabularyTest(unittest.TestCase):
    def test_unknown_mode_is_an_error(self) -> None:
        q = support.group(points="5", choose_n=2, alternatives=("2", "2"),
                          credit={"mode": "weighted"})
        ids = tuple(a["id"] for a in q["alternatives"])  # type: ignore[attr-defined]
        self.assertTrue(any(d.startswith("error") for d in run(support.bundle([q], support.key_for(ids)))))

    def test_credit_on_a_non_group_is_an_error(self) -> None:
        q = support.question("q1", "5")
        q["credit"] = {"mode": "capped"}
        diags = run(support.bundle([q], support.key_for(("q1",))))
        self.assertTrue(any(d.startswith("error") for d in diags), diags)


class SuppressionTest(unittest.TestCase):
    def test_an_invalid_mode_suppresses_the_arithmetic(self) -> None:
        # one broken field must yield one diagnostic, not one per rule that reads it
        q = support.group(points="5", choose_n=2, alternatives=("6", "2"),
                          credit={"mode": "weighted"})
        ids = tuple(a["id"] for a in q["alternatives"])  # type: ignore[attr-defined]
        errors = [d for d in run(support.bundle([q], support.key_for(ids))) if d.startswith("error")]
        self.assertEqual(len(errors), 1, errors)


if __name__ == "__main__":
    unittest.main()
