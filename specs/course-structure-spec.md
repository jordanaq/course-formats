# Course Structure Specification — v0.1.11

**Version:** 0.1.11
**Status:** current
**Frozen:** 2026-11-20
**Supersedes:** `course-structure-spec-v0.1.10.md` (0.1.10, sha256
`62e78b816049546f694955a04ae797cc355ca2ea83b490f1de0c9c7d0a9931a3`, left
byte-identical); 0.1.9, 0.1.8, 0.1.7, 0.1.6, 0.1.5, 0.1.4, 0.1.3, 0.1.2, 0.1.1
and 0.1 are superseded transitively.
**Companion tool:** `Agents/Courses/scripts/course_lint.py` (the executable contract)
**Consumer:** `Agents/Courses/**` in this vault

## Change scope of v0.1.11

The assessment directory's shape changes, and the linter follows it. An assessment is now **one
JSON bundle plus the submissions it collects**; the markdown key and the feedback directory stop
being what the shape is built around:

- **`<directory name>.json` is the exam key.** `Exam 01/Exam 01.json`,
  `Reading Worksheet 01/Reading Worksheet 01.json` — the assessment bundle
  (`assessment-format-spec-v0.11.3.md`), named for the directory that holds it. Absent is
  `missing-exam-bundle` (WARNING): a course mid-migration has untranslated assessments, and that
  is a to-do, not a broken course. Present but not a bundle — unreadable, not an object, or
  missing `format_version`/`assessment`/`answer_key` — is `bad-exam-bundle` (ERROR), because
  every downstream tool reads it as truth.
  `checks/unit_structure.py:_check_exam_bundle`; the field names are
  `course_lint_config.py:EXAM_BUNDLE_KEYS`.
- **`Responses/` is the only required subdirectory.** A submission is `Responses/<id>.json` and
  the feedback that grades it is either inside the submission (`submission-format-spec-v0.3.md`
  §6) or `Responses/<id>.report.json` beside it — attached to the submission it grades, not filed
  in a directory of its own. `missing-exam-subdir` now fires once, for `Responses/`
  (`course_lint_config.py:REQUIRED_EXAM_SUBDIRS`).
- **`Keys/` and `Feedback/` stay legal but optional.** Unmigrated assessments keep them, and the
  location/kind rule of §2.1 still governs any `.md` inside them; nothing is deleted by a version
  bump. Removing them is a migration, and this version is only the shape change.
- §7 gains two rows — `missing-exam-bundle` (WARN) and `bad-exam-bundle` (ERROR), both from
  `checks/unit_structure.py:_check_exam_bundle` — and now holds **61 rows for 61 emitted codes**.

Everything v0.1.10 states still holds except §1.5's subdirectory rule, restated below.

## Change scope of v0.1.10

No rule changed, and **no code changed**. This version closes a defect in the
document itself:

- `exam-id-unknown` now has its §7 row (ERROR,
  `checks/state_json.py:check_exam_ids_resolve`). It was emitted by the linter
  from 2026-10-21, counted in every total in this document, listed in §9.7 — and
  absent from the matrix for eight versions while 0.1.3 claimed it had been
  restored.
- §9.7's claim that the row was restored in 0.1.3 is corrected rather than
  quietly dropped: the row was missing the whole time (§9.14).
- §7 now holds **59 rows for 59 emitted codes**, verified as a **set equality**
  in both directions — the check 0.1.9 lacked, which is why a one-row gap
  survived a version that audited the table row-by-row.

Everything v0.1.9 states still holds and is restated here in full.

## Change scope of v0.1.9

No rule changed. **Every citation in this document now names a symbol instead of
a line number** (§9.13):

- §7's 58 rows were **regenerated from the emitting sites** — the table now lists
  the function(s) that emit each code, and all 58 were verified to match the code
  exactly (the old table had drifted: `bad-fm-status` was cited at a line that,
  after 0.1.4 inserted `check_unit_field`, belongs to a different function, and
  `invalid-state-json` was two lines stale).
- 57 prose citations were re-resolved the same way; three bare `:NNN`
  continuations and two line *ranges* became real symbols.
- `path.py:1234` cannot be grepped after a refactor; `path.py:function` can, and
  it does not move. §0.2 now says so explicitly.
- Result-code count is unchanged at **59**; no test changes.

Everything v0.1.8 states still holds and is restated here in full.

## Change scope of v0.1.8

One named feature plus its consequences — the last item on the queue:

- **The exam family carries no `status`** (§2.2) — new result code
  `unexpected-exam-status` (ERROR, §7). The rule was already the design in
  `checks/templates.py:_check_status` ("the exam family owns no status"), but nothing
  enforced it and **all 845** exam-family files carried a hand-set value.
- **The 845 values were deleted** (§9.12): `active` 659, `canonical` 153,
  `available` 16, `graded` 9, `pending` 5, `completed` 3 — a vocabulary that
  matched neither the content kinds (`draft`/`active`/`completed`) nor
  `_state.json`'s assessment lifecycle (`available`/`deferred`/`completed`/
  `cancelled`/`delivered`), which is why it could not be a mirror of anything.
  The 259 content-kind files keep their status untouched.
- §7's count rises from 58 to **59**, and the change queue is **empty** for the
  first time: all eight v0.1 items are resolved.

Everything v0.1.7 states still holds and is restated here in full.

## Change scope of v0.1.7

**No rule added.** The queue's *`Archived/` contents* item is closed by decision,
not by code:

- Measured 2026-11-19: the vault has **one** archive subtree —
  `Philosophy/History of Ethics/Unit 01 — Presocratic Ethics/Archived/` — holding
  one entry, `Lecture 02 — Homeric Moral Vocabulary/`, whose directory name is
  already on-grammar. Its file (`Day 02 - Homeric Moral Vocabulary.md`) is a
  legacy name that the exemption deliberately permits.
- Decision: **nothing inside `Archived/` is name-checked.** The subtree exempts
  every course-file rule so superseded material can be kept verbatim; enforcing
  live naming there would force renames of exactly the content the archive
  exists to preserve. Only the directory *name* `Archived/` is constrained
  (§1.6, `course_lint_config.py:EXAM_LEVEL_BY_PARENT_PREFIXES`).
- Consequence: the result-code count stays at **58**; there is no new check to
  test. §10 drops to one item.

Everything v0.1.6 states still holds and is restated here in full.

## Change scope of v0.1.6

One named feature plus its consequences:

- **A lecture directory's own file must be named after the directory** (§1.3) —
  new result code `lecture-file-mismatch` (ERROR, §7). §1.3 has said this since
  v0.1; nothing enforced it, and 32 files violated it (`Lesson NN - Title.md`
  sitting inside `Lecture NN — Title/`).
- **The 32 violations are deliberately left in place** for now, on the owner's
  instruction: the rule ships, the repair is deferred (§9.11). The linter
  therefore reports **32 errors** on this vault until that repair happens — they
  are known, enumerated, and not to be treated as a broken build. §9.11 lists
  every affected directory, the link cost, and the exact rename recipe.
- The queue's *bare vs dotted lecture form per course* item is **measured and
  closed as moot**: 82 bare and 115 dotted lecture directories, and no course
  mixes them (§9.11).
- §7's count rises from 57 to **58**.

Everything v0.1.5 states still holds and is restated here in full.

## Change scope of v0.1.5

One named feature plus its consequences:

- **The kanban settings block is validated** (§5) — new result code
  `bad-kanban-settings` (ERROR, §7). Exactly one `%% kanban:settings` block, last
  in the file, raw JSON object (not fenced), `kanban-plugin: board`, and
  `list-collapse` sized to the column count. §5 previously said the block was
  **not** checked; that blind spot had already hidden a real column.
- §9.10 records the corruption it was measured against: in
  `Ethics/Korsgaard`'s sibling board `History of Ethics/Assignments.md` the block
  opener sat above `## Archive`, so the column and its `Day 001` card lived
  inside the comment and the JSON did not parse. Repaired before the rule
  shipped, so the new check fires 0 times on today's vault.
- §7's count rises from 56 to **57**, and change-queue item 1 (*kanban settings
  block*) is **implemented and withdrawn**; three items remain.

Everything v0.1.4 states still holds and is restated here in full.

## Change scope of v0.1.4

One named feature plus its consequences:

