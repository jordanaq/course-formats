"""Contract tests for `scope_coverage` (§2.6, §2.6.4, §2.6.5, §8 checks 11–13)."""
from __future__ import annotations

import unittest

from lint_assessment.document import Bundle
from lint_assessment.rules import scope_coverage

from . import support

SOURCE = {"id": "s1", "citation": "Book", "tier": "required", "category": "primary",
          "schemes": [{"scheme": "chapter", "status": "verified"}],
          "ranges": [{"scheme": "chapter", "start": "1", "end": "9", "status": "verified"}]}


def doc(**extras: object) -> dict[str, object]:
    bundle = support.bundle([support.question("q1")], support.key_for(("q1",)))
    assessment = bundle["assessment"]
    assert isinstance(assessment, dict)
    for key, value in extras.items():
        assessment[key] = value
    return bundle


def scope(**over: object) -> dict[str, object]:
    body: dict[str, object] = {
        "course": {"id": "c1"},
        "segments": [{"id": "seg1", "kind": "unit"}, {"id": "seg2", "kind": "unit"}],
    }
    body.update(over)
    return body


def run(bundle: dict[str, object]) -> list[str]:
    return [f"{d.path}: {d.message}" for d in scope_coverage.check(Bundle(bundle))]  # type: ignore[arg-type]


class ScopeTest(unittest.TestCase):
    def test_well_formed_scope_is_silent(self) -> None:
        self.assertEqual(run(doc(scope=scope(), sources=[SOURCE])), [])

    def test_course_id_is_required(self) -> None:
        self.assertTrue(run(doc(scope={"course": {}, "segments": [{"id": "s"}]})))

    def test_segments_must_be_present(self) -> None:
        self.assertTrue(run(doc(scope={"course": {"id": "c"}, "segments": []})))

    def test_duplicate_segment_ids(self) -> None:
        bad = scope(segments=[{"id": "s"}, {"id": "s"}])
        self.assertTrue(run(doc(scope=bad)))

    def test_coverage_without_scope_is_an_error(self) -> None:
        self.assertTrue(any("scope" in m for m in run(doc(coverage={"assessed": [{"segment_id": "s", "question_ids": ["q1"]}]})))) 


class TierGateTest(unittest.TestCase):
    def test_source_without_tier(self) -> None:
        source = dict(SOURCE)
        del source["tier"]
        self.assertTrue(run(doc(scope=scope(), sources=[source])))

    def test_tier_outside_the_vocabulary(self) -> None:
        self.assertTrue(run(doc(scope=scope(), sources=[dict(SOURCE, tier="core")])))

    def test_category_outside_the_vocabulary(self) -> None:
        self.assertTrue(run(doc(scope=scope(), sources=[dict(SOURCE, category="tertiary")])))

    def test_threshold_share_requires_score_mode(self) -> None:
        gate = {"mastery": True, "threshold_share": "3/5"}
        self.assertTrue(run(doc(scope=scope(), sources=[SOURCE], gate=gate)))

    def test_threshold_share_above_one(self) -> None:
        gate = {"mastery": True, "mode": "score", "threshold_share": "6/5"}
        self.assertTrue(run(doc(scope=scope(), sources=[SOURCE], gate=gate)))

    def test_mastery_threshold_is_silent(self) -> None:
        gate = {"mastery": True, "mode": "score", "threshold_share": "3/5"}
        self.assertEqual(run(doc(scope=scope(), sources=[SOURCE], gate=gate)), [])

    def test_mastery_without_a_mode_is_an_error(self) -> None:
        # §2.6.3: a gated paper must say whether completion or a score advances it
        self.assertTrue(run(doc(scope=scope(), sources=[SOURCE], gate={"mastery": True})))

    def test_mastery_false_without_a_mode_is_silent(self) -> None:
        self.assertEqual(run(doc(scope=scope(), sources=[SOURCE], gate={"mastery": False})), [])


class FloorTest(unittest.TestCase):
    def test_floor_naming_an_unused_tier(self) -> None:
        floors = [{"tier": "extension", "min_share": "1/2", "applies_to": "all"}]
        self.assertTrue(run(doc(scope=scope(), sources=[SOURCE], floors=floors)))

    def test_duplicate_floors_for_one_tier(self) -> None:
        floors = [{"tier": "required", "min_share": "1/2", "applies_to": "all"},
                  {"tier": "required", "min_share": "3/4", "applies_to": "all"}]
        self.assertTrue(run(doc(scope=scope(), sources=[SOURCE], floors=floors)))

    def test_mastery_floor_without_a_mastery_gate(self) -> None:
        floors = [{"tier": "required", "min_share": "1", "applies_to": "mastery"}]
        gate = {"mastery": False}
        self.assertTrue(run(doc(scope=scope(), sources=[SOURCE], floors=floors, gate=gate)))

    def test_mastery_floor_with_a_mastery_gate_is_silent(self) -> None:
        floors = [{"tier": "required", "min_share": "1", "applies_to": "mastery"}]
        gate = {"mastery": True, "mode": "completion"}
        self.assertEqual(run(doc(scope=scope(), sources=[SOURCE], floors=floors, gate=gate)), [])


class CoverageTest(unittest.TestCase):
    def test_unknown_segment(self) -> None:
        coverage = {"assessed": [{"segment_id": "nope", "question_ids": ["q1"]}]}
        self.assertTrue(run(doc(scope=scope(), sources=[SOURCE], coverage=coverage)))

    def test_unknown_question(self) -> None:
        coverage = {"assessed": [{"segment_id": "seg1", "question_ids": ["ghost"]}]}
        self.assertTrue(run(doc(scope=scope(), sources=[SOURCE], coverage=coverage)))

    def test_omission_reason_outside_the_vocabulary(self) -> None:
        coverage = {"assessed": [{"segment_id": "seg1", "question_ids": ["q1"]}],
                    "omitted": [{"segment_id": "seg2", "reason": "vibes", "topic": "t"}]}
        self.assertTrue(run(doc(scope=scope(), sources=[SOURCE], coverage=coverage)))

    def test_conforming_coverage_is_silent(self) -> None:
        coverage = {"assessed": [{"segment_id": "seg1", "question_ids": ["q1"]}],
                    "omitted": [{"segment_id": "seg2", "reason": "time", "topic": "ch. 9"}]}
        self.assertEqual(run(doc(scope=scope(), sources=[SOURCE], coverage=coverage)), [])

    def test_an_alternative_id_may_be_cited(self) -> None:
        # §2.7 accepts "a question or alternative": a pool term is an answer a segment reaches
        group = support.group(qid="qg", points="5", choose_n=2, alternatives=("2", "2"),
                              credit={"mode": "capped"})
        alternative_ids = tuple(a["id"] for a in group["alternatives"])  # type: ignore[attr-defined]
        bundle = support.bundle([support.question("q1"), group],
                                support.key_for(("q1",) + alternative_ids))
        assessment = bundle["assessment"]
        assert isinstance(assessment, dict)
        assessment["scope"] = scope()
        assessment["sources"] = [SOURCE]
        assessment["coverage"] = {
            "assessed": [{"segment_id": "seg1", "question_ids": ["q1", "qg_a1"]}]
        }
        self.assertEqual(run(bundle), [])


if __name__ == "__main__":
    unittest.main()
