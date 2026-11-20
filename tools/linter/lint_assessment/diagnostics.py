"""Diagnostics: the only vocabulary a rule may report in.

Every check speaks in `Diagnostic` values. A rule does not raise, print, or return a string:
it yields diagnostics, and the orchestrator decides what they mean. That keeps a rule pure
(a document in, diagnostics out) and makes every rule testable without files, streams or
exit codes.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

#: A rule family. One per module under `rules/`, plus the schema and delivery passes.
RuleId = Literal[
    "schema",
    "identity",
    "points",
    "credit",
    "weights",
    "words",
    "scope",
    "coverage",
    "delivery",
    "submission",
    "report",
]

#: `error` means the document is not a conforming document; `warning` means it is
#: conforming but a smell (§8 check 15 is the reason warnings exist at all).
Severity = Literal["error", "warning"]


@dataclass(frozen=True, order=True)
class Diagnostic:
    """One finding, located in the document.

    Invariants:
        * `path` is a location expression rooted at `$` — `$.assessment.sections[0]` —
          and it names a position that exists in the document as parsed, never a
          hypothetical one.
        * `message` states what is wrong, in the document's own vocabulary, and never how
          to fix it: a rule reports violations, it does not author documents.
    """

    severity: Severity
    rule: RuleId
    path: str
    message: str


def error(rule: RuleId, path: str, message: str) -> Diagnostic:
    """Requires: nothing. Ensures: an `error` diagnostic with the given fields."""
    return Diagnostic(severity="error", rule=rule, path=path, message=message)


def warning(rule: RuleId, path: str, message: str) -> Diagnostic:
    """Requires: nothing. Ensures: a `warning` diagnostic with the given fields."""
    return Diagnostic(severity="warning", rule=rule, path=path, message=message)
