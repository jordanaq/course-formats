#!/usr/bin/env python3
"""Release check: manifest pins, schema meta-validation, vectors, spec drift.

Requires: run inside the repository. `jsonschema` is importable.
Ensures: one exit status — 0 when the release is internally consistent, 1 otherwise — and one
line per problem, so a broken release fails before it is tagged rather than after a consumer
pins it.

What "consistent" means here, in the order the checks run:

1. the manifest carries the fields a consumer reads (`release`, `formats`, `canonical`,
   `artifacts`, `sha256`), and `sha256` names exactly the artifact paths and nothing else;
2. every pinned digest matches the file at the checked tree — the working tree by default,
   or a git ref with `--ref`, so a tag can be re-checked without checking it out;
3. every `.schema.json` artifact is a valid JSON Schema (Draft 2020-12);
4. the conformance vectors load and their groups are counted (a truncated file is a `json`
   error, a silently emptied one is a count of zero);
5. when the release pins an assessment spec, the bundle schema embedded in that spec's
   fenced JSON blocks is the canonical schema file — the drift that has to be caught by hand
   until the generator lands (ERRATA, "Schema generation and drift").

The check does not decide whether the *content* of a release is right; it decides whether the
release describes itself truthfully.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

FENCED_JSON = re.compile(r"```json\n(.*?)\n```", re.S)
REQUIRED_FIELDS = ("release", "formats", "canonical", "artifacts", "sha256")


class Tree:
    """Requires: `ref` is None for the working tree, or a git ref that resolves.

    Ensures: `read` returns the bytes of `path` at that tree and `text` its UTF-8 decoding.
    """

    def __init__(self, root: Path, ref: str | None) -> None:
        self.root = root
        self.ref = ref

    def read(self, path: str) -> bytes:
        if self.ref is None:
            return (self.root / path).read_bytes()
        return subprocess.run(
            ["git", "-C", str(self.root), "show", f"{self.ref}:{path}"],
            check=True,
            capture_output=True,
        ).stdout

    def text(self, path: str) -> str:
        return self.read(path).decode("utf-8")

    def exists(self, path: str) -> bool:
        if self.ref is None:
            return (self.root / path).is_file()
        return subprocess.run(
            ["git", "-C", str(self.root), "cat-file", "-e", f"{self.ref}:{path}"],
            capture_output=True,
        ).returncode == 0


def artifact_paths(manifest: dict) -> list[str]:
    """Requires: `manifest["artifacts"]` is a mapping of groups to path mappings.

    Ensures: every artifact path named by the manifest, groups flattened, sorted.
    """
    return sorted(
        path
        for group in manifest["artifacts"].values()
        for path in group.values()
    )


def embedded_bundle_schema(spec: str) -> dict | None:
    """Requires: `spec` is the markdown of an assessment-format spec.

    Ensures: the bundle schema from its fenced `json` blocks, or `None` when the spec embeds
    no block titled `Assessment Bundle …`.
    """
    for body in FENCED_JSON.findall(spec):
        try:
            block = json.loads(body)
        except json.JSONDecodeError:
            continue
        if isinstance(block, dict) and "Assessment Bundle" in str(block.get("title", "")):
            return block
    return None


def check(manifest: dict, tree: Tree) -> list[str]:
    """Requires: `manifest` is the parsed manifest of the release `tree` describes.

    Ensures: the problems found, in check order, each naming the artifact it concerns.
    """
    problems: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in manifest:
            problems.append(f"manifest: missing {field!r}")
    if problems:
        return problems

    paths = artifact_paths(manifest)
    pinned = set(manifest["sha256"])
    for path in sorted(set(paths) - pinned):
        problems.append(f"manifest: {path} is an artifact but is not pinned")
    for path in sorted(pinned - set(paths)):
        problems.append(f"manifest: {path} is pinned but is not a declared artifact")

    for path in paths:
        if not tree.exists(path):
            problems.append(f"{path}: missing from the checked tree")
            continue
        digest = hashlib.sha256(tree.read(path)).hexdigest()
        if digest != manifest["sha256"].get(path):
            problems.append(f"{path}: sha256 {digest[:12]}… does not match the pin")

    schemas: dict[str, dict] = {}
    for path in paths:
        if not path.endswith(".schema.json") or not tree.exists(path):
            continue
        try:
            schema = json.loads(tree.text(path))
            Draft202012Validator.check_schema(schema)
            schemas[path] = schema
        except Exception as error:  # noqa: BLE001 — a broken schema is the diagnostic
            problems.append(f"{path}: not a valid Draft 2020-12 schema ({error})")

    vectors = manifest["artifacts"].get("fixtures", {}).get("conformance_vectors")
    if vectors and tree.exists(vectors):
        try:
            groups = json.loads(tree.text(vectors))
            cases = sum(len(value) for value in groups.values() if isinstance(value, list))
            print(f"vectors: {len(groups)} groups, {cases} cases")
            if not groups or not cases:
                problems.append(f"{vectors}: no conformance cases")
        except json.JSONDecodeError as error:
            problems.append(f"{vectors}: not JSON ({error})")

    bundle_path = manifest["artifacts"].get("schemas", {}).get("assessment")
    spec_path = manifest["artifacts"].get("specs", {}).get("assessment")
    if bundle_path in schemas and spec_path and tree.exists(spec_path):
        embedded = embedded_bundle_schema(tree.text(spec_path))
        if embedded is None:
            problems.append(f"{spec_path}: no embedded bundle schema to compare")
        elif embedded != schemas[bundle_path]:
            problems.append(f"{spec_path}: embedded bundle schema has drifted from {bundle_path}")

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check a release manifest against its tree.")
    parser.add_argument(
        "manifest",
        nargs="?",
        default="releases/v0.13.0/manifest.json",
        help="path to the manifest (default: releases/v0.13.0/manifest.json)",
    )
    parser.add_argument(
        "--ref",
        default=None,
        help="check a git ref instead of the working tree (e.g. a release tag)",
    )
    args = parser.parse_args(argv)

    root = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], check=True, capture_output=True, text=True
        ).stdout.strip()
    )
    tree = Tree(root, args.ref)
    manifest = json.loads(tree.text(args.manifest))
    where = args.ref or "working tree"

    problems = check(manifest, tree)
    print(f"release {manifest.get('release', '?')} at {where}: {len(problems)} problem(s)")
    for problem in problems:
        print("  FAIL:", problem)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
