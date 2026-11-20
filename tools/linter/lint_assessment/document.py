"""Read-only typed views over a parsed bundle.

The bundle is a tree with four levels that every rule walks — assessment → sections →
questions → alternatives — plus the flat answer-key map. This module is the one place that
knows how to walk it, and it walks it **totally**: iterators skip members that are not
objects, and the accessors return `None` rather than raising. A rule that needs to *report*
a malformed member asks the view for it and compares against `None`.

Nothing here mutates: a view is a lens over the caller's `JsonObject`, not a copy, so a
diagnostic path computed here always names a location in the document the caller passed in.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterator

from . import jsonview, rationals
from .jsonview import JsonObject

#: Question types that carry options and a machine-checkable answer (§2.2).
CHOICE_TYPES: frozenset[str] = frozenset({"single_choice", "multiple_select"})
#: Question types answered in prose.
WRITTEN_TYPES: frozenset[str] = frozenset({"short_answer", "essay"})
#: The credit modes of §2.4.2. Absence means `equal`.
CREDIT_MODES: frozenset[str] = frozenset({"equal", "capped"})


@dataclass(frozen=True)
class Alternative:
    """One alternative of a group, or the single body of an ordinary question."""

    raw: JsonObject
    path: str

    @property
    def id(self) -> str | None:
        """Requires: nothing. Ensures: the alternative's id, or `None` if absent/invalid."""
        return jsonview.get_str(self.raw, "id")

    @property
    def points(self) -> str | None:
        """Requires: nothing. Ensures: the raw `points` string, or `None`."""
        return jsonview.get_str(self.raw, "points")

    @property
    def type(self) -> str | None:
        """Requires: nothing. Ensures: the declared `type`, or `None`."""
        return jsonview.get_str(self.raw, "type")


@dataclass(frozen=True)
class Question:
    """One member of `sections[].questions[]` — an ordinary question or a group."""

    raw: JsonObject
    path: str

    @property
    def id(self) -> str | None:
        """Requires: nothing. Ensures: the question's id, or `None`."""
        return jsonview.get_str(self.raw, "id")

    @property
    def type(self) -> str | None:
        """Requires: nothing. Ensures: the declared `type`, or `None`."""
        return jsonview.get_str(self.raw, "type")

    @property
    def points(self) -> str | None:
        """Requires: nothing. Ensures: the raw `points` string, or `None`."""
        return jsonview.get_str(self.raw, "points")

    @property
    def is_group(self) -> bool:
        """Requires: nothing.

        Ensures: `True` exactly when `type == "alternative_set"`. Established by the type
        alone, never by the presence of `alternatives` — a malformed document must not be
        able to change which rules run.
        """
        return self.type == "alternative_set"

    @property
    def credit_mode(self) -> str | None:
        """Requires: nothing.

        Ensures: the declared credit mode, `"equal"` when `credit` is absent (§2.4.2),
        or `None` when `credit` is present but not an object or `mode` is not a string.
        A caller distinguishes "absent means equal" from "present but broken" by
        `credit_mode is None` versus the raw `credit` member.
        """
        if "credit" not in self.raw:
            return "equal"
        credit = jsonview.get_object(self.raw, "credit")
        if credit is None:
            return None
        return jsonview.get_str(credit, "mode")

    def alternatives(self) -> Iterator[Alternative]:
        """Requires: nothing.

        Ensures: every alternative of a group, in the paper's order, as `Alternative`
        views with paths rooted at this question's path. Yields nothing for a non-group.
        """
        if not self.is_group:
            return
        items = jsonview.get_array(self.raw, "alternatives") or []
        for index, item in enumerate(items):
            member = jsonview.as_object(item)
            if member is None:
                continue
            yield Alternative(raw=member, path=f"{self.path}.alternatives[{index}]")

    @property
    def choose_n(self) -> int | None:
        """Requires: nothing. Ensures: `choose_n` when it is an integer, else `None`."""
        return jsonview.get_int(self.raw, "choose_n")

    def points_value(self) -> Fraction | None:
        """Requires: nothing.

        Ensures: the question's points as an exact value, or `None` when the string is
        absent or not canonical.
        """
        text = self.points
        if text is None:
            return None
        return rationals.parse(text)


