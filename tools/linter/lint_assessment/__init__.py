"""A document linter for the assessment format (§0.11.0).

The package is a skeleton with contracts: read `../README.md` for the module map and the two
rules the code is written under — check before acting, and types checked rather than hoped
for.
"""
from __future__ import annotations

from .diagnostics import Diagnostic, RuleId, Severity
from .lint import LintResult, lint_bundle, lint_submission
from .spec import Schemas, load_schemas

__all__ = [
    "Diagnostic",
    "LintResult",
    "RuleId",
    "Schemas",
    "Severity",
    "lint_bundle",
    "lint_submission",
    "load_schemas",
]