- **`unit` is the unit number as a bare integer, and must equal the enclosing
  `Unit NN — …` directory** (§2.2) — new result code `unit-mismatch` (ERROR, §7).
  The exam family wrote it as a quoted two-digit string (`unit: '03'`) while
  every lecture wrote `unit: 3`; nothing compared either form to the directory.
  The padded identity string is `unit_id`, not `unit`.
- The **196 exam-family strings were repaired** to ints (§9.9): 9 distinct
  values, each already equal to its ancestor unit, so the mapping was lossless
  (`'00'`→0 … `'08'`→8). 203 content files already conformed, including the 3
  exams that happened to use an int.
- §7's count rises from 55 to **56**, and change-queue item 1 (*`unit` field
  type*) is **implemented and withdrawn**; four items remain.

Everything v0.1.3 states still holds and is restated here in full.

## Change scope of v0.1.3

One named feature plus its consequences:

- **`lecture_id` is `<unit>.<lecture position>`, both zero-padded** (§1.3) — new
  result code `lecture-id-mismatch` (ERROR, §7). The unit half is read from the
  nearest `Unit NN — …` ancestor; the position follows the same three placements
  `lecture_number` uses. Carrying the unit is what makes an id unique inside a
  course.
- The **89 values that violated it were repaired** (§9.8) across 8 courses: 42
  bare-dotted ids gained the unit's zero pad, 32 bare integers became
  `<unit>.<position>`, and 15 Korsgaard slugs became numeric. Three state files'
  references were migrated with them; 108 values already conformed.
- The **`exam_id` queue item is withdrawn as already implemented** (§9.7). Its
  "fires 6 times" evidence was wrong — the check shipped before v0.1.2 was frozen,
  all five Classics records exist, and the Political Philosophy id in the queue was
  a file name, not a frontmatter value. So of the change queue's first two items,
  one was already done and the other (`lecture_id`) is done here; both are
  withdrawn and five items remain.
- §7's count is corrected from 53 to **55** distinct codes: `exam-id-unknown`
  (shipped in code without a spec bump) and `lecture-id-mismatch` were both missing
  from the table.

Everything v0.1.2 states still holds and is restated here in full.

## Change scope of v0.1.2

One named feature plus its consequences:

- **`lecture_number` must equal the position the file's location declares**
  (§1.3) — result code `lecture-number-mismatch` (ERROR, §7). The position is
  read from the enclosing lecture directory, or from a flat lecture file's own
  name, or for a lecture-part from the lecture directory one level up.
- The **6 values that violated it were repaired** (§9.6); all six were Korsgaard
  lectures carrying a copy of their `Lecture 01` file's `lecture_number: 1`.
- §7 was **regenerated from the code**, which corrected two counts v0.1 and v0.1.1
  stated (48, then 52 — the real number, with the new code, was 53) and restored
  emission sites the hand-written rows had dropped.
- §9's subsection order is repaired: v0.1.1 shipped §9.5 before §9.4.
- Change-queue item 1 (*`lecture_number` vs directory*) is **implemented and
  removed**; the remaining seven are renumbered.

Everything v0.1.1 states still holds and is restated here in full.

## Change scope of v0.1.1

One named feature plus its consequences:

- **A state path must sit in a directory that exists** (§3.4) — new result code
  `missing-assessment-dir` (ERROR, §7), deliberately status-independent.
- The **129 state path values that violated it were repaired** (§9.5), and §9.2's
  "0 unresolved" claim from v0.1 is corrected: it was scoped too narrowly.
- Change-queue item 3 (*assessment path exists*) is **implemented and removed**;
  the remaining eight are renumbered.

Everything v0.1 states still holds and is restated here in full.

## Change scope of v0.1


This document states, in one place, the structure that `Agents/Courses/` must have.
It is assembled from three sources, in this order of authority:

1. **The linter** (`Agents/Courses/scripts/`) — executable and authoritative.
   Every rule below cites the file and the function that implements it.
2. **This document** — the human-readable statement of those rules, plus the
   conventions the linter cannot yet check.
3. **The skills** (`course-framework`, `course-fw-*`, `exam-generator`) — advisory
   only. Where a skill contradicts the linter, the linter wins and the skill is
   a defect to fix.

What v0.1 changes relative to the previous de-facto state (four mutually
inconsistent skill references; see §9 for the migration that was executed):

- Eight new linter checks (§7, marked **new**).
- `status` is no longer a required frontmatter field on the exam family (§2.3).
- `status`, where present, is restricted to `draft | active | completed` for the
  four content kinds (§2.2).
- One convention for lecture directory names, with no capsule suffix (§1.4).
- `_state.json` is declared versioned content (§3.6), and its path values must be
  vault-relative (§3.5).
- The `Archived/` subtree is exempt from course-file rules (§1.7).

## 0. Authority, scope, and how to read citations

**0.1** A course is any directory `Agents/Courses/<Subject>/<Course>/` that
contains a `_state.json`. Three subdirectories of `Agents/Courses/` are **not**
subject directories and are skipped by every walker: `scripts/` and `tests/`
(the linter itself) and `skills/` (agent-facing pointer documents that route to
this spec) — `course_lint_config.py:NON_COURSE_DIRS`, used at `course_lint.py:find_courses` and
`checks/cross_course.py:check_duplicate_course_ids`, `:check_source_id_overlaps`, `:check_subject_directory_mismatch`.

**0.2** A rule is stated here with the citation of its implementation, e.g.
`course_lint_config.py:UNIT_DIR_RE`. The citation is part of the rule: if the code and
this document disagree, the code is right and this document is the bug.

**0.3** Severities are `ERROR` (fails the lint, exit 2) and `WARNING` (exit 1).
Exit codes: `0` clean, `1` warnings only, `2` errors, `3` catastrophic
(`course_lint_config.py:EXIT_CLEAN`).

**0.4** This document does not cover: the *content* of a lecture (pedagogy,
reading selections), citation style inside prose, or the assessment-format
contracts, which live in `Agents/Design/assessment-format-spec-*`.

**0.5** Where a rule needs comparison rather than character matching, this
document says so explicitly (§8). A checker that only tests file names cannot
claim conformance.

## 1. Directory grammar

### 1.1 Course root

```
Agents/Courses/<Subject>/<Course>/
```

The course root may contain **only** these entries
(`course_lint_config.py:ASSESSMENT_DIR_PREFIXES`, check `checks/course_structure.py:check_unexpected_course_root_entries`):

| Entry | Requirement |
|---|---|
| `_state.json` | required file (`course_lint_config.py:ALLOWED_COURSE_ROOT_ENTRIES`) |
| `HUB.md` | required file — the course syllabus hub |
| `Assignments.md` | required file |
| `Synthesis Drafts/` | optional directory |
| `references/` | optional directory (§1.8) |
| `Unit NN — <Title>/` | units (`course_lint_config.py:UNIT_DIR_RE`) |
| `<Course> Board.md` etc. | the kanban board (§5) |

Anything else is `unexpected-entry` (ERROR, `checks/course_structure.py:check_unexpected_course_root_entries`).
Dot-prefixed entries are ignored everywhere.

Note the name: the course hub is **`HUB.md`**, never `README.md`. The
`README.md → HUB.md` change (vault commit `4db84d3c`) is the convention this
spec pins.

### 1.2 Unit directory

`^Unit \d{2} — .+$` (`course_lint_config.py:UNIT_DIR_RE`). Two digits exactly; `Unit 001`
is invalid, `Unit 105` is a *stub* reference, not a directory (§6.2).

A unit directory may contain **only** the following
(check `checks/unit_structure.py:check_unit_entries`):

| Entry | Requirement |
|---|---|
| `HUB.md` | required — the unit hub |
| `Lecture NN[.L] — <Title>/` | a lecture directory (§1.4) |
| `Lecture NN[.L] — <Title>.md` | a lecture file, flat form (§1.4) |
| `Lecture Part ZZ — <Title>/` | a lecture-part directory (§1.5) |
| `Exam NN/` | a timed assessment (§1.6) |
| `Reading Worksheet NN[- Title]/`, `RN NN[- Title]/` | a reading worksheet (§1.6) |
| `Archived/` | the unit's archive (§1.7) |
| `references/` | the unit's support notes (§1.8) |

