"""The specs as a source of truth: version and the JSON schemas.

The linter never embeds a copy of a schema. It reads the specs the same way a reader does —
fenced `json` blocks whose `title` names the document type — so a spec revision changes the
linter's verdicts without changing its code, and a typo in a spec is a lint failure rather
than a silent divergence.

From 0.12.0 the two documents a run needs live in two files: the bundle schema in
`assessment-format-spec-vX.md`, the submission schema in `submission-format-spec-vY.md`. The
report schema no longer exists anywhere — 0.12.0 moved the grading record into the
submission — so `Schemas.report` is optional and `None` in every current run.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

from .jsonview import JsonObject


#: A fenced `json` block in the spec's markdown (§1.1 keeps the schemas there).
BLOCK = re.compile(r"```json\n(.*?)\n```\n", re.S)
#: The version a schema pins, wherever the spec states it (§1.1 says it three times).
VERSION_CONST = re.compile(r'"format_version":\s*\{\s*"const":\s*"([^"]+)"')
#: A spec file's name, with its version split into components so they compare numerically.
SPEC_FILE = re.compile(r"assessment-format-spec-v(\d+)\.(\d+)(?:\.(\d+))?\.md$")
#: The submission spec's name, same comparison. It carries the other half of the shapes.
SUBMISSION_SPEC_FILE = re.compile(r"submission-format-spec-v(\d+)\.(\d+)(?:\.(\d+))?\.md$")


@dataclass(frozen=True)
class Schemas:
    """The Draft 2020-12 schemas a run validates against, plus the version they pin.

    Invariants:
        * `version` equals the `format_version` const both schemas require (§1.1): the two
          specs state it and must agree, so it is read once here and compared by the
          `schema` rule.
        * `report` is `None` from 0.11.3 onward — no current spec defines a report, and a
          run that demanded one would be reading a document the specs retired.
    """

    bundle: JsonObject
    submission: JsonObject
    report: JsonObject | None
    version: str


def find_blocks(text: str) -> tuple[str, ...]:
    """Requires: `text` is the spec's markdown.

    Ensures: the body of every fenced `json` block, in document order, with the closing
    fence removed. A block that is not valid JSON is still returned — deciding what a
    broken block means is `load_schemas`' business, not the scanner's.
    """
    return tuple(match.group(1) for match in BLOCK.finditer(text))


def load_schemas(text: str, submission_text: str | None = None) -> Schemas | None:
    """Requires: `text` is the bundle spec's markdown; `submission_text`, when given, is the
    submission spec's markdown.

    Ensures: the schemas named by `title` (`… Bundle vX`, `… Submission vY`) and the version
    they pin; `None` if a schema a run needs is missing, is not an object, or if two
    documents disagree about the version. A `… Report` block is loaded when a spec still
    carries one (0.11.x) and left `None` otherwise — 0.12.0 has no report to validate.
    Returns `None` rather than raising, because "a spec is unreadable" is a fact about the
    input.
    """
    found: dict[str, JsonObject] = {}
    for source in (text,) if submission_text is None else (text, submission_text):
        for body in find_blocks(source):
            try:
                block = json.loads(body)
            except json.JSONDecodeError:
                continue
            if not isinstance(block, dict):
                continue
            title = block.get("title")
            if not isinstance(title, str):
                continue
            for kind in ("Bundle", "Submission", "Report"):
                if kind in title:
                    found.setdefault(kind, block)
    if "Bundle" not in found or "Submission" not in found:
        return None
    required: tuple[JsonObject, ...] = (found["Bundle"], found["Submission"])
    if "Report" in found:
        required = (*required, found["Report"])
    versions = {
        match.group(1)
        for match in (VERSION_CONST.search(json.dumps(block)) for block in required)
        if match is not None
    }
    if len(versions) != 1:
        return None
    version = versions.pop()
    return Schemas(
        bundle=found["Bundle"],
        submission=found["Submission"],
        report=found.get("Report"),
        version=version,
    )


def read_text(path: str) -> str | None:
    """Requires: `path` is a filesystem path.

    Ensures: the file's text, or `None` when it cannot be read. This is the package's one
    permitted exception site: a missing or unreadable file is a caller error, not a
    document defect, and it must not propagate as a traceback into a lint report.
    """
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return None


def latest_spec(directory: str) -> str | None:
    """Requires: `directory` is a filesystem path.

    Ensures: the path of the newest spec file in `directory`, compared as **numeric** version
    components, or `None` when the directory holds none. A name-based choice (or a string
    sort) turns every version bump into a failure that says nothing about the code: `v0.11.10`
    sorts before `v0.11.9`, and a pinned filename goes stale the moment a version ships.
    """
    best: tuple[tuple[int, ...], str] | None = None
    try:
        names = os.listdir(directory)
    except OSError:
        return None
    for name in names:
        match = SPEC_FILE.match(name)
        if match is None:
            continue
        version = tuple(int(part) if part is not None else 0 for part in match.groups())
        path = os.path.join(directory, name)
        if best is None or version > best[0]:
            best = (version, path)
    return best[1] if best is not None else None

def latest_submission_spec(directory: str) -> str | None:
    """Requires: `directory` is a filesystem path.

    Ensures: the path of the newest `submission-format-spec-v*.md` in `directory`, compared as
    numeric version components, or `None` when the directory holds none. Same reasoning as
    `latest_spec`: a pinned filename goes stale on the next bump.
    """
    best: tuple[tuple[int, ...], str] | None = None
    try:
        names = os.listdir(directory)
    except OSError:
        return None
    for name in names:
        match = SUBMISSION_SPEC_FILE.match(name)
        if match is None:
            continue
        version = tuple(int(part) if part is not None else 0 for part in match.groups())
        path = os.path.join(directory, name)
        if best is None or version > best[0]:
            best = (version, path)
    return best[1] if best is not None else None
