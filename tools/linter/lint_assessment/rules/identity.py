"""Identity and answer-key coverage (§2.1, §2.4.6, §8 checks 1 and 9).

Two facts, one module: every id is unique across the whole document, and every question or
alternative that can be answered has exactly one key entry, with no orphan entries. They sit
together because they fail together — a duplicated id and a misdirected key entry look like
one bug from a reader's side.
"""
from __future__ import annotations

from typing import Iterator

from ..diagnostics import Diagnostic, error
from ..document import Bundle


def duplicate_ids(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing.

    Ensures: one `error` per id that is declared more than once anywhere in the document
    (sources, sections, questions, alternatives, criteria share one id space, §2.1), naming
    the id and the kinds that collided. Reports each id once, not once per occurrence.
    """
    seen: dict[str, list[tuple[str, str]]] = {}
    for declared, kind, path in bundle.all_ids():
        seen.setdefault(declared, []).append((kind, path))
    for declared, places in seen.items():
        if len(places) < 2:
            continue
        kinds = ", ".join(sorted({kind for kind, _ in places}))
        yield error(
            "identity",
            places[0][1],
            f"id {declared!r} is declared {len(places)} times ({kinds}); "
            f"ids share one space across sources, sections, questions, alternatives and "
            f"criteria (§2.1)",
        )


def key_coverage(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing.

    Ensures: an `error` for every answerable question or alternative with no key entry, for
    every key entry naming nothing in the document, and for a group that carries its own
    key entry (a group has no answer of its own, §2.4.5). A question whose `type` is
    missing or unknown is not reported here — that is `points`' business — and the absence
    of a key entry for it is not reported either, to avoid one defect becoming two.
    """
    answerable: dict[str, str] = {}
    groups: dict[str, str] = {}
    for section in bundle.sections():
        for question in section.questions():
            question_id = question.id
            if question_id is None:
                continue
            if question.is_group:
                groups[question_id] = question.path
                for alternative in question.alternatives():
                    if alternative.id is not None:
                        answerable[alternative.id] = alternative.path
            elif question.type is not None:
                answerable[question_id] = question.path

    key = bundle.answer_key
    for owner_id, path in answerable.items():
        if owner_id not in key:
            yield error(
                "identity",
                path,
                f"{owner_id!r} is answerable but has no answer-key entry (§2.4.6)",
            )
    known = set(answerable) | set(groups)
    for owner_id in key:
        if owner_id in groups:
            yield error(
                "identity",
                f"$.answer_key['{owner_id}']",
                f"{owner_id!r} is an alternative_set and has no answer of its own; "
                f"its alternatives carry the key entries (§2.4.5)",
            )
        elif owner_id not in known:
            yield error(
                "identity",
                f"$.answer_key['{owner_id}']",
                f"answer-key entry {owner_id!r} names no question or alternative in the "
                f"document (§8 check 9)",
            )


def check(bundle: Bundle) -> Iterator[Diagnostic]:
    """Requires: nothing. Ensures: `duplicate_ids` then `key_coverage`, in that order."""
    yield from duplicate_ids(bundle)
    yield from key_coverage(bundle)