Anything else is `unexpected-unit-entry` (ERROR, `checks/unit_structure.py:check_unit_entries`).
This is what keeps loose scratch files out of units: a research note belongs in
`references/`, not in the unit directory.

### 1.3 Lecture directory and file

Two legal forms, one convention — the unit digit is always zero-padded to two
digits, the position part is optional, and there is **no capsule suffix**
(`course_lint_config.py:REFERENCE_FILE_RE`, `:LECTURE_DIR_FLEX_RE`, `:LECTURE_DIR_RE`):

```
Lecture NN — <Title>/         # NN is the lecture's position in the unit
Lecture NN — <Title>.md
Lecture NN.L — <Title>/       # NN = unit, L = position inside the unit
Lecture NN.L — <Title>.md
```

- `NN` is two digits (`Lecture 1.1` is invalid: it is neither form, and is
  reported as `unexpected-unit-entry`).
- `.L` exists because four units in this vault run to ten or more lectures and
  the dotted form is the only unambiguous one; the bare form stays legal for
  shorter units. Which form a unit uses is per-course, not per-unit type.
- **Prerequisite capsules are ordinary lectures.** They are numbered in reading
  order and carry no `P` or `.0` marker; their capsule role survives as prose in
  the hub's row label. See §9.3 for the migration that retired the old markers.
- A lecture directory's own file carries the same name as the directory, and the
  frontmatter `lecture_id` is `<unit>.<lecture position>`, both halves zero-padded:
  `Lecture 07.6 — …` inside `Unit 07 — …` is `"07.6"`, and `Lecture 03 — …` inside
  `Unit 02 — …` is `"02.3"`. The unit comes from the nearest `Unit NN — …`
  ancestor; the position follows `lecture_number`'s rule, so the two fields are
  derived from one place. Disagreement is `lecture-id-mismatch` (ERROR,
  `checks/frontmatter.py:check_frontmatter_fields`). `checks/frontmatter.py:check_unit_field` requires the field;
  §9.7 records the migration.
- **`lecture_number` is the lecture's position inside the unit, never the unit
  number**: `Lecture 08.7 — …` carries `lecture_number: 7`, `Lecture 02 — …`
  carries `2`. It is read from where the file actually sits — the enclosing
  lecture directory; the file's own name when the lecture is *flat*, as
  Pluralist Socialism keeps it at unit level; and for a `lecture-part`, the
  lecture directory one level up. Disagreement is `lecture-number-mismatch`
  (ERROR, `checks/frontmatter.py:check_frontmatter_fields`). Legacy flat `Lesson NN - …` files
  (Classics Unit 01) are read through the same rule. A file whose location
  declares no position (an unanchored name in a unit directory) is not judged by
  this rule.

- **The lecture directory's own file is named after the directory** —
  `Lecture 07 — Title/Lecture 07 — Title.md`, `.md` stem equal to the directory
  name. Three-tier lecture dirs (`HUB.md` plus `Lecture Part NN/` subdirs) and
  flat-at-unit courses (Pluralist Socialism keeps the file in the unit
  directory) hold no own file and are exempt; a directory that holds *any*
  Markdown file other than `HUB.md` is expected to hold one matching its own
  name. A legacy `Lesson NN - Title.md` inside `Lecture NN — Title/` is
  `lecture-file-mismatch` (ERROR, `checks/course_structure.py:check_lecture_file_names`). The number
  can agree while the identity drifts, so nothing derived from the directory
  notices — which is why the name rule has to exist. §9.11 records the 32 live
  violations and the deferred repair.

A directory that *looks* like a lecture dir but is not in a unit is
`misplaced-lecture-dir` (ERROR, `checks/course_structure.py:check_unexpected_course_root_entries`).

### 1.4 Lecture-part directory

`^Lecture Part \d{2} — .+$` (`course_lint_config.py:LECTURE_PART_DIR_RE`), inside a lecture
directory. A part file's `part_number` must equal the directory's number
(ERROR `part-number-mismatch`, `checks/frontmatter.py:check_frontmatter_fields`). `part_number` is a
bare integer: the padding lives in the directory name, not in the value.

### 1.5 Assessment directories

Named `Exam NN` (`^Exam \d{2}$`, `course_lint_config.py:EXAM_DIR_RE`) or
`^(?:Reading Worksheet|RN) \d{2}(?: - .+)?$` (`course_lint_config.py:READING_WORKSHEET_DIR_RE`).

**Assessment directories may sit at unit, lecture, or lecture-part level.** The
level is recorded in `Exam NN/HUB.md` as `exam_level: unit|lecture|part`
(`course_lint_config.py:VALID_FM_STATUS_BY_KIND`) and must match where the directory actually sits
(`checks/templates.py:_check_exam_file`; codes `bad-exam-level`, `exam-level-mismatch`).
The level implied by a parent directory is read from its name prefix, longest
prefix first (`course_lint_config.py:VALID_FM_STATUS_BY_KIND`).

Each assessment directory holds its hub, the bundle that is its key, and the submissions it
collects:

| Entry | Contents | Required |
|---|---|---|
| (own `HUB.md`) | `kind: exam` — the assessment's metadata and its level | yes |
| `<directory name>.json` | the assessment bundle: questions and answer key | absent = WARNING |
| `Responses/` | `<id>.json` per submission, `<id>.report.json` per graded submission | yes |
| `Keys/` | `exam-key` — the markdown key, where it is kept as the authoring source | no |
| `Feedback/` | `exam-feedback` — legacy; feedback belongs beside its submission | no |

`Responses/` is `course_lint_config.py:REQUIRED_EXAM_SUBDIRS`; a missing one is
`missing-exam-subdir` (ERROR, `checks/unit_structure.py:_validate_exam_dir`). The bundle is
checked by `_check_exam_bundle`: absent is `missing-exam-bundle` (WARNING), present but not a
bundle is `bad-exam-bundle` (ERROR). A missing hub is `missing-exam-readme` (WARNING).

`Keys/` and `Feedback/` are optional, so an assessment may hold either, both or neither; a `.md`
inside them still carries the kind its location implies (`EXAM_KIND_BY_SUBDIR`), and the bundle
is JSON, so no `kind:` rule applies to it.

### 1.6 Archive

The archive directory inside a unit is named exactly **`Archived/`**
(`course_lint_config.py:EXAM_LEVEL_BY_PARENT_PREFIXES`).

The archive subtree is **exempt from every course-file rule**: deprecated-kind
and template checks do not descend into it, so superseded lectures can be kept
verbatim. Only the directory *name* is constrained. (Verified: a `kind: lesson`
file placed inside `Archived/` produces no finding.)

This exemption is deliberate and **final**, not an unexamined gap. Measured
2026-11-19: one archive subtree exists, one entry, directory on-grammar, file
legacy-named — and the legacy name is the point. A rule requiring live naming
inside `Archived/` would rename the material the archive is preserving, so none
was added (v0.1.7).

### 1.7 `references/`

`references/` may exist at the course root and in every unit
(`course_lint_config.py:EXAM_LEVEL_BY_PARENT_PREFIXES`). It holds human-facing support notes. Every `.md`
file in it must be **Title Case with spaces**: the first word starts with an
upper-case letter or digit, later words may be lower-case function words, and a
lone `-` may separate words — `Reading Access.md`, `Research - Ch6 Reasoning.md`
(`course_lint_config.py:REFERENCES_DIR_NAME`). Non-`.md` entries are ignored.
A violation is `bad-reference-name` (ERROR, `checks/unit_structure.py:check_reference_names`).

Rationale: `references/` is the one place where notes accumulate by hand, so its
naming is the one place that drifts. Kebab-case names were the observed failure
mode.

## 2. Frontmatter contract

### 2.1 Kinds

Allowed: `syllabus`, `unit`, `lecture`, `lecture-part`, `exam`, `exam-key`,
`exam-response`, `exam-feedback` (`course_lint_config.py:LECTURE_NAME_RE`). Deprecated:
`lesson`, `unit-selection`, `reading-assignment`, all ERROR
(`course_lint_config.py:LECTURE_NAME_RE`, `checks/templates.py:check_kind_validity`).

The `kind` must also match the file's location: an `Exam NN/Keys/*.md` file is
`exam-key`, not `lecture` (ERROR `wrong-kind`, `checks/templates.py:_check_exam_file`).

