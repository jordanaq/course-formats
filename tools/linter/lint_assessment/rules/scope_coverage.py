"""Scope, tiers, gating, floors and the coverage audit (§2.6, §2.7).

These belong together because they are one chain of reference: a floor names a tier, a tier
lives on a source, a tier is only meaningful against a scope, and a coverage entry names a
scope segment. A linter that checked each in isolation would accept every document whose
references dangle consistently.

The boundary this module keeps: it judges the *declarations* — shares are exact and in
range, tiers exist, a mastery floor has a gate — while the grounding arithmetic that decides
whether a paper's points reach a floor (§2.6.4's worst legal selection) belongs to the
harness and, for recorded grades, to the report rule. A linter cannot compute a share from a
bundle's keys without also owning the locator rules, so it does not pretend to.
"""
from __future__ import annotations

from typing import Iterator

from .. import jsonview, rationals
from ..diagnostics import Diagnostic, error
from ..document import Bundle
from ..jsonview import JsonObject

#: §2.7's omission reasons.
OMISSION_REASONS: frozenset[str] = frozenset({"time", "scope", "redundant", "deferred"})
#: §2.6.3's gate applies_to values.
FLOOR_SCOPES: frozenset[str] = frozenset({"mastery", "all"})
#: §2.6.2's tier vocabulary.
TIERS: frozenset[str] = frozenset({"required", "extension", "supplemental"})
#: §2.6.2's category vocabulary.
CATEGORIES: frozenset[str] = frozenset({"primary", "secondary"})
#: §2.6.3's gate modes.
GATE_MODES: frozenset[str] = frozenset({"completion", "score"})


def _share_ok(text: str | None) -> bool:
    """True when `text` is a canonical rational in `(0, 1]` (§2.6.1, §8 check 12)."""
    value = rationals.parse(text) if text is not None else None
    return value is not None and 0 < value <= 1


