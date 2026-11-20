# Written specification — a document linter for the assessment format

This directory was a **skeleton before it became a program**, and the order is kept: the
structure was fixed first — module boundaries, types, signatures, and a local contract per
callable — and the behaviour was then pinned by module tests against those contracts before
any body was filled. Depth-first: leaf modules (`jsonview`, `rationals`) went green, then
`document`/`spec`, then each rule, then the orchestrator and the CLI.

Current state: **111 tests, 0 failures; `mypy --strict` clean over 16 modules.**

The reason is the one the skeleton-coding paper makes: a set of behavioural tests is only
strong enough for *one* structure. Deciding the structure implicitly, by writing
implementation first and testing afterwards, leaves the contract underspecified and the tests
selecting a program rather than a design. So:

1. `lint_assessment/` — the skeleton: types, signatures, `Requires:` / `Ensures:` /
   `Invariants:` in every docstring, and `raise NotImplementedError` bodies.
2. `tests/` — the behavioural specs, written against the contracts, no knowledge of the
   implementation.
3. Implementation fills the bodies until `tests/` is green and `mypy --strict` is clean.

## Module map

| module | responsibility | may import |
|---|---|---|
| `diagnostics` | `Diagnostic`, `Severity`, `RuleId`; the only vocabulary a rule may report in | — |
| `jsonview` | **total** accessors over parsed JSON: every accessor returns a value or `None`, never raises | `diagnostics` |
| `rationals` | canonical rational strings ↔ `Fraction`, exactly (§2.3.1) | — |
| `document` | read-only typed views: bundle → sections → questions → alternatives → key entries | `jsonview`, `rationals` |
| `spec` | extract the three JSON schemas and the version from the spec document | `jsonview` |
| `rules.*` | one module per rule family (`points`, `identity`, `credit`, `weights`, `words`, `scope`, `report`); each exports `check(...) -> Iterator[Diagnostic]` | `diagnostics`, `jsonview`, `rationals`, `document` |
| `lint` | orchestration: schema pass, then every rule, then ordering | everything |
| `cli` | argv, file IO, exit status; **the only place that may raise** | `lint`, `spec` |

## The two rules this code is written under

**Check before acting, never catch afterwards.** A callable that can meet a malformed
document returns a `Diagnostic` describing the malformation; it does not index into a shape
it has not verified and it does not use exceptions as control flow. `jsonview` exists so that
"is it an object / an array / a string / an int" is one call, returning `None`. There is
exactly one `try` in the package: at the CLI boundary around file IO, because a missing file
is a caller error, not a document defect.

**Types are checked, not hoped for.** `mypy --strict` over `lint_assessment/` is part of the
build; the JSON boundary is typed as `JsonValue` and narrowed through `jsonview`, so no rule
ever holds `Any`.

## Running

```sh
# the dev venv (mypy is not in the system python)
python3 -m venv .venv && .venv/bin/pip -q install mypy
.venv/bin/mypy --strict lint_assessment        # must be clean
python3 -m unittest discover -s tests -v       # must be green

python3 -m lint_assessment.cli <bundle.json>   # exit 0 clean, 1 errors, 2 usage
```