### 2.2 Required fields by kind

`checks/frontmatter.py:check_frontmatter_fields`. Missing field = `frontmatter-missing-field`
(ERROR, `checks/frontmatter.py:check_unit_field` and four `checks/templates.py` sites).

| kind | required fields |
|---|---|
| `lecture` | `course`, `kind`, `lecture_id`, `lecture_number`, `unit`, `unit_title`, `concentrations`, `difficulty`, `status` |
| `lecture-part` | `course`, `kind`, `part_id`, `part_number`, `lecture_number`, `unit`, `unit_title`, `work_id`, `segment_id`, `status` |
| `unit` | `course`, `kind`, `unit_id`, `unit_title`, `concentrations`, `scale`, `status` |
| `syllabus` | `course`, `kind`, `course_title`, `status` |
| `exam` | `course`, `kind`, `exam_id`, `exam_level`, `unit` |
| `exam-key`, `exam-response`, `exam-feedback` | `course`, `kind`, `exam_id` |

**`unit`.** The unit *number*, as a bare integer, equal to the enclosing
`Unit NN — …` directory: `unit: 3` inside `Unit 03 — …`. It is a number like
`lecture_number`, not an identity string — the padded `"03"` form belongs to
`unit_id` on unit hubs. Disagreement, including the quoted-string form, is
`unit-mismatch` (ERROR, `checks/frontmatter.py:check_unit_field`, wired for the exam family at
`checks/templates.py:_check_exam_file`; §9.9 records the migration).

**`status`.** For the four content kinds it is required and must be one of
`draft`, `active`, `completed` (`course_lint_config.py:REQUIRED_FM_BY_KIND`); anything else
is `bad-fm-status` (ERROR, `checks/frontmatter.py:check_frontmatter_fields`, `checks/templates.py:_check_status`).
The exam family carries **no** `status`: assessment state belongs to
`_state.json` (§3.4). Writing one is `unexpected-exam-status` (ERROR,
`checks/templates.py:_check_exam_file`) — the 845 values that used to sit there used a
vocabulary matching neither the content kinds nor the state file, so they could
not have been a mirror of anything (§9.12 records the deletion).

**Number-valued fields are bare integers**; zero padding lives in file names.
`lecture_number: 10` accompanies `Lecture 08.10 — …`. Identity strings mirror the
name token instead: `unit_id: "01"` accompanies `Unit 01 — …` (ERROR
`unit-id-mismatch`, `checks/templates.py:check_unit_hub_template`).

### 2.3 Hub frontmatter

`HUB.md` at the course root is `kind: syllabus`; in a unit `kind: unit`; in a
lecture directory `kind: lecture` with only the lecture-family fields
(`checks/templates.py:check_lecture_hubs`). A hub is required at course and unit level
(`missing-file` ERROR, `missing-unit-hub` ERROR); a lecture directory's hub is
`missing-lecture-hub` (ERROR, `checks/templates.py:check_lecture_hubs`).

## 3. `_state.json`

### 3.1 Required top-level fields

Twenty fields (`checks/state_json.py:check_required_top_level_fields`); absence is `state-missing-field`
(ERROR, `checks/state_json.py:check_required_top_level_fields`):

```
schema_version, course_id, course_title, subject, created_at, updated_at,
status, curriculum, last_lesson, source_registry, source_requests, assessments,
study_hold, next_unit_selection, weak_areas, retrieval_queue, completed_units,
completed_works, synthesis_drafts, event_history
```

`status` ∈ `active | paused | completed` (`course_lint_config.py:REQUIRED_STATE_FIELDS`,
`bad-course-status`); `schema_version` must be `1` (`bad-schema-version`,
`checks/state_json.py:check_schema_version`). `curriculum` must carry its seven fields
(`checks/state_json.py:check_curriculum`, `curriculum-missing-field`).

### 3.2 `assessments[]`

Each entry carries the eighteen fields at `course_lint_config.py:REQUIRED_SOURCE_REGISTRY_FIELDS`
(`assessment-missing-field`); `status` ∈ `cancelled | available | completed |
deferred | delivered | graded | submitted` (`course_lint_config.py:REQUIRED_ASSESSMENT_FIELDS`,
`assessment-invalid-status` WARNING).

### 3.3 `source_registry[]`

Sixteen fields (`checks/state_json.py:check_source_registry`, `source-registry-missing-field`).

### 3.4 Assessment paths are vault-relative and must resolve

The four path fields — `student_exam_path`, `key_path`, `response_path`,
`feedback_path` (`checks/state_json.py:check_source_registry`) — are **vault-relative**, never
absolute. An absolute value is `absolute-state-path` (ERROR,
`checks/state_json.py:check_assessment_path_forms`). Absolute paths break on any other checkout or mount
point; the 88 absolute values found on 2026-10-15 were all rewritten (§9.2).

Each value must also sit in a directory that **exists**: its parent directory
is checked, and a miss is `missing-assessment-dir` (ERROR,
`checks/state_json.py:check_assessment_path_dirs`). The rule is deliberately **status-independent** —
the 129 values that violated it (§9.5) were all `status: available`, so a rule
that ignored `available` assessments would have reported none of them. A path
whose *file* is absent passes as long as its directory is there: that is an
authoring-front gap, not a defect.

### 3.5 `_state.json` is versioned

`_state.json` **is tracked in git** and committed alongside the artifacts it
points to (one commit per unit is the established cadence). It is the audit
trail of what was delivered, graded, and deferred; a generated-and-ignored
copy would lose that. Earlier guidance saying "never commit `_state.json`" is
withdrawn.

### 3.6 Timestamps

`created_at`/`updated_at` must parse as timestamps (`bad-timestamp`, WARNING,
`checks/state_json.py:check_timestamps`).

## 4. Hub templates

Required top-level sections per hub kind (`course_lint_config.py:EXAM_KIND_BY_SUBDIR`).
A missing section is `missing-template-section` (ERROR,
`checks/templates.py:_check_sections`); a section outside required+optional is
`unexpected-section` (ERROR, `checks/templates.py:_check_sections`).

| Hub kind | heading level | required sections |
|---|---|---|
| course (`syllabus`) | `#` | Units, I. Program Purpose, II. Governing Curricular Guardrails, III. Lecture Architecture, IV. Bibliography and Citation Standards, V. Sources |
| unit (`unit`) | `#` | Unit Rationale, Prerequisites, Lectures, Primary Editions, Unit Completion Standard (+ optional Recurring Secondary Works, Unit Synthesis) |
| lecture (`lecture`) | `#` | Overview, Learning Objectives, Lecture Parts (+ optional Optional Lecture Material, Exam, Next) |
| lecture body (`lecture`) | `##` | Central Questions, Learning Objectives, Prerequisites, Required Primary Reading, Required Secondary Reading, Key Concepts, Argument Reconstruction, Teaching Notes, Seminar Questions, Exercise, Connections (+ optional Strongly Recommended, Research / Extension, Close-Reading Targets, Interpretive Disputes, Edition / Translation Notes, Reading Order) |
| lecture-part body | `##` | the lecture list without Connections, plus optional Next / Reading Order |

Unfilled template markers are `placeholder-content` (WARNING,
`checks/templates.py:check_unit_hub_template`).

## 5. Kanban board

The board is a Markdown file with `kanban-plugin: board` in its frontmatter
(`missing-kanban-frontmatter` ERROR, `checks/kanban.py:check_kanban_frontmatter`) and the columns
`In Progress`, `Current Unit`, `Future Units`, `Completed`
(`checks/kanban.py:check_kanban_columns`; a missing column is `missing-kanban-column`
ERROR, `checks/kanban.py:check_kanban_columns`). Column matching is a **substring** test, so
`## ✅ Completed` and `## 📋 Completed` both satisfy the `Completed` column.

Cards in `In Progress` need a due date (`missing-due-date` WARNING,
`checks/kanban.py:check_in_progress_due_dates`); completed cards need a completion date
(`missing-completion-date` WARNING, `checks/kanban.py:check_completed_dates`).

