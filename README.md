# course-formats

Canonical source for course formats and their linters, consumed by the Obsidian vault,
`assessment-cli`, and `course-organizer`.

Current scope: the assessment bundle, submission, and course-structure formats. The
course-structure spec is prose only for now; its schema and linter are still to move.

This repository is the **provenance authority**: a release here names the exact prose, JSON
Schema, and fixtures that downstream repositories consume. Consumers vendor a release as a git
submodule pinned to a tag; they do not keep editable copies.

[`ERRATA.md`](ERRATA.md) holds the canonical list of conflicts found inside the formats, their
resolution, and the items deliberately left open. App-specific profiles and fixture conversions
stay in the consuming repositories.

## Canonicality

- **Schemas are canonical for structure.** `schemas/*.schema.json`, at the tag consumers pin,
  is the file programs read and validate against. Edit the schema first.
- **Specs carry the normative prose.** They remain the authority for rules a schema cannot
  express: exact rational arithmetic, word counting, timing, rendering, privacy, and awards.
- The specs currently embed copies of the schemas in fenced JSON blocks. Until the generator
  lands, those blocks must be kept identical to the canonical schema files by hand.
  `tools/release-check/` fails a release whose embedded block has drifted.
- Payload `format_version` consts remain in the schemas and documents. They are part of the
  format, not a filename or repository convention.

## Versioning

- One release pairs an assessment bundle format with a submission specification revision and
  a course-structure revision. `v0.12.2` pairs assessment `0.12.1`, submission `0.5`, and
  course `0.1.11`. `v0.12.3` keeps that pairing and adds the `studentVisible` projection
  annotations to the assessment-bundle schema; the bundle format is unchanged, so consumer
  pins stay at `v0.12.2` until they adopt the annotations.
- From `v0.13.0`, a release is a **tag plus a manifest**. The artifacts live once, at the
  repository root, and `releases/<release>/manifest.json` records the format pairing and the
  SHA-256 pins; the tag's tree is what makes the release immutable. `v0.12.0`–`v0.12.2` keep
  their full directory copies as history, and `v0.12.3`'s copies remain in its tag.
- Artifact filenames are deliberately unversioned; paths are stable across releases, and
  `manifest.json` is where a consumer learns them.
- Releases are immutable. A change produces a new tag and a new manifest, never an edit to an
  existing one.

## Layout

```
schemas/                  # canonical machine-readable structure
specs/                    # normative prose (current: embeds schema copies)
fixtures/                 # examples, worked examples, conformance vectors
releases/<release>/       # manifest.json only, from v0.13.0 on:
                          #   formats, artifact paths, SHA-256 pins
ERRATA.md                 # conflicts inside the formats, resolved and open
tools/
  linter/                 # cross-check oracle; not part of a release
  release-check/          # manifest pins, schema meta-validation, vector counts, spec drift
```

## Consumers

| Repository | Role | Status |
| --- | --- | --- |
| `assessment-cli` | reads schemas and fixtures; validates bundles and submissions | submodule at `vendor/course-formats`, `v0.12.2` |
| `~/Documents/Obsidian-Vault` | reads the normative specs and linter | submodule at `Agents/Design/course-formats`; current specs and linter are symlinks into it |
| `course-organizer` | reads the schemas and specs | submodule at `vendor/course-formats`, `v0.12.2` |

Consumers pin the release tag. Update by checking out a newer tag in the submodule and
committing the new gitlink. Paths come from the pinned `manifest.json`; from `v0.13.0` they
are root-relative (`schemas/…`, `specs/…`, `fixtures/…`), before it they are
`releases/<release>/…`.

## Tooling

`tools/release-check/check_release.py` gates a release against itself: manifest fields, pins vs
the checked tree, Draft 2020-12 meta-validation, conformance-vector counts, and it fails when a
spec's embedded bundle schema has drifted from the canonical file. Run it before tagging, and
against any tag afterwards:

```
python3 tools/release-check/check_release.py                     # the working tree
python3 tools/release-check/check_release.py releases/v0.12.2/manifest.json --ref v0.12.2
```

`tools/linter/` is the Python cross-check linter copied from the vault. It is **not
release-gating** and is currently out of date:

- It scrapes schemas from fenced markdown blocks instead of reading the canonical schema files.
- Its `latest_spec` logic expects versioned filenames (`assessment-format-spec-vX.Y.Z.md`),
  which this repository no longer uses.

Fix these when the linter is brought back into service. The current release does not depend on
it. The course linter (`course_lint.py`) still lives in the vault and is not yet part of this
repository.

## Known pending work

1. Generate the specs' embedded schema blocks from `schemas/` and fail on drift (the check half
   exists in `tools/release-check/`).
2. Add the prose-example test: extract the current appendix bundles into fixtures and validate
   them alongside the schema.
3. Move the course linter and its fixtures here; then resolve C01–C05 and the stale submission
   v0.3 citation the course spec still carries.
4. Resolve the open errata in [`ERRATA.md`](ERRATA.md): ignored over-answer word checks,
   pending-locator wording, and rubric prose caps.
5. The vault's build/verify scripts stay in the vault for now.
