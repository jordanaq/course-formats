"""Orchestration: schema pass, then rules, then a stable order.

The pipeline is deliberately dumb and total:

    parse (caller)  →  schema pass  →  bundle rules  →  report rules  →  sort

Every stage appends to one list. No stage decides whether a later stage may run — a schema
violation does not suppress the semantic rules, because a reader fixing a key wants every
problem at once, not one per run. The only exception to that is inside a rule, where a
malformed field suppresses the rule that would have read it, so one defect yields one
diagnostic rather than three.
"""
from __future__ import annotations

from dataclasses import dataclass

import jsonschema
from jsonschema import Draft202012Validator

from . import projection, rules
from .rules import submission as submission_rules
from .diagnostics import Diagnostic, error
from .document import Bundle
from .jsonview import JsonObject
from .spec import Schemas


#: A total order over diagnostics: severity first (errors before warnings), then rule, then
#: path, then message. Two runs over one document print identically.
_ORDER: dict[str, int] = {
    name: index for index, name in enumerate(
        ("schema", "points", "identity", "credit", "weights", "words", "scope", "coverage",
         "delivery", "submission", "report")
    )
}


def sort_diagnostics(diagnostics: list[Diagnostic]) -> tuple[Diagnostic, ...]:
    """Requires: nothing.

    Ensures: the diagnostics in a stable, documented order — errors before warnings, then by
    rule family, then by path, then by message — so a diff between two runs shows only real
    changes.
    """
    return tuple(
        sorted(
            diagnostics,
            key=lambda d: (
                0 if d.severity == "error" else 1,
                _ORDER.get(d.rule, len(_ORDER)),
                d.path,
                d.message,
            ),
        )
    )


@dataclass(frozen=True)
class LintResult:
    """The outcome of one lint run.

    Invariants:
        * `diagnostics` is sorted by `(severity, rule, path)`, so two runs over the same
          inputs print identically.
        * `ok` is true exactly when no diagnostic has severity `error`. Warnings do not make
          a document non-conforming — they describe a conforming document that will
          disappoint someone (§8 check 15).
    """

    diagnostics: tuple[Diagnostic, ...]

    @property
    def errors(self) -> tuple[Diagnostic, ...]:
        """Requires: nothing. Ensures: the `error` diagnostics, in order."""
        return tuple(d for d in self.diagnostics if d.severity == "error")

    @property
    def warnings(self) -> tuple[Diagnostic, ...]:
        """Requires: nothing. Ensures: the `warning` diagnostics, in order."""
        return tuple(d for d in self.diagnostics if d.severity == "warning")

    @property
    def ok(self) -> bool:
        """Requires: nothing. Ensures: `True` exactly when `errors` is empty."""
        return not any(d.severity == "error" for d in self.diagnostics)


def check_schema(schemas: Schemas, kind: str, document: JsonObject) -> list[Diagnostic]:
    """Requires: `kind` is `"bundle"`, `"submission"` or `"report"`.

    Ensures: one `error` per schema violation, each carrying the JSON path of the offending
    instance — a schema verdict a person cannot locate is not a usable diagnostic. Never
    raises: an unreadable schema is one diagnostic, not a traceback.
    """
    schema = {"bundle": schemas.bundle, "submission": schemas.submission,
              "report": schemas.report}.get(kind)
    if schema is None:
        return [error("schema", "$", f"no {kind} schema was extracted from the spec")]
    validator = Draft202012Validator(schema)
    out: list[Diagnostic] = []
    for violation in validator.iter_errors(document):
        path = "$" + "".join(
            f"[{part}]" if isinstance(part, int) else f".{part}"
            for part in violation.absolute_path
        )
        out.append(error("schema", path, violation.message))
    return sorted(out, key=lambda d: (d.path, d.message))


def lint_bundle(bundle: Bundle, schemas: Schemas) -> LintResult:
    """Requires: `bundle` is a parsed bundle; `schemas` came from the same spec version.

    Ensures: the schema pass plus every bundle rule, sorted, with a version-mismatch `error`
    when `bundle.format_version` differs from `schemas.version`. Total: any document that
    parsed yields a result.
    """
    out = check_schema(schemas, "bundle", bundle.raw)
    if bundle.format_version != schemas.version:
        out.append(
            error(
                "schema",
                "$.format_version",
                f"this document declares {bundle.format_version!r} but the spec beside it "
                f"is {schemas.version!r}; a lint run is only meaningful against the "
                f"version it names",
            )
        )
    for _, rule in rules.bundle_rules():
        out.extend(rule(bundle))
    return LintResult(diagnostics=sort_diagnostics(out))


def lint_submission(
    bundle: Bundle, submission: JsonObject, schemas: Schemas, digest: str | None = None
) -> LintResult:
    """Requires: `bundle` and `submission` are parsed objects; `schemas` came from the specs
    beside them.

    Ensures: `lint_bundle`'s diagnostics, the submission's schema pass, the submission rules
    (§8 of the submission spec: who, which paper, coverage, shapes, feedback, grading state,
    graders), and every report rule run against the projection in `projection.py`. From 0.12.0
    the grading record is *inside* the submission, so the arithmetic rules are applied to a
    projection rather than a second document; `digest`, when the caller knows the bundle's
    bytes, lets `paper.sha256` be compared. A report schema, when an 0.11.x spec still
    supplies one, is not consulted — no document in a 0.12.0 run is a report.
    """
    out = list(lint_bundle(bundle, schemas).diagnostics)
    out.extend(check_schema(schemas, "submission", submission))
    out.extend(submission_rules.check(bundle, submission, digest))
    projected_submission = projection.legacy_submission(submission)
    projected_report = projection.as_report(submission)
    for _, rule in rules.report_rules():
        out.extend(rule(bundle, projected_submission, projected_report))
    return LintResult(diagnostics=sort_diagnostics(out))