@dataclass(frozen=True)
class Section:
    """One member of `sections[]`."""

    raw: JsonObject
    path: str

    @property
    def id(self) -> str | None:
        """Requires: nothing. Ensures: the section's id, or `None`."""
        return jsonview.get_str(self.raw, "id")

    def questions(self) -> Iterator[Question]:
        """Requires: nothing. Ensures: the section's questions in order."""
        items = jsonview.get_array(self.raw, "questions") or []
        for index, item in enumerate(items):
            member = jsonview.as_object(item)
            if member is None:
                continue
            yield Question(raw=member, path=f"{self.path}.questions[{index}]")


@dataclass(frozen=True)
class Bundle:
    """A parsed assessment bundle, viewed read-only."""

    raw: JsonObject

    @property
    def format_version(self) -> str | None:
        """Requires: nothing. Ensures: the declared `format_version`, or `None`."""
        return jsonview.get_str(self.raw, "format_version")

    @property
    def assessment(self) -> JsonObject | None:
        """Requires: nothing. Ensures: the `assessment` object, or `None`."""
        return jsonview.get_object(self.raw, "assessment")

    def sections(self) -> Iterator[Section]:
        """Requires: nothing. Ensures: the assessment's sections in order."""
        assessment = self.assessment
        if assessment is None:
            return
        items = jsonview.get_array(assessment, "sections") or []
        for index, item in enumerate(items):
            member = jsonview.as_object(item)
            if member is None:
                continue
            yield Section(raw=member, path=f"$.assessment.sections[{index}]")

    def questions(self) -> Iterator[Question]:
        """Requires: nothing.

        Ensures: every question in document order, flattened across sections — the order
        §6 requires of a report's results.
        """
        for section in self.sections():
            yield from section.questions()

    @property
    def answer_key(self) -> JsonObject:
        """Requires: nothing.

        Ensures: the answer-key map, or an empty map when the member is absent or not an
        object — so a rule never has to test for it before iterating.
        """
        return jsonview.get_object(self.raw, "answer_key") or {}

    def key_entry(self, owner_id: str) -> JsonObject | None:
        """Requires: `owner_id` is a question or alternative id.

        Ensures: that owner's key entry, or `None` when there is none.
        """
        return jsonview.as_object(self.answer_key.get(owner_id))

    def all_ids(self) -> Iterator[tuple[str, str, str]]:
        """Requires: nothing.

        Ensures: `(id, kind, path)` for every id the bundle declares, where `kind` is one
        of `source`, `section`, `question`, `alternative`, `criterion`, in document order.
        Ids that are absent or not strings are skipped — reporting them is `identity`'s
        job, and it can only do that if this walk does not fail on them.
        """
        assessment = self.assessment
        if assessment is None:
            return
        for index, source in enumerate(jsonview.get_array(assessment, "sources") or []):
            member = jsonview.as_object(source)
            if member is None:
                continue
            source_id = jsonview.get_str(member, "id")
            if source_id is not None:
                yield source_id, "source", f"$.assessment.sources[{index}].id"
        for section in self.sections():
            if section.id is not None:
                yield section.id, "section", f"{section.path}.id"
            for question in section.questions():
                if question.id is not None:
                    yield question.id, "question", f"{question.path}.id"
                for alternative in question.alternatives():
                    if alternative.id is not None:
                        yield alternative.id, "alternative", f"{alternative.path}.id"
        for owner_id in self.answer_key:
            entry = self.key_entry(owner_id)
            if entry is None:
                continue
            for index, criterion in enumerate(jsonview.get_array(entry, "criteria") or []):
                member = jsonview.as_object(criterion)
                if member is None:
                    continue
                criterion_id = jsonview.get_str(member, "id")
                if criterion_id is not None:
                    yield (criterion_id, "criterion",
                           f"$.answer_key['{owner_id}'].criteria[{index}].id")