**The settings block is validated** (`bad-kanban-settings` ERROR,
`checks/kanban.py:check_kanban_settings`). Exactly one `%% kanban:settings` block must exist, it
must be the last content in the file, its body must be a raw JSON object — a
fenced code block is the plugin's classic `Unexpected token 'j'` failure — its
`kanban-plugin` must be `board`, and its `list-collapse` array, when present,
must have one entry per `##` column. Extra plugin keys
(`show-checkboxes`, `hide-tags-display`, …) are allowed and unvalidated: the
courses use only `kanban-plugin` and `list-collapse`, but the rule must not
police options it does not own.

Three failure modes are invisible in the source file, which is why this is an
ERROR and not a WARNING: a fence breaks parsing outright; an opener placed above
a column swallows that column and its cards into the comment; a short
`list-collapse` array silently mis-collapses. §9.10 records the live instance
that motivated the rule.

## 6. Cross-course rules

Run with `--cross-course`; codes are emitted against
`Agents/Courses/ (cross-course)`:

- `duplicate-course-id` (ERROR, `checks/cross_course.py:check_duplicate_course_ids`).
- `shared-source` (WARNING, `checks/cross_course.py:check_source_id_overlaps`): one `source_id` used by
  two courses.
- `subject-mismatch` (ERROR, `checks/cross_course.py:check_subject_directory_mismatch`): a course's `subject`
  disagrees with its subject directory.

Stub units: a `[[Unit NNN — …]]` wikilink in the course hub with no directory is
a stub and must be registered in `_state.json` → `stub_units`, else
`stub-unit-not-registered` (WARNING, `checks/course_structure.py:check_stub_units`). Unit
numbers of two **or three** digits are accepted (`\d{2,3}`), because a
100+-unit curriculum registers `Unit 105`.

## 7. Check matrix

Every result code the linter can emit, with severity and implementation. The
table is generated from the emitting sites, not maintained by hand: the `Where`
column names the **function** that emits each code, never a line number, so it
survives edits above it. Where a code is emitted from more than one place, every
site is listed.

Codes marked **new** were added after v0.1: `missing-assessment-dir` in 0.1.1,
`lecture-number-mismatch` in 0.1.2, `exam-id-unknown` (added to the code on
2026-10-21 without a spec bump) and `lecture-id-mismatch` in 0.1.3,
`unit-mismatch` in 0.1.4, `bad-kanban-settings` in 0.1.5,
`lecture-file-mismatch` in 0.1.6, `unexpected-exam-status` in 0.1.8, and
`missing-exam-bundle` and `bad-exam-bundle` in 0.1.11.

| Code | Sev | Where |
|---|---|---|
| `absolute-state-path` **(new)** | ERROR | `checks/state_json.py:check_assessment_path_forms` |
| `assessment-invalid-status` | WARN | `checks/state_json.py:check_assessments` |
| `assessment-missing-field` | ERROR | `checks/state_json.py:check_assessments` |
| `bad-assessments` | ERROR | `checks/state_json.py:check_assessments` |
| `bad-course-status` | ERROR | `checks/state_json.py:check_course_status` |
| `bad-curriculum` | ERROR | `checks/state_json.py:check_curriculum` |
| `bad-exam-bundle` **(new)** | ERROR | `checks/unit_structure.py:_check_exam_bundle` |
| `bad-exam-dir-name` | ERROR | `checks/unit_structure.py:_validate_exam_dir` |
| `bad-exam-level` **(new)** | ERROR | `checks/templates.py:_check_exam_file` |
| `bad-fm-status` **(new)** | ERROR | `checks/frontmatter.py:check_frontmatter_fields`, `checks/templates.py:_check_status` |
| `bad-kanban-settings` **(new)** | ERROR | `checks/kanban.py:check_kanban_settings` |
| `bad-reference-name` **(new)** | ERROR | `checks/unit_structure.py:check_reference_names` |
| `bad-schema-version` | ERROR | `checks/state_json.py:check_schema_version` |
| `bad-source-registry` | ERROR | `checks/state_json.py:check_source_registry` |
| `bad-timestamp` | WARN | `checks/state_json.py:check_timestamps` |
| `bad-unit-dir-name` | ERROR | `checks/course_structure.py:check_unit_dir_naming`, `checks/unit_structure.py:check_unit_dir_naming_unit` |
| `current-lecture-missing` | ERROR | `checks/templates.py:check_state_position` |
| `current-unit-missing` | ERROR | `checks/templates.py:check_state_position` |
| `curriculum-missing-field` | ERROR | `checks/state_json.py:check_curriculum` |
| `deprecated-kind` | ERROR | `checks/templates.py:check_kind_validity` |
| `duplicate-course-id` | ERROR | `checks/cross_course.py:check_duplicate_course_ids` |
| `exam-id-unknown` | ERROR | `checks/state_json.py:check_exam_ids_resolve` |
| `exam-level-mismatch` **(new)** | ERROR | `checks/templates.py:_check_exam_file` |
| `frontmatter-missing-course` | WARN | `checks/frontmatter.py:check_frontmatter_fields` |
| `frontmatter-missing-field` | ERROR | `checks/frontmatter.py:check_frontmatter_fields`, `checks/templates.py:check_lecture_hubs`, `checks/templates.py:check_unit_hub_template`, `checks/templates.py:check_course_hub_template`, `checks/templates.py:_check_exam_file` |
| `invalid-state-json` | ERROR | `checks/state_json.py:check_state_exists_and_parse` |
| `lecture-grouping-overused` | WARN | `checks/unit_structure.py:check_lecture_grouping` |
| `lecture-grouping-underused` | WARN | `checks/unit_structure.py:check_lecture_grouping` |
| `lecture-file-mismatch` **(new)** | ERROR | `checks/course_structure.py:check_lecture_file_names` |
| `lecture-id-mismatch` **(new)** | ERROR | `checks/frontmatter.py:check_frontmatter_fields` |
| `lecture-number-mismatch` **(new)** | ERROR | `checks/frontmatter.py:check_frontmatter_fields` |
| `lesson-id-unknown` | WARN | `checks/frontmatter.py:check_lesson_id_references` |
| `misplaced-lecture-dir` | ERROR | `checks/course_structure.py:check_unexpected_course_root_entries` |
| `missing-assessment-dir` **(new)** | ERROR | `checks/state_json.py:check_assessment_path_dirs` |
| `missing-completion-date` | WARN | `checks/kanban.py:check_completed_dates` |
| `missing-due-date` | WARN | `checks/kanban.py:check_in_progress_due_dates` |
| `missing-exam-bundle` **(new)** | WARN | `checks/unit_structure.py:_check_exam_bundle` |
| `missing-exam-readme` | WARN | `checks/unit_structure.py:_validate_exam_dir` |
| `missing-exam-subdir` | ERROR | `checks/unit_structure.py:_validate_exam_dir` |
| `missing-file` | ERROR | `checks/course_structure.py:check_required_files`, `checks/kanban.py:check_kanban_exists`, `checks/state_json.py:check_state_exists_and_parse` |
| `missing-frontmatter` | ERROR | `checks/frontmatter.py:check_frontmatter_fields`, `checks/templates.py:check_lecture_hubs`, `checks/templates.py:check_unit_hub_template`, `checks/templates.py:check_course_hub_template`, `checks/templates.py:_check_exam_file` |
| `missing-kanban-column` | ERROR | `checks/kanban.py:check_kanban_columns` |
| `missing-kanban-frontmatter` | ERROR | `checks/kanban.py:check_kanban_frontmatter` |
| `missing-lecture-hub` | ERROR | `checks/templates.py:check_lecture_hubs` |
| `missing-template-section` | ERROR | `checks/templates.py:_check_sections` |
| `missing-unit-hub` | ERROR | `checks/unit_structure.py:check_unit_hub_exists` |
| `part-number-mismatch` **(new)** | ERROR | `checks/frontmatter.py:check_frontmatter_fields` |
| `placeholder-content` | WARN | `checks/templates.py:check_unit_hub_template` |
| `shared-source` | WARN | `checks/cross_course.py:check_source_id_overlaps` |
| `source-registry-missing-field` | ERROR | `checks/state_json.py:check_source_registry` |
| `state-missing-field` | ERROR | `checks/state_json.py:check_required_top_level_fields` |
| `stub-unit-not-registered` | WARN | `checks/course_structure.py:check_stub_units` |
| `subject-mismatch` | ERROR | `checks/cross_course.py:check_subject_directory_mismatch` |
| `unescaped-alias-pipe-in-table` | ERROR | `checks/table_links.py:_check_file` |
| `unexpected-entry` | ERROR | `checks/course_structure.py:check_unexpected_course_root_entries` |
| `unexpected-section` | ERROR | `checks/templates.py:_check_sections` |
| `unexpected-exam-status` **(new)** | ERROR | `checks/templates.py:_check_exam_file` |
| `unexpected-unit-entry` **(new)** | ERROR | `checks/unit_structure.py:check_unit_entries` |
| `unit-id-mismatch` **(new)** | ERROR | `checks/templates.py:check_unit_hub_template` |
| `unit-mismatch` **(new)** | ERROR | `checks/frontmatter.py:check_unit_field` |
| `wrong-kind` | ERROR | `checks/templates.py:_check_exam_file` |

