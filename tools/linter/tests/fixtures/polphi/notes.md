# E2E fixture — Political Philosophy U1L1 Exam 02 → v0.11.1 JSON triple

**Source (read-only):**
`Agents/Courses/Philosophy/Political Philosophy/Unit 01 — Plato: Justice, Rule, Expertise, and
Political Order/Lecture 01 — Plato, Socrates, Athens, and the Problem of Political Expertise/
Exam 02/` — instructor key `Keys/Political-Philosophy-U1L1-Exam02-Instructor.md`, student paper
`Responses/Political-Philosophy-U1L1-Exam02-Student.md`, `HUB.md`.

**Produced:** `bundle.json`, `submission.json`, `report.json`, `validate.py`
(copied verbatim from `Agents/Design/linter/tests/fixtures/validate.py`; its `VAULT`, `SPEC`,
`HARNESS` and `FILES` constants already point at `verify_v111.py`, the 0.11.1 spec and this
directory's three files, so no edit was needed), `build_fixture.py` (generator: emits the three
JSON files and prints the §2.2.1 word counts), `notes.md`.

No vault file was written or modified.

## Shape

| item | value |
|---|---|
| assessment id | `pp-l1-1-exam-02` |
| sections | `section_i` (q1–q6), `section_ii` (group `section_ii_essays`) |
| short answers | 6 × `short_answer`, `points: "6"` → 36 |
| alternative set | `choose_n: 1`, `points: "14"`, alternatives `essay_a`/`essay_b` at `"14"` each, `credit` **absent** (absent = `equal`, §2.4.2) → 14 |
| total | `"50"` |
| delivery | `{"mode": "open_book"}` |
| gate | `{"mastery": false, "note": …}` — no `mode`, no `threshold_share` |
| floors | `[{"tier": "required", "min_share": "1", "applies_to": "all"}]` |
| sources | one: Schofield, `tier: required`, `category: secondary`, schemes `print_page`/`chapter`/`line`, all `verified` |
| answer key | `analytic_rubric` throughout (6 × 3 criteria; `essay_a`/`essay_b` 5 criteria each) |
| quote log | 28 entries, all `verified`, each located by `print_page` value **and** `line` |

The essay group deliberately omits `credit`: absence means `equal` and is the more demanding
test of §8 check 15 (every alternative's `points` must equal `group.points / choose_n` exactly).

## Floor: translated and checked

The key's Floors section states *"Required-tier share: 100% of points (50/50)"*, one declared
source at `tier: required`, and `applies_to: all` on the ground that the floor here is not a
mastery constraint but a statement that the paper has no other evidential basis. Translated
literally as `min_share: "1"`, `applies_to: "all"`.

Under §2.6.4 (0.11.1): the ordinary questions q1–q6 are each grounded in `required` (36
points); the group is evaluated under its worst legal selection — `choose_n` is 1, so the
least-grounded alternative counts, and both `essay_a` and `essay_b` carry locators, so the group
grounds `min(min(14, 14), 14) = 14`. `(36 + 14) / 50 = 1`, so `min_share: "1"` holds exactly
with no rounding. The validator confirms it (`semantic bundle: OK`).

The floor has teeth, and I checked that it does rather than assuming it. Three mutations of the
emitted bundle, each run through `verify_v111.semantic_bundle`:

- `essay_b`'s locators (entry and all criteria) removed →
  `floor required 1 unmet: group 'section_ii_essays' grounds 0 of its 14 (worst legal selection:
  the 1 least-grounded alternatives), 36 of 50 points grounded`. This is the anti-riding
  property: an alternative cannot ride on its grounded sibling, and at `choose_n: 1` the new
  rule computes what the old per-alternative rule did — the essay choice is load-bearing.
- `q5`'s locators removed → `… grounds 14 of its 14 …, 44 of 50 points grounded` (fails, as
  `44/50 < 1`).
- `min_share: "3/2"` → `min_share 3/2 not in (0, 1]`.

(The third probe I ran — setting `print_page` to `pending` while leaving the locators
`verified` — stayed clean, and correctly so: the source also carries a **verified range**
pp. 1–99, and §2.5.2's second limb lets a verified positional locator stand on a verified range
that contains it. That is the rule working, not a hole.)

## Judgement calls

**1. Word limits: `recorded`, not `capped`.** The key's only *first-person* statement of the
ranges is in a **time budget** ("Q1–Q3 (3 × ~3 min, 100–150 words each)", "Essay (~10 min,
250–300 words)"), i.e. the counts are derived from a speaking/writing rate, not imposed on the
answer. Two further facts settle it: (a) the key's own model answers run to **267, 365, 355,
340, 309 and 360 words** for Q1–Q6 — two to three times the stated maximum — so the range
demonstrably never bounded what a full answer looks like; (b) the only stated consequence
("answers over the word cap are not read beyond it") appears on the student paper and in
`HUB.md`, not in the key, and truncating a marked answer is a **scoring** consequence that
§2.2.1 requires the question's own `note` to state in full, and that §4.2 forbids as an
undeclared penalty — no criterion in the rubrics mentions length.