def scope(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing.

    Ensures: an `error` when `scope` is present without a `course.id`, without a nonempty
    `segments` array, or with duplicate segment ids; and an `error` when `coverage` or
    `floors` are present without a `scope`, since both are expressed in segment terms.
    """
    assessment = bundle.assessment
    if assessment is None:
        return
    block = jsonview.get_object(assessment, "scope")
    if block is None:
        if "scope" in assessment:
            yield error("scope", "$.assessment.scope", "scope must be an object (§2.6.1)")
        if "coverage" in assessment:
            yield error(
                "scope",
                "$.assessment.coverage",
                "coverage is expressed in scope segments, so it needs a `scope` (§2.7)",
            )
        if "floors" in assessment:
            yield error(
                "scope",
                "$.assessment.floors",
                "floors are shares of points grounded in a tier, so they need a `scope` "
                "and its sources (§2.6.4)",
            )
        return
    course = jsonview.get_object(block, "course")
    if course is None or jsonview.get_str(course, "id") is None:
        yield error(
            "scope", "$.assessment.scope.course", "scope must name a `course.id` (§2.6.1)"
        )
    segments = jsonview.get_array(block, "segments")
    if segments is None or not segments:
        yield error(
            "scope",
            "$.assessment.scope.segments",
            "scope must carry at least one segment (§2.6.1)",
        )
        return
    seen: set[str] = set()
    for index, item in enumerate(segments):
        path = f"$.assessment.scope.segments[{index}]"
        member = jsonview.as_object(item)
        if member is None:
            yield error("scope", path, "a segment must be an object (§2.6.1)")
            continue
        segment_id = jsonview.get_str(member, "id")
        if segment_id is None:
            yield error("scope", f"{path}.id", "a segment must carry a string `id` (§2.6.1)")
            continue
        if segment_id in seen:
            yield error(
                "scope",
                f"{path}.id",
                f"segment id {segment_id!r} is declared twice; coverage would be "
                f"ambiguous (§2.6.1)",
            )
        seen.add(segment_id)


def tiers_and_gate(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing.

    Ensures: an `error` for every source with no `tier`, with a tier outside
    `required | extension | supplemental`, or with a `category` outside
    `primary | secondary`; an `error` when `gate.mode` is present and `mastery` is not
    `true`, when `threshold_share` is present without `mode: "score"`, or when either share
    is outside `(0, 1]` as an exact rational.
    """
    assessment = bundle.assessment
    if assessment is None:
        return
    for index, item in enumerate(jsonview.get_array(assessment, "sources") or []):
        path = f"$.assessment.sources[{index}]"
        member = jsonview.as_object(item)
        if member is None:
            yield error("scope", path, "a source must be an object (§2.6.2)")
            continue
        source_id = jsonview.get_str(member, "id")
        tier = jsonview.get_str(member, "tier")
        if "tier" not in member:
            yield error(
                "scope",
                f"{path}.tier",
                f"source {source_id!r} must declare a `tier`; silence is exactly what "
                f"§2.6.2 exists to stop",
            )
        elif tier is None or tier not in TIERS:
            yield error(
                "scope",
                f"{path}.tier",
                f"source {source_id!r} has tier {tier!r}, not one of {sorted(TIERS)} (§2.6.2)",
            )
        if "category" in member:
            category = jsonview.get_str(member, "category")
            if category is None or category not in CATEGORIES:
                yield error(
                    "scope",
                    f"{path}.category",
                    f"source {source_id!r} has category {category!r}, not one of "
                    f"{sorted(CATEGORIES)} (§2.6.2)",
                )

    gate = jsonview.get_object(assessment, "gate")
    if gate is None:
        if "gate" in assessment:
            yield error("scope", "$.assessment.gate", "gate must be an object (§2.6.3)")
        return
    mastery = gate.get("mastery")
    if not isinstance(mastery, bool):
        yield error(
            "scope",
            "$.assessment.gate.mastery",
            "gate.mastery is required and must be a boolean (§2.6.3)",
        )
        return
    if "mode" not in gate and mastery:
        yield error(
            "scope",
            "$.assessment.gate.mode",
            "gate.mode is required when `mastery` is true (§2.6.3): a gated paper must say "
            "whether completion or a score threshold advances it",
        )
    if "mode" in gate:
        mode = jsonview.get_str(gate, "mode")
        if mode is None or mode not in GATE_MODES:
            yield error(
                "scope",
                "$.assessment.gate.mode",
                f"gate mode {mode!r} is not one of {sorted(GATE_MODES)} (§2.6.3)",
            )
        elif not mastery:
            yield error(
                "scope",
                "$.assessment.gate.mode",
                "a gate mode is meaningless on a paper with `mastery: false` (§2.6.3)",
            )
    if "threshold_share" in gate:
        text = jsonview.get_str(gate, "threshold_share")
        if not _share_ok(text):
            yield error(
                "scope",
                "$.assessment.gate.threshold_share",
                f"threshold_share {text!r} is not an exact share in (0, 1] (§2.6.3)",
            )
        elif jsonview.get_str(gate, "mode") != "score":
            yield error(
                "scope",
                "$.assessment.gate.threshold_share",
                "a threshold is only applied under `mode: \"score\"`; this gate is "
                f"{jsonview.get_str(gate, 'mode')!r} (§2.6.3)",
            )


def floors(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing.

    Ensures: an `error` when a floor names a tier no declared source uses, when two floors
    name the same tier, when a floor's `applies_to` is outside the vocabulary, or when a
    `mastery`-scoped floor exists without `gate.mastery` being `true` (an unenforceable
    floor is a fiction, §8 check 12). The share is judged alone, never as a cross-product
    over groups: whether the paper's points reach it is the harness's §2.6.4 arithmetic.
    """
    assessment = bundle.assessment
    if assessment is None:
        return
    declared = jsonview.get_array(assessment, "floors")
    if declared is None:
        if "floors" in assessment:
            yield error("scope", "$.assessment.floors", "floors must be an array (§2.6.4)")
        return
    used_tiers: set[str] = set()
    for item in jsonview.get_array(assessment, "sources") or []:
        member = jsonview.as_object(item)
        if member is None:
            continue
        tier = jsonview.get_str(member, "tier")
        if tier is not None:
            used_tiers.add(tier)
    gate = jsonview.get_object(assessment, "gate") or {}
    mastery_gate = gate.get("mastery") is True
    seen: set[str] = set()
    for index, item in enumerate(declared):
        path = f"$.assessment.floors[{index}]"
        member = jsonview.as_object(item)
        if member is None:
            yield error("scope", path, "a floor must be an object (§2.6.4)")
            continue
        tier = jsonview.get_str(member, "tier")
        if tier is None or tier not in TIERS:
            yield error(
                "scope",
                f"{path}.tier",
                f"floor tier {tier!r} is not one of {sorted(TIERS)} (§2.6.4)",
            )
            continue
        if tier in seen:
            yield error(
                "scope",
                f"{path}.tier",
                f"a second floor for tier {tier!r}: one share per tier (§2.6.4)",
            )
        seen.add(tier)
        if tier not in used_tiers:
            yield error(
                "scope",
                f"{path}.tier",
                f"floor names tier {tier!r} but no declared source uses it (§8 check 12)",
            )
        share = jsonview.get_str(member, "min_share")
        if not _share_ok(share):
            yield error(
                "scope",
                f"{path}.min_share",
                f"min_share {share!r} is not an exact share in (0, 1] (§2.6.4)",
            )
        applies = jsonview.get_str(member, "applies_to")
        if applies is None or applies not in FLOOR_SCOPES:
            yield error(
                "scope",
                f"{path}.applies_to",
                f"applies_to {applies!r} is not one of {sorted(FLOOR_SCOPES)} (§2.6.4)",
            )
        elif applies == "mastery" and not mastery_gate:
            yield error(
                "scope",
                f"{path}.applies_to",
                "a mastery-scoped floor only binds where `gate.mastery` is true; this "
                "paper declares no mastery gate, so the floor could never be enforced "
                "(§8 check 12)",
            )


def coverage(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing.

    Ensures: an `error` when `coverage.assessed` is absent or empty, when an `assessed[]`
    entry names a segment not in `scope.segments`, when a segment is assessed twice, when a
    `question_ids` member names nothing in the document, when an `omitted[]` entry names an
    unknown segment or a `reason` outside §2.7's vocabulary, or when an omission carries no
    `topic`. Never compares coverage against a floor or a quota: coverage observes, it does
    not enforce (§2.7).
    """
    assessment = bundle.assessment
    if assessment is None or "coverage" not in assessment:
        return
    block = jsonview.get_object(assessment, "coverage")
    if block is None:
        yield error("coverage", "$.assessment.coverage", "coverage must be an object (§2.7)")
        return
    scope_block = jsonview.get_object(assessment, "scope") or {}
    segment_ids: set[str] = set()
    for item in jsonview.get_array(scope_block, "segments") or []:
        member = jsonview.as_object(item)
        if member is None:
            continue
        segment_id = jsonview.get_str(member, "id")
        if segment_id is not None:
            segment_ids.add(segment_id)
    # §2.7 says a coverage entry names "a question or alternative": a pool term and an
    # essay choice are both legitimate answers to cite, so both id spaces are accepted.
    question_ids = {question.id for question in bundle.questions() if question.id is not None}
    for question in bundle.questions():
        for alternative in question.alternatives():
            if alternative.id is not None:
                question_ids.add(alternative.id)

    assessed = jsonview.get_array(block, "assessed")
    if assessed is None or not assessed:
        yield error(
            "coverage",
            "$.assessment.coverage.assessed",
            "coverage must assess at least one segment; an empty audit says nothing (§2.7)",
        )
        assessed = []
    seen: set[str] = set()
    for index, item in enumerate(assessed):
        path = f"$.assessment.coverage.assessed[{index}]"
        member = jsonview.as_object(item)
        if member is None:
            yield error("coverage", path, "an assessed entry must be an object (§2.7)")
            continue
        segment_id = jsonview.get_str(member, "segment_id")
        if segment_id is None or segment_id not in segment_ids:
            yield error(
                "coverage",
                f"{path}.segment_id",
                f"assessed segment {segment_id!r} is not a declared scope segment (§2.7)",
            )
        elif segment_id in seen:
            yield error(
                "coverage",
                f"{path}.segment_id",
                f"segment {segment_id!r} is assessed twice (§2.7)",
            )
        else:
            seen.add(segment_id)
        cited = jsonview.get_array(member, "question_ids")
        if cited is None or not cited:
            yield error(
                "coverage",
                f"{path}.question_ids",
                "an assessed segment must name the questions that test it (§2.7)",
            )
            continue
        for position, cited_id in enumerate(cited):
            text = jsonview.as_str(cited_id)
            if text is None or text not in question_ids:
                yield error(
                    "coverage",
                    f"{path}.question_ids[{position}]",
                    f"coverage cites {text!r}, which names no question in this document "
                    f"(§8 check 13)",
                )

    for index, item in enumerate(jsonview.get_array(block, "omitted") or []):
        path = f"$.assessment.coverage.omitted[{index}]"
        member = jsonview.as_object(item)
        if member is None:
            yield error("coverage", path, "an omission must be an object (§2.7)")
            continue
        if "segment_id" in member:
            segment_id = jsonview.get_str(member, "segment_id")
            if segment_id is None or segment_id not in segment_ids:
                yield error(
                    "coverage",
                    f"{path}.segment_id",
                    f"omitted segment {segment_id!r} is not a declared scope segment (§2.7)",
                )
        reason = jsonview.get_str(member, "reason")
        if "reason" in member and (reason is None or reason not in OMISSION_REASONS):
            yield error(
                "coverage",
                f"{path}.reason",
                f"omission reason {reason!r} is not one of {sorted(OMISSION_REASONS)} (§2.7)",
            )
        topic = jsonview.get_str(member, "topic")
        if topic is None or not topic.strip():
            yield error(
                "coverage",
                f"{path}.topic",
                "an omission must name the topic it omits; an anonymous omission hides "
                "what was cut (§2.7)",
            )


def check(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing.

    Ensures: `scope`, `tiers_and_gate`, `floors`, `coverage` — in that order, since each
    later rule presumes the earlier one's references exist.
    """
    yield from scope(bundle)
    yield from tiers_and_gate(bundle)
    yield from floors(bundle)
    yield from coverage(bundle)
