"""Contract tests for `identity` (§2.1, §2.4.5, §2.4.6, §8 checks 1 and 9)."""
from __future__ import annotations

import unittest

from lint_assessment.document import Bundle
from lint_assessment.rules import identity

from . import support


def run(doc: dict[str, object]) -> list[str]:
    return [f"{d.severity}: {d.message}" for d in identity.check(Bundle(doc))]  # type: ignore[arg-type]


class DuplicateTest(unittest.TestCase):
    def test_unique_ids_are_clean(self) -> None:
        doc = support.bundle([support.question("q1"), support.question("q2")],
                             support.key_for(("q1", "q2")))
        self.assertEqual(run(doc), [])

    def test_two_questions_with_one_id_are_reported_once(self) -> None:
        doc = support.bundle([support.question("q1"), support.question("q1")],
                             support.key_for(("q1",)))
        errors = [d for d in run(doc) if "q1" in d]
        self.assertEqual(len(errors), 1, errors)

    def test_an_alternative_may_not_share_its_group_id(self) -> None:
        q = support.group(qid="qg")
        q["alternatives"][0]["id"] = "qg"  # type: ignore[index]
        doc = support.bundle([q], support.key_for(tuple(a["id"] for a in q["alternatives"])))  # type: ignore[attr-defined]
        self.assertTrue(any(d.startswith("error") for d in run(doc)))


class KeyCoverageTest(unittest.TestCase):
    def test_missing_entry_is_an_error(self) -> None:
        doc = support.bundle([support.question("q1")], {})
        self.assertTrue(any(d.startswith("error") for d in run(doc)))

    def test_extra_entry_is_an_error(self) -> None:
        doc = support.bundle([support.question("q1")],
                             support.key_for(("q1", "ghost")))
        self.assertTrue(any("ghost" in d for d in run(doc)))

    def test_a_group_may_not_have_its_own_entry(self) -> None:
        q = support.group(qid="qg")
        ids = tuple(a["id"] for a in q["alternatives"])  # type: ignore[attr-defined]
        key = support.key_for(ids)
        key["qg"] = support.key_for(("qg",))["qg"]
        doc = support.bundle([q], key)
        errors = [d for d in run(doc) if "qg" in d]
        self.assertTrue(errors, "a group's own key entry was accepted")


if __name__ == "__main__":
    unittest.main()