`recorded` is therefore the honest enforcement: the range, the §2.2.1 counting rule and the
breach are recorded; the score is untouched. Each question carries the required `note` saying
exactly that. The submission exercises the check on both sides — five of six short answers and
the essay are **inside** their range (140, 150, 148, 147, 150 words; essay 293) and produce no
`process_notes`, while q2 at **177 words** breaches the 150 maximum and produces exactly one
entry: `{"question_id": "q2", "count": 177, "bound": "max"}`. `q3` and `q6` sit exactly on the
boundary at 150 and are correctly treated as compliant (the bound is inclusive).

**2. Identifier normalisation (forced).** The vault's exam id is `pp-l1.1-exam-02` and its
segment id `lecture-01.1`; both contain `.`, which the spec's `^[A-Za-z][A-Za-z0-9_-]*$`
identifier pattern forbids for `assessment.id`, `segment.id` and every question/alternative id.
Translated to `pp-l1-1-exam-02` and `lecture-01-1`. This is a lossy but unavoidable
translation; the original strings are recorded here, and a consumer matching a segment id
against a course state file would need the mapping.

**3. Section id vs group id.** `section_ii` is the section; the alternative-set question had to
be renamed `section_ii_essays` because question, alternative and section ids share one ID space
(§2.1, §8 check 1) and the harness rejects the collision. The paper's own naming ("Section II")
is preserved in the section `title`.

**4. Locator status: `verified` for all three schemes, with the reconstruction recorded in the
source `note`.** The key's Locator status block marks `print_page` verified "pp. 1–99",
`chapter` verified, and `line` verified "1–18008". That is what was translated. But the key's
own *Source or Extraction Gaps* section says two page numerals (p. 7, p. 51) are absent from the
body and the pagination was fixed by counting running-heads — a stricter reading would call
those two pages `derived`. I did **not** downgrade them, because (i) the key states the scheme
verified and supports it with spot checks (p. 10, 33, 64, 77, 100), and (ii) `derived` requires
a `derived_from` naming a source range, and there is no clean range to name for "the page whose
footer was replaced by a chapter number". The caveat is carried, in prose, in
`assessment.sources[0].note`, which is the field §2.5.1 provides for exactly this. Anyone
re-verifying should read that note before trusting p. 7 or p. 51.

**5. No derived locators.** The key says "Derived locators: none", and none were introduced.
Every positional locator is a `print_page` value or range inside pp. 1–99, each either a
declared verified scheme or covered by a verified range.

**6. `line` locators.** The key's line numbers address a vault extraction
(`Raw/Sources/Philosophy/Political-Philosophy/Schofield-Plato-Political-Philosophy/
Schofield-Plato-Political-Philosophy.txt`, 18,008 lines). A locator carries exactly one scheme,
so the file cannot also be named in it; it is named in the source `note`. Line numbers are
declared `verified` as the key declares them, and are used only in the quote log (as re-checking
anchors), never as the grounding citation.

**7. Third-party quotations.** Where the key quotes Ferrari, Cooper, Dunn, Ober or Sedley, the
locator is to **Schofield's page**, exactly as the key does; the `attribution` field names the
original speaker. Those works are not declared as sources, because the key does not verify them
against the original either and declaring them would invent a second evidential basis the paper
does not have.

**8. Chapter 3.** It begins at p. 100 and is not examinable. No locator anywhere cites p. 100 or
`chapter: "3"`; the boundary is stated in prose in `assessment.instructions` and reflected in
the source's `ranges` (the assigned range stops at 99).

**9. `estimated_minutes`.** The key gives no per-question estimate. Derived from its time budget
table: 3 minutes per short answer, 10 for the essay → 28 minutes of item time against a
40-minute limit. No warning is triggered (28 ≤ 40). `response_lines` is a rendering decision
only (12 / 34), since the key prints no answer space.

**10. Why no `mastery`-scoped floor.** The key says `mastery: false`, and Exam 01 is the
lecture's mastery-gated paper. `applies_to: "mastery"` would have been unevaluable (§8 check 12
would still demand a `gate`); `all` is what the key asserts — the floor is a statement about the
paper's evidential basis, not about progression.

## Unrepresentable, or representable only with loss

- **The coverage audit's real shape.** The key's audit is a table keyed by *sections of the
  assigned source* (Introduction; ch. 1 §§1–5; ch. 2 §§1.1–4), with "questions that reach it".
  The spec keys `coverage.assessed[]` by **scope segment**, and this paper has exactly one
  segment (the lecture). So the audit collapses to a single `assessed` row listing all eight
  question/alternative ids, and the section-by-section map — the part a reader actually wants —
  survives only as the row's `note`, in prose. This is a genuine expressiveness gap: a
  one-segment assessment cannot carry a section-level coverage map as data. The six deliberate
  omissions are fully representable and were translated one-for-one with the key's own `reason`
  values (`time`, `scope`, `redundant`, `redundant`, `time`, `scope`).
