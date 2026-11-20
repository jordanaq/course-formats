"""Command-line entry point — the package's only impure boundary.

Everything below this module returns values; this module talks to the filesystem, prints, and
chooses an exit status. That split is what makes every rule testable without a temp file, and
it confines the package's `try` blocks to the two places where the input is a *file*: reading
it, and parsing it as JSON. Neither case is a document anomaly — a missing file is a caller
error — so neither one becomes a traceback or a finding.

    lint_assessment BUNDLE [--submission SUB] [--spec SPEC] [--submission-spec SPEC] [--json]

Exit status:
    0   conforming (warnings allowed — they describe a conforming document)
    1   one or more errors
    2   a file could not be read, an argument is unusable, or a spec is missing a schema
"""
from __future__ import annotations

import json
import os
import sys

from .diagnostics import Diagnostic
from .document import Bundle
from .jsonview import JsonObject
from .lint import lint_bundle, lint_submission
from .rules.submission import digest_of
from .spec import Schemas, latest_spec, latest_submission_spec, load_schemas, read_text

USAGE = (
    "usage: lint_assessment BUNDLE [--submission SUB] [--spec SPEC] "
    "[--submission-spec SPEC] [--json]"
)

#: The vault's design directory: where both spec families live, beside this package.
DESIGN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#: The newest spec in that directory, resolved by version. Pinning a filename here would put
#: a version bump on the critical path of every lint run, so the version is discovered.
DEFAULT_SPEC = latest_spec(DESIGN) or os.path.join(DESIGN, "assessment-format-spec.md")

#: The newest submission spec, resolved the same way. Since 0.12.0 it holds the submission
#: schema — the bundle spec deliberately no longer carries one.
DEFAULT_SUBMISSION_SPEC = latest_submission_spec(DESIGN) or os.path.join(
    DESIGN, "submission-format-spec.md"
)


def format_text(diagnostics: tuple[Diagnostic, ...]) -> str:
    """Requires: nothing.

    Ensures: one line per diagnostic, `severity rule path: message`, in the order given.
    Empty string for no diagnostics — the caller decides whether silence is a result.
    """
    return "\n".join(
        f"{diagnostic.severity} {diagnostic.rule} {diagnostic.path}: {diagnostic.message}"
        for diagnostic in diagnostics
    )


def format_json(diagnostics: tuple[Diagnostic, ...]) -> str:
    """Requires: nothing.

    Ensures: a JSON array of `{severity, rule, path, message}` objects, in the order given,
    parseable by `json.loads`. Used by the test suite and by anything that wants to diff two
    runs.
    """
    return json.dumps(
        [
            {
                "severity": diagnostic.severity,
                "rule": diagnostic.rule,
                "path": diagnostic.path,
                "message": diagnostic.message,
            }
            for diagnostic in diagnostics
        ],
        indent=2,
    )


def parse_args(argv: list[str]) -> JsonObject | None:
    """Requires: `argv` is the argument vector without the program name.

    Ensures: `{"bundle": str, "submission": str | None, "spec": str,
    "submission_spec": str, "json": bool}` when the arguments are usable, else `None`.
    `--report` is not an option: from 0.12.0 the grading record is inside the submission, so
    naming one is a caller error rather than an ignored flag.
    """
    options: JsonObject = {
        "bundle": None,
        "submission": None,
        "spec": DEFAULT_SPEC,
        "submission_spec": DEFAULT_SUBMISSION_SPEC,
        "json": False,
    }
    positionals: list[str] = []
    index = 0
    while index < len(argv):
        argument = argv[index]
        if argument == "--json":
            options["json"] = True
        elif argument in ("--submission", "--spec", "--submission-spec"):
            if index + 1 >= len(argv):
                return None
            options[argument[2:].replace("-", "_")] = argv[index + 1]
            index += 1
        elif argument.startswith("--"):
            return None
        else:
            positionals.append(argument)
        index += 1
    if len(positionals) != 1:
        return None
    options["bundle"] = positionals[0]
    return options


def _load_json(path: str) -> JsonObject | str:
    """The parsed document, or a message describing why it cannot be parsed.

    Returning a message instead of raising keeps the boundary total: the only failures left
    to the caller are the exit status and the printed line.
    """
    text = read_text(path)
    if text is None:
        return f"cannot read {path}"
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        return f"{path} is not valid JSON: {exc.msg} at line {exc.lineno}"
    if not isinstance(document, dict):
        return f"{path} holds a JSON {type(document).__name__}, not an object"
    return document


def _schemas(options: JsonObject) -> Schemas | str:
    """Requires: `options` carries `spec` and `submission_spec` paths.

    Ensures: the loaded `Schemas`, or a message string when a spec cannot be read or does not
    carry the schema a run needs. Both spec files are read: the bundle schema from the
    assessment spec, the submission schema from the submission spec.
    """
    bundle_text = read_text(str(options["spec"]))
    if bundle_text is None:
        return f"cannot read the spec at {options['spec']}"
    submission_text = read_text(str(options["submission_spec"]))
    if submission_text is None:
        return f"cannot read the submission spec at {options['submission_spec']}"
    schemas = load_schemas(bundle_text, submission_text)
    if schemas is None:
        return (
            f"{options['spec']} and {options['submission_spec']} do not together carry the "
            f"bundle and submission schemas this linter needs, or they disagree about the "
            f"version"
        )
    return schemas


def main(argv: list[str]) -> int:
    """Requires: `argv` is the argument vector **without** the program name.

    Ensures: a documented exit status, having printed either nothing (clean), the formatted
    diagnostics, or one line of usage. Never raises: an unreadable file is status 2 with a
    message, and a document that is not valid JSON is a lintable defect reported as an
    error, not a crash.
    """
    if "--report" in argv:
        print(
            "no --report: from 0.12.0 the grading record is inside the submission "
            "(submission-format-spec-v0.3.md §6); pass --submission only"
        )
        return 2

    options = parse_args(argv)
    if options is None:
        print(USAGE)
        return 2

    schemas = _schemas(options)
    if isinstance(schemas, str):
        print(schemas)
        return 2

    bundle_text = read_text(str(options["bundle"]))
    bundle_document = _load_json(str(options["bundle"]))
    if isinstance(bundle_document, str):
        print(bundle_document)
        return 2
    bundle = Bundle(bundle_document)

    submission_path = options["submission"]
    if submission_path is None:
        diagnostics = lint_bundle(bundle, schemas).diagnostics
    else:
        submission = _load_json(str(submission_path))
        if isinstance(submission, str):
            print(submission)
            return 2
        digest = digest_of(bundle_text) if bundle_text is not None else None
        diagnostics = lint_submission(bundle, submission, schemas, digest).diagnostics

    if options["json"]:
        print(format_json(diagnostics))
    elif diagnostics:
        print(format_text(diagnostics))
    if not diagnostics:
        return 0
    return 0 if not any(d.severity == "error" for d in diagnostics) else 1


if __name__ == "__main__":  # pragma: no cover - exercised through main()
    raise SystemExit(main(sys.argv[1:]))