**59 distinct codes**, counted by enumerating the emitting sites in every shape
they are written (`ctx.add_result` and the `results.append(LintResult(...))` form
used by `checks/cross_course.py`).

**Correction (0.1.2).** v0.1 shipped 48 and v0.1.1 52. Both were wrong: 0.1.2
regenerates the table from the code and finds sites the hand-written rows had
dropped — five `frontmatter-missing-field` sites where three were listed, four
`missing-frontmatter` where three were, and two more. The count and the rows now
come from the same scan, so they cannot disagree.

**Correction (0.1.3).** 0.1.2's 53 was accurate for the code as frozen on
2026-10-15. `exam-id-unknown` was added to the code on 2026-10-21 without a spec
bump — its row was missing from the table — and `lecture-id-mismatch` is added
here. Both rows are present now: 55 codes.

## 8. What a conforming checker must do

Rules split in two, and the split is load-bearing:

**Name/presence rules** — decided from a path or a frontmatter key: directory
grammars, allow-lists, required files and fields, required sections, the shape of
a `references/` file name.

**Value rules** — need the value read *and compared*: `exam_level` against the
directory's placement; `part_number` against `Lecture Part ZZ/`; `lecture_number`
against the position the file's location declares; `unit_id` against
`Unit NN —`; a path being relative rather than absolute; a path's parent
directory against the filesystem; `status` against its allowed set. A checker that only tests names and key presence cannot
conform: it passes every value rule vacuously. The linter implements value rules
by reading frontmatter and `_state.json` and comparing in Python
(`checks/frontmatter.py:check_frontmatter_fields`, `checks/templates.py:check_exam_file_kinds`,
`checks/state_json.py:check_assessment_path_forms`, `:check_assessment_path_dirs`).

## 9. Migration record (2026-10-15)

Executed in this order, one pass each, with `git mv` throughout so history
follows the files.

### 9.1 Lecture naming

- **Pluralist Socialism**, 8 pairs: `Lecture N.L — …` → `Lecture 0N.L — …`
  (directory + file + frontmatter + hub rows + cross-references).
- **Iris Murdoch**, 36 pairs: prerequisite capsules folded into the reading
  order and the whole sequence renumbered. Order was taken from each capsule's
  **own body** ("read it before Lecture NN.L"), not from the hub pointer, which
  was wrong for two U04 capsules; those pointers were corrected by hand.
  Readings after the fold, e.g. U04: `04.1` capsule, `04.2` Plato, `04.3`
  capsule, `04.4` Weil, `04.5`–`04.7`.
- Substitution was limited to `Lecture <id>` occurrences and `# Lectures` table
  cells. A blanket replacement of bare ids was rejected: worksheet bodies use the
  same digit shapes for question numbers (`1.1`, `2.3`) and would have been
  corrupted.

### 9.2 State paths

88 absolute values across the courses' `_state.json` files were rewritten
vault-relative; 22 of them also pointed at `…/Feedback/README.md`, which the
`HUB.md` convention had renamed — those were repointed to `Feedback/HUB.md`.

**Correction (0.1.1).** v0.1 claimed "after the rewrite, 0 path values were
unresolved". That is **withdrawn** as too narrow: the check re-tested only the
values it had just rewritten, not whether paths still resolved after §9.1
renamed lecture directories. A later audit over every path value found **129
whose parent directory does not exist** — 105 in Classics written `…/Exam 1/…`
while the delivered assessment sat in `…/Exam 01/…`, and 24 in Pluralist
Socialism still naming the pre-§9.1 lecture directory (a regression from that
very pass). Repaired in §9.5; the rule that would have caught both is §3.4.

### 9.3 Housekeeping

- History of Ethics: `Archived — Superseded Lectures/` → `Archived/`; the three
  kebab-case `references/` files renamed to Title Case (and one prose reference
  updated).
- Loose research notes moved into unit `references/` directories: Think U06
  `Research - Ch6 Reasoning.md`, Korsgaard U01 `Research - Prologue and Lecture
  1.md`.

### 9.4 Verification


- `python3 Agents/Courses/scripts/course_lint.py --vault . --cross-course` →
  **10 courses, 0 errors, 0 warnings**.
- `python3 -m unittest discover -s Agents/Courses/tests` → **264 tests, OK**.
  v0.1 recorded 235 before its final pass; the suite then stood at 242 (36 tests
  for the rules in §1.4–§1.7, §2.2, §3.4 and 6 for course discovery (§0.1), plus
  18 stale fixtures from the `README.md → HUB.md` rename fixed). v0.1.1 added 9
  for `missing-assessment-dir`; v0.1.2 adds 13 for `lecture-number-mismatch`
  (both lecture forms, flat lecture files, the legacy `Lesson NN` name,
  lecture-parts reading their enclosing lecture, and the pass-through cases).
- Archive exemption verified by planting a `kind: lesson` file and a stray
  `references/`-style name inside `Archived/`: 0 findings.
- `missing-assessment-dir` exercised against the **real vault**, not only in unit
  tests: one repaired value was reverted by hand, the linter reported it
  (`assessments[12].student_exam_path`), and the file was restored
  byte-identically afterwards (digest compared before/after).
- `lecture-number-mismatch` was exercised the same way: before repairing the six
  values the linter reported exactly those six (no others, across 197 lecture and
  3 lecture-part files), and afterwards a single value was reverted by hand and
  the finding reappeared; the file was restored byte-identically.

### 9.5 Assessment path repair (0.1.1)

129 values in 2 files, format-preserving: only the four path-field string values
changed, so key order, indent width and every other byte on disk is untouched
(129 insertions / 129 deletions in `git diff --stat`).

- `Literature/Classics/_state.json` — 105 values, `…/Exam N/…` → `…/Exam 0N/…`.
- `Philosophy/Pluralist Socialism/_state.json` — 24 values,
  `…/Lecture N.L …/` → `…/Lecture 0N.L …/`.

Every one of the 129 landed on a directory that already existed, so the new check
reports **0 findings** on the repaired vault. Measured after repair: 540 path
values, of which 388 have the file present, 152 have the directory present with
the file not yet authored, and 0 have a missing directory. The repair is
idempotent (a second run reports `0 values in 0 files`).

### 9.6 Lecture-number repair (0.1.2)

Six lecture files in Korsgaard, each carrying `lecture_number: 1` — the value
copied from its unit's `Lecture 01` file and never incremented:

| Unit | File | was | now |
|---|---|---|---|
| U02 | `Lecture 02 — Bernard Williams: Convergence and Flourishing` | 1 | 2 |
| U02 | `Lecture 03 — Mill and the Reflective Agent` | 1 | 3 |
| U03 | `Lecture 02 — The Solution: Practical Identity and Autonomy` | 1 | 2 |
| U03 | `Lecture 03 — Moral Obligation and the Kingdom of Ends` | 1 | 3 |
| U04 | `Lecture 02 — Pain, Animals, and the Origin of Value` | 1 | 2 |
| U04 | `Lecture 03 — Scepticism, Suicide, and the Conclusion` | 1 | 3 |

Each edit touches one frontmatter line only. The other 191 lecture files and all 3
lecture-part files already agreed with their location, which is why the rule could
be implemented without inventing a convention: the definition in §1.3 is what the
rest of the vault already does.

### 9.7 Exam-id repair (0.1.3)

v0.1.2's change queue listed `exam_id` resolution as an unimplemented gap that
"fires 6 times". **That evidence was wrong, and the item was already implemented.**

