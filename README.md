# course-formats

Canonical source for course formats and their linters, consumed by the Obsidian vault,
`assessment-cli`, and `course-organizer`.

Current scope: the assessment bundle and submission formats. The repository is intended to
grow to own the course-structure format and the other course linters as well.

This repository is the **provenance authority**: a release here names the exact prose, JSON
Schema, and fixtures that downstream repositories consume. Consumers vendor a release as a git
submodule pinned to a tag; they do not keep editable copies.

## Canonicality

- **Schemas are canonical for structure.** `releases/<release>/schemas/*.schema.json` is the
  file programs read and validate against. Edit the schema first.
- **Specs carry the normative prose.** They remain the authority for rules a schema cannot
  express: exact rational arithmetic, word counting, timing, rendering, privacy, and awards.
- The specs currently embed copies of the schemas in fenced JSON blocks. Until the generator
  lands, those blocks must be kept identical to the canonical schema files by hand. The
  generator and its drift check are the next tooling task.
- Payload `format_version` consts remain in the schemas and documents. They are part of the
  format, not a filename or repository convention.

## Versioning

- One release pairs an assessment bundle format with a submission specification revision.
  `v0.12.0` pairs assessment `0.12.0` with submission `0.4`.
- Release directories, tags, and `manifest.json` carry the version. Artifact filenames are
  deliberately unversioned.
- Releases are immutable. A change produces a new release directory and tag.

## Layout

```
releases/<release>/
  manifest.json           # formats, artifact paths, SHA-256 pins
  schemas/                # canonical machine-readable structure
  specs/                  # normative prose (current: embeds schema copies)
  fixtures/               # examples, worked examples, conformance vectors
tools/
  linter/                 # cross-check oracle; not part of a release
```

## Consumers

| Repository | Role | Status |
| --- | --- | --- |
| `assessment-cli` | reads schemas and fixtures; validates bundles and submissions | submodule pending remote |
| `~/Documents/Obsidian-Vault` | reads the normative specs and linter | submodule pending remote |
| `course-organizer` | reads the schemas and specs | submodule pending remote |

Submodules require an upstream URL. Until this repository is pushed, consumers use a local
checkout.

## Tooling

`tools/linter/` is the Python cross-check linter copied from the vault. It is **not
release-gating** and is currently out of date:

- It scrapes schemas from fenced markdown blocks instead of reading the canonical schema files.
- Its `latest_spec` logic expects versioned filenames (`assessment-format-spec-vX.Y.Z.md`),
  which this repository no longer uses.

Fix these when the linter is brought back into service. The current release does not depend on
it.

## Known pending work

1. Generate the specs' embedded schema blocks from `releases/<release>/schemas/` and fail on drift.
2. Move and adapt the build scripts; they currently assume vault paths and versioned filenames.
3. Reconcile the bundle spec's citations of `submission-format-spec-v0.3.md` with the paired
   submission revision `0.4`.
4. Add the upstream remote, tags, and consumer submodules.