- **The 2/2/2 and 3/3/4/2/2 point splits.** §4.2 forbids per-criterion maxima, so the key's
  bracketed weights cannot be data. They are recorded in each `reference_answer` as an
  authoring guide ("the key's bracketed split is 2/2/2 …"), and the report's awards are argued
  from the criterion descriptions instead. The consequence: the fixture's awards are *not* the
  key's 2/2/2 arithmetic and must not be read as it.
- **`capped` word limits.** See judgement call 1 — representable, but not honest here.
- **The key's "Strongly Recommended tier" (Waterfield; SEP).** Named in the lecture and
  explicitly excluded from the paper. Not declared as sources: declaring an uncited source would
  put a tier in `sources[]` that no locator uses, and §2.6.4 would then allow a floor on it.
- **The full 102-entry quote log.** The log is data and is not required to be exhaustive
  (§2.5.4). 28 entries are carried, chosen to cover every quotation used in the criteria and the
  key's own anchors; the remaining 74 were verified in the key and are not repeated. All 28 are
  `verified` in both schemes cited.
- **`exam_level`, `unit`, `course` frontmatter, the note-generation map.** Vault metadata with no
  field in this format. `scope` carries what the format can hold.

## What is synthetic

Everything in `submission.json`, and the awards, evidence and feedback in `report.json`.

- `submission_id` is `synthetic-pp-l1-1-exam-02-001` — the label is in the id, because the
  submission schema sets `additionalProperties: false` and there is no annotation field.
- The six short answers and the essay are **written for this fixture**, in a plausible graduate
  voice, from the key's model answers and from Schofield's own phrasing where the key quotes it.
  They are not a real student's work, and the 177-word q2 answer is deliberately over the cap.
- The awarding is synthetic too: one essay answered (`essay_a`), scores chosen to land on
  ordinary fractions and to exercise several criteria partially. **q1 9/2, q2 7/2, q3 4, q4 9/2,
  q5 4, q6 3** (= 47/2 for Section I) and **essay_a 3 + 5/2 + 5/2 + 3/2 + 1 = 21/2**.
  `total_awarded_points` is `"34"` of `"50"` — exact, reconciled by the harness, not a subtotal.
- `essay_b` was **not** answered. Under `choose_n: 1` it is neither counted nor ignored;
  `answered_alternative_ids: ["essay_a"]`, `ignored_alternative_ids: []`, and `essay_b`
  contributes no `criterion_scores`. The group is still marked out of its full 14 (§2.4.3).
- Every `justification` argues from the response text; the `evidence` field quotes the
  submission. No locator appears in the report — report locators are optional provenance, and
  inventing them to fill the field is what §9 forbids.

## Ambiguities I had to resolve

- **Does an alternative-set `max_points` include the group's own `points` or the counted
  alternatives' sum?** §6 is explicit (the group's `points`, the weight that does not move), and
  the harness enforces it. Used `"14"`, not `"14"` × counted.
- **`role` for `chapter` locators.** `primary` is the default and `cf` marks a *comparative*
  reference, which a chapter coordinate is not; the chapter locators beside each `print_page`
  range are therefore left at the default rather than being marked `cf`, even though they are
  secondary *coordinates*. Marking them `cf` would have said something about the citation's
  argumentative weight that the key does not say.
- **`floors` visibility.** Private (§1.1), and the assessment `instructions` therefore mention
  only the reading range and the word ranges — never the floor or the coverage audit.

## Validation

`python3 validate.py` (all three layers: schema extraction + `Draft202012Validator` +
`verify_v111.py`'s §8 checks 1–15 and its own 4,005-check self-run). Verbatim output:

```text
schema bundle    : 'Assessment Bundle v0.11.1' extracted and meta-valid
schema submission: 'Assessment Submission v0.11.1' extracted and meta-valid
schema report    : 'Assessment Grading Report v0.11.1' extracted and meta-valid

schema bundle    : OK  (bundle.json)
schema submission: OK  (submission.json)
schema report    : OK  (report.json)

harness self-run   : checks=4005 failures=0 warnings=0

semantic  bundle    : OK
semantic  submission: OK
semantic  report    : OK
semantic  word-limits: OK

questions: 7 (of which 1 alternative_set)  alternatives: 2
total possible points: 50  report total_possible_points: 50  awarded: 34

RESULT: ALL CLEAN — 3/3 schema valid, semantic checks 1-15 empty, totals reconcile
```

No warnings were raised (no capped-group warning, no unverified-quote warning, no timing
warning: 28 estimated minutes against a 40-minute limit).


**Version hop.** Migrated to 0.11.2 by its version string and nothing else (§10.2): 0.11.2 adds a
translation convention for a gate whose source records no mechanism, and changes no rule this
document is checked against, so the verdict is unchanged. The harness that validates this triple
is `Agents/Design/verify_v112.py`.


**Criterion weights (0.11.3).** Recorded from the source key, which states them per criterion:
`- [2 pts] (a) …` three times on each of Q1–Q6 (all 6-point questions), and the essays as
`3 + 3 + 4 + 2 + 2 = 14` (five numbered criteria each). Nothing was divided evenly — the
numbers are the key's own.
