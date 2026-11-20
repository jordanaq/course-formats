"""The rule families, and the order they report in.

A rule is a function from a document (or a document triple) to diagnostics. It is pure: no
IO, no printing, no raising. Ordering is fixed here so two runs over the same document
produce byte-identical output — a linter whose output reorders cannot be diffed, and a diff
is how a reader checks that a fix helped.
"""
from __future__ import annotations

from typing import Callable, Iterator, Protocol

from ..diagnostics import Diagnostic
from ..document import Bundle
from ..jsonview import JsonObject
from . import credit, identity, points, report, scope_coverage, weights, words


class BundleRule(Protocol):
    """A rule over the bundle alone."""

    def __call__(self, bundle: Bundle) -> Iterator[Diagnostic]:
        """Requires: `bundle` is a parsed bundle, possibly malformed.

        Ensures: one diagnostic per violation, and none for a conforming document.
        """
        ...


class ReportRule(Protocol):
    """A rule that needs the submission and the report as well as the bundle."""

    def __call__(
        self, bundle: Bundle, submission: JsonObject, report: JsonObject
    ) -> Iterator[Diagnostic]:
        """Requires: the three documents are parsed, possibly malformed.

        Ensures: one diagnostic per violation, and none for a conforming triple.
        """
        ...


#: Bundle rules, in reporting order. The order is not the order they run in — they all run —
#: but it IS the order their diagnostics sort into, so a reader sees structural problems
#: before consequential ones.
BUNDLE_RULES: tuple[tuple[str, BundleRule], ...] = (
    ("points", points.check),
    ("identity", identity.check),
    ("credit", credit.check),
    ("weights", weights.check),
    ("words", words.check),
    ("scope", scope_coverage.check),
)


def _load() -> tuple[tuple[str, BundleRule], ...]:
    """Register the rules once, lazily: the modules import `..document`, never this one."""
    return BUNDLE_RULES


def bundle_rules() -> tuple[tuple[str, BundleRule], ...]:
    """Requires: nothing.

    Ensures: the registered bundle rules, in reporting order. Returns a tuple rather than
    the module-level constant so that registering a rule cannot mutate a collection another
    caller is iterating.
    """
    return _load()


def report_rules() -> tuple[tuple[str, ReportRule], ...]:
    """Requires: nothing. Ensures: the registered report rules, in reporting order."""
    return (("report", report.check),)