What the queue claimed: 5 Classics Unit 03 worksheet hubs (`reading-ws-03-1`…`-5`)
and 1 Political Philosophy Unit 00 hub (`political-philosophy-u0l1`) carried an
`exam_id` that appeared in no `assessments[].assessment_id`.

What was actually in the vault when measured for 0.1.3:

- `check_exam_ids_resolve` — the check the queue item asked for — is registered in
  `course_lint.py:lint_course`, runs on every course, exempts `Archived/`, and reports once
  per distinct id per course. It was added in commit `2fb53037` on 2026-10-21, i.e.
  **before v0.1.2 was frozen**, without a spec bump.
- All five Classics Unit 03 worksheet records are present in
  `Literature/Classics/_state.json` (82 assessments in total), each with a
  `lesson_id` and `covers_segment_ids` matching its lecture, and each hub's
  `exam_id` (`reading-ws-03-1`…`-5`) resolves against them.
- The Political Philosophy Unit 00 hub carries `exam_id: pp-l0.1-exam-01`, which
  matches its state record. The `political-philosophy-u0l1` string the queue cited
  is the hub **file name**, not its frontmatter value — the two were conflated.

Measured at 0.1.3: **749 `exam_id` carriers across 9 courses, 0 unresolved**, and a
full `--cross-course` run reports **0 findings**. The check is not passing
vacuously: breaking one hub's `exam_id` to an unregistered value made it fire
immediately, and restoring the file returned byte-identical output.

No frontmatter value needed changing. The repair in this version is to the
**record**, not to the vault: the queue item is withdrawn.

**Correction (0.1.10).** 0.1.3 claimed the `exam-id-unknown` row, "missing from
v0.1.2's §7 table", was "restored there". It was not. The table kept 58 rows
while every count in this document said 59, and the row only appeared in the
matrix in 0.1.10 — eight versions later. The count was right and the table was
short; nothing compared them, because the 0.1.9 verification checked that each
**existing** row matched its emitting sites and never checked the reverse
direction (§9.14).

### 9.8 Lecture-id migration (0.1.3)

`lecture_id` was three conventions at once: 108 padded dotted values
(`07.6`), 42 unpadded dotted (`1.1`), 32 bare integers (`2`), and 15 Korsgaard
slugs (`lecture-01-hume-reflective-endorsement`). The new definition in §1.3 —
`<unit>.<lecture position>`, both zero-padded — changed 89 of the 197 values:

| Course | Values changed | Shape |
|---|---|---|
| Philosophy/Political Philosophy | 28 | `2` → `00.2` (bare position → unit added) |
| Ethics/Korsgaard | 17 | 15 slugs → `02.1`; 2 unpadded → `01.1` |
| Ethics/Animal Ethics | 16 | `1.2` → `01.2` |
| Philosophy/Think | 12 | `6.1` → `06.1` |
| Philosophy/Public Philosophy Writing | 7 | `1.1` → `01.1` |
| Philosophy/History of Ethics | 4 | `2` → `02.2` (unit added) |
| History/Modern Israel and Palestine | 4 | `1.2` → `01.2` |
| Literature/Classics | 1 | `1.2` → `01.2` |

The unit half is read from the nearest `Unit NN — …` ancestor and the position
from the same three placements `lecture_number` uses, so both fields are derived
from one place. Only the `lecture_id:` line changes in each file; no file name,
directory name or body text moves.

Three `_state.json` files referenced the old values and were migrated in the same
pass, so no join broke: Korsgaard's 22 `lesson_id` references, Public Philosophy
Writing's 7 `event_history[].lecture_id` references, and Political Philosophy's
`stub_units` entry. Korsgaard's `lesson_id`s are now numeric — the join survives,
but the slugs are no longer human-readable in `_state.json`.

Why each family had to change. The 42 unpadded dotted values carried the unit but
not its zero pad (`1.2` for Unit 01's Lecture 02); the pad is what makes the string
sort and compare predictably. The 32 bare integers carried the position but not the
unit — and that is exactly why Political Philosophy collided: its ids `1`–`5` each
appeared once in Unit 00 and once in Unit 01. The 15 Korsgaard slugs carried
neither. So all four families failed the same contract in different ways, and 108
padded values already satisfied it.

Measured after repair: **197 values, 0 duplicates**, and the new check reports **0
findings** on all 9 courses. The repair is idempotent; a second run changes
nothing.

### 9.9 Unit-type repair (0.1.4)

`unit` was written two ways with no rule either way: every `lecture` (197) and
`lecture-part` (3) file used a bare integer, while 196 of the 199 `exam`-family
files used a quoted two-digit string. Three exams in History of Ethics already
used an int. Nothing in the linter read the field beyond requiring its presence,
so the split never failed — it would only bite a tool comparing `"03"` to `3`.

The 196 strings were rewritten to the integer they already spelled, one
`unit:` line each:

| string | int | files |
|---|---|---|
| `'00'` | 0 | 1 |
| `'01'` | 1 | 64 |
| `'02'` | 2 | 19 |
| `'03'` | 3 | 18 |
| `'04'` | 4 | 13 |
| `'05'` | 5 | 10 |
| `'06'` | 6 | 15 |
| `'07'` | 7 | 20 |
| `'08'` | 8 | 36 |

Nine distinct values, and **all 196 already equalled their ancestor unit**, so the
mapping was lossless and no value judgement was needed: `'03'` became `3`, never
`03`. Measured after repair: **399 `unit` fields, 0 strings, 0 mismatches**. No
`_state.json` carries a `unit` key (only `unit_id`), so no join was touched.

The canonical int is the unit *number*, matching how `lecture_number` is written;
the padded string identity lives in `unit_id`. The new check derives the expected
value from the nearest `Unit NN — …` ancestor, so it also catches a file filed
under the wrong unit — which is what makes it worth more than the type fix alone.

### 9.10 The kanban settings block was silently swallowing a column (0.1.5)

The queue said the settings block was unvalidated. Measuring it found the gap
had already cost a column — not a hypothetical.

`Ethics/History of Ethics/Assignments.md` read, in order: frontmatter, four
columns, `%% kanban:settings`, **`## Archive`**, the archived `Day 001` card, the
JSON, `%%`. The opener sat above the `Archive` heading, so the heading and its
card were inside the comment, and the block's body was
`## Archive\n\n- [x] Day 001 … \n\n{"kanban-plugin":…}` — which is not JSON. The
plugin could not parse the settings at all, and the fourth/fifth column
relationship was wrong: 5 `##` headings against 4 `list-collapse` entries.

Nothing else could have caught it. `missing-kanban-column` only looks for the
required four by substring, and `Archive` is optional; the frontmatter check sees
`kanban-plugin: board` and is satisfied; the cards inside the block are neither
in `In Progress` nor `Completed`, so the date warnings skip them. Word processors
and Obsidian's reading view hide `%%` comments, so the breakage is invisible in
every surface except the raw file.

Repaired before the rule shipped (block moved after the last column,
`list-collapse` raised to five entries; no card, date, or `{gcal:…}` marker
changed). Measured after: 10 course boards, 10 settings blocks, all valid, 0
findings.

Vault-wide the same scan found 15 boards, of which the two Personal boards
`Kanban/Workflow.md` and `Essay AI Kanban.md` carry a *second* settings block at
EOF wrapped in a fenced code block — the plugin's classic `Unexpected token 'j'`
failure. They are outside `Agents/Courses/**`, so the linter does not see them;
they are noted here rather than silently fixed, because Personal/ is not this
spec's to edit.

### 9.11 Lecture file names: rule now, repair deferred (0.1.6)

The queue item was *bare vs dotted lecture form per course*. Measured: **197
lecture directories — 82 bare (`Lecture NN — …`), 115 dotted (`Lecture NN.L — …`)
— and no course mixes the two forms.** A per-course guard would fire zero times
and could not be tested against a real violation, so the item is closed as moot
rather than implemented as unverifiable code.

The same scan found something that *was* real. §1.3 has said since v0.1 that a
lecture directory's own file carries the directory's name; nothing checked it,
and **32 files violate it**, all in one shape — a legacy `Lesson NN - Title.md`
inside `Lecture NN — Title/`:

| course | violations |
|---|---|
| Ethics/Animal Ethics | 16 |
| Philosophy/Think | 12 |
| History/Modern Israel and Palestine | 4 |

Every derived field agrees with the directory (`lecture_number`, `lecture_id`),
so no existing rule notices: the number matches, only the identity drifts. Eight
of the 33 legacy stems (the 32 above plus Classics Unit 01, which is exempt as an
archive-adjacent legacy) carry inbound wikilinks — 24 link instances, mostly
Modern Israel hubs — so a rename is not a pure `git mv`.

**Owner decision (2026-11-19): enforce the rule, do not repair yet.** The check
ships and the vault reports 32 ERRORS until the rename pass happens. They are
known, enumerated, and must not be read as a broken build; a "0 findings" gate on
this vault stays red in exactly this one code until then.

The deferred recipe, for the pass that does it:

1. For each of the 32 directories, `git mv "Lesson NN - Title.md" "Lecture NN — Title.md"`
   (the target name is the directory's own name plus `.md`).
2. Rewrite every `[[Lesson NN - Title…]]` wikilink to the new stem — 24 instances
   across the Modern Israel and Think hubs; run the vault-wide link check after.
3. Re-run `course_lint.py --vault . --cross-course`; `lecture-file-mismatch` must
   reach 0 before the entry is deleted from this section.

**Outcome (2026-11-19, after this rule shipped):** a course-maintenance pass
renamed the 32 files (`2ff26381`, `6a30f66f`, `a61c6630`), so
`lecture-file-mismatch` now reports **0**. One legacy file remains —
`Literature/Classics/Unit 01 — The Dispossessed/Lesson 01 - Read The
Dispossessed.md` — and it is not inside a `Lecture NN — …/` directory, so the
rule does not reach it: a flat lecture file at unit level, which §1.3 permits
for courses that keep lectures out of per-lecture directories.

### 9.12 Deletion of the exam-family `status` (0.1.8)

The queue said the exam family's `status` was ungoverned. Measured 2026-11-19:
it was universal — **845 of 845** exam-family files (`exam`, `exam-key`,
`exam-response`, `exam-feedback`) carried one, every value hand-set:

| value | files |
|---|---|
| `active` | 659 |
| `canonical` | 153 |
| `available` | 16 |
| `graded` | 9 |
| `pending` | 5 |
| `completed` | 3 |

Compare the two governed vocabularies it sat between: content kinds use
`draft`/`active`/`completed` (`course_lint_config.py:REQUIRED_FM_BY_KIND`), and
`_state.json`'s 233 assessment records use `available` 174, `deferred` 45,
`completed` 11, `cancelled` 2, `delivered` 1. The frontmatter set overlaps
neither, and `canonical` — the second-largest value — appeared on arbitrary
HUBs, keys and student responses with no consistent role. It recorded nothing
comparable to anything.

The code had said so since v0.1 (`checks/templates.py:_check_status`: "the exam family owns
no status") and `_check_status` returned early for those kinds, so the field was
decoration. Only two values carried information the vault does not keep
elsewhere: `graded` (9 Modern Israel feedback files, graded date also in the
filename) and `pending` (5 Classics Sisyphus feedback HUBs awaiting feedback).

**Decision: delete, then forbid** (owner, 2026-11-19). The `status:` line was
removed from all 845 exam-family frontmatter blocks — format-preserving,
idempotent, content kinds untouched. Measured after: 845 exam-family files, **0**
with `status`, 0 unparseable, 0 missing `exam_id`; the 259 content-kind files
still carry theirs. `unexpected-exam-status` (ERROR) then makes the field
un-writable.

The count grew from 749 to 845 between v0.1 and this pass because reading
worksheets added by course maintenance carry both `exam_id` and `status`. That is
why the old "749" equalled the `exam_id` carrier count: it was always the same
population, and the figure was a moving target rather than a fixed defect count.

### 9.13 Citations switched from line numbers to symbols (0.1.9)

Six citations had already been corrected by hand during 0.1.4–0.1.6 as code
inserted above them shifted every later line. Checking the rest found the drift
was general, not occasional:

- `bad-fm-status` was cited at `checks/frontmatter.py` line 173. After 0.1.4
  added `check_unit_field`, that line belongs to **that** function — a
  plausible-looking citation naming the wrong code.
- `invalid-state-json` was cited at `checks/state_json.py` line 37; the emission
  sits at 39.
- Three "bare continuation" citations resolved against the *first* file named on
  their line rather than the file actually being continued, and two citations
  were line **ranges**, which name no single symbol at all.
- A line-based scan finds only a quarter of the emissions: `add_result(` almost
  always puts the code string on the *following* line, so the §7 table had to be
  rebuilt by character offset, then mapped to the enclosing module-level `def`.

Verification: all 58 §7 rows now equal their emitting-site set exactly, and no
line number remains anywhere in the document. The trade accepted: a citation says
*which* function, not where inside it — coarser for rules implemented as a single
expression in a long function, but never wrong, and still greppable.

### 9.14 The missing `exam-id-unknown` row (0.1.10)

`exam-id-unknown` was added to the code on 2026-10-21 (`2fb53037`) without a spec
bump. 0.1.3 investigated that code, found it correctly implemented, verified it
was non-vacuous by breaking a `reading-ws-03-1` id, and wrote that the missing §7
row was "restored there". The row was never added.

How it survived eight versions:

- Every count in the document said 59, and the preamble lists the code by name,
  so the number looked verified. The table itself had 58 rows. The two numbers
  lived in different sections and nothing compared them.
- 0.1.9 regenerated §7 from the emitting sites — but from the sites **of the rows
  already in the table**, so it confirmed 58 correct rows and had no way to notice
  a 59th was absent. A generator that iterates rows cannot discover a missing row.
- Both directions are needed, and only one was ever checked.

The fix here is the row plus the corrective note in §9.7. The durable guard is
`Agents/Courses/tests/test_spec_check_matrix.py`: it locates the newest spec by
numeric version, extracts §7's rows, and asserts **set equality both ways**
against the codes the checks actually emit — plus, per row, that the named
functions are the ones that emit that code. Four tests; the suite is 314.

That test immediately caught a second, older assumption of mine: every superseded
spec still says `**Status:** current` in its own frontmatter, because a frozen
predecessor is byte-identical and cannot be edited. "Which version is current" is
therefore a property of `README.md` alone, and each spec's own status line is a
historical artifact. The test now says so rather than asserting the opposite.

## 10. Change queue

**Empty.** Populated in v0.1 with eight items; all eight are now resolved.

| item | resolved in |
|---|---|
| assessment path exists | 0.1.1 (§3.4) |
| `lecture_number` vs directory | 0.1.2 (§9.6) |
| `exam_id` resolves into `_state.json` | 0.1.3 (§9.7 — was already implemented) |
| `lecture_id` value family | 0.1.3 (§9.8) |
| `unit` field type | 0.1.4 (§9.9) |
| kanban settings block | 0.1.5 (§9.10) |
| bare vs dotted lecture form | 0.1.6 (§9.11 — moot: no course mixes) |
| `Archived/` contents | 0.1.7 (§1.6 — exemption is deliberate) |
| legacy `status` on the exam family | 0.1.8 (§9.12) |

Nine rows for eight items because *`exam_id` resolves* and *`lecture_id` value
family* were one queue entry in v0.1 and split when the first turned out to be
already implemented.

Future gaps are **not** to be added here silently. A new item needs measured
evidence and a decision, and it enters this section in a version bump like every
other change — never as an unrecorded TODO in the code.

## 11. Companion tooling

```bash
python3 Agents/Courses/scripts/course_lint.py --vault . --cross-course
python3 Agents/Courses/scripts/course_lint.py --vault . --format json
python3 -m unittest discover -s Agents/Courses/tests
```

`repair.py` provides the mechanical fixes the linter's own checks can apply
(creating missing hubs and assessment subdirectories, adding `HUB.md`); it never
rewrites content. `--format json` is the integration surface for other tools.

Agent-facing pointers that must not restate rules live in
`Agents/Courses/skills/` (`course-linter/vault-layout.md`,
`course-linter/linter-expected-values.md`,
`exam-generator/course-folder-structure.md`). Each is a valid `SKILL.md` with
frontmatter whose body routes to this spec; the directory is skipped by course
discovery (§0.1).

Exit codes are listed in §0.3.
