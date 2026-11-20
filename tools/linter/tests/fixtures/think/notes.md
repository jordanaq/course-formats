# Think Exam 05 → v0.11.1 E2E fixture — judgement calls and evidence

Output directory: `/home/tsiru/.hermes/cache/scratch/linter-e2e-think/`

| file | what it is |
|---|---|
| `bundle.json` | 8 questions, 20 points, open book, 2 declared sources, coverage audit |
| `submission.json` | **synthetic** student response (see §6) |
| `report.json` | grading of that synthetic response: **35/2 of 20** |
| `validate.py` | the shipped fixture validator, copied verbatim (see §8) |
| `build_docs.py` | deterministic builder that writes the three documents and asserts the totals |

(The shipped fixture's own `bundle/submission/report.json` were copied in temporarily to
confirm the harness self-run was clean before I started, then deleted.)

Vault status: read-only throughout. I issued no write, move or delete under
`/home/tsiru/Documents/Obsidian-Vault`.

---

## 1. The exam paper is not where the brief says it is

The brief names `Exam 05/Part-5-God-Exam.md`. That file does not exist. The directory holds:

```
Exam 05/HUB.md                                  (metadata stub: structure only)
Exam 05/Keys/Part-5-God-Instructor.md           the key
Exam 05/Responses/Part-5-God-Student.md         the paper, despite the folder name
Exam 05/Feedback/Part-5-God-Graded-2026-07-23.md  a graded response (see §2)
```

`Responses/Part-5-God-Student.md` is titled *"Open-Book Self-Study Exam"*, has
`**Time:** 20 minutes`, `**Points:** 20`, an Instructions block, and Parts I–III with the
stems and options A–D — and **no answers**. It is the paper. Its `kind:` front-matter says
`exam-response`, which is why it was filed under Responses, but nothing in it is a response.
I used it as the authoritative question text.

Fidelity check, run programmatically: extracted the 20 option lines from the paper and
compared them to the bundle's 20 options — **20/20 exact, 0 mismatches**. Stem comparison
differs only in the two places listed in §7.1: the inline `(N points)` markers were dropped
(points are structural fields) and Q8's block-quoted scenario was inlined into the single
prompt string.

## 2. The brief's premise "there is no real student answer" is false

`Feedback/Part-5-God-Graded-2026-07-23.md` contains a recorded response with per-question
teacher feedback and a **18 / 20** total, including full student prose for Q6–Q8.

I did **not** reuse it. `submission.json` is an independently written synthetic answer
(§6). Two reasons: the brief asks for a synthetic submission, and presenting a real
recorded response as synthetic would be a false claim about provenance. But the discovery is
worth recording for the linter work:

- The feedback's Q6 rubric is *"Reconstruction / Evidential objection / Scope objection /
  Clean separation of parallel objections"*. The key's Q6 bullets are *"resemblance and
  analogy / inference to an intelligent cause / evidential objection / scope objection"* —
  a different fourth criterion, and the feedback gives the 4th mark for a property ("clean
  separation") the key never asks for. So the key and the feedback do not share a rubric.
  My rubric follows the **key**, since the brief makes the key authoritative.
- The feedback's total (18) is reachable from my rubric too, but my synthetic script lands
  on 35/2 — a different number on purpose, so the two cannot be confused.

## 3. Gate: declared from course policy (corrected)

The exam's own key states no gate: total 20, "Intended time: 20 minutes, open book", primary
source. A first pass therefore omitted `gate` — and that was wrong, because omitting it
*asserts* `mastery: false`, contradicting the corpus:

- `Think/_state.json` → `assessments[exam-05].mastery_gate: true`
- `Think/HUB.md`: "each unit concludes with a unit essay exam with a mastery gate (e.g.,
  Exam 05 completed 2026-07-23)"
- The sibling unit exams state the mechanism explicitly: "Mastery gate: >=14/20 for unit
  credit (per course policy, unit exam is mastery-gated)" — Exams 06, 07 and 08, all
  20-point unit papers like this one.

So the gate is `{"mastery": true, "mode": "score", "threshold_share": "7/10"}`, with the
evidence in `note`. **14/20 of a 20-point paper is exactly 7/10** (§2.3.1's exact-rational
arithmetic, the same conversion §2.6.3 works through). Nothing here is invented: the gate is
course policy, the threshold is the one the sibling keys record, and the note says that this
paper's own key is silent about it.

The earlier reasoning — "§2.6.3 requires a mode, so declaring the gate means inventing one" —
was reading the spec correctly and the corpus incorrectly: the mode is not a guess, it is in
the three neighbouring keys.

## 4. Floors: none declared, and the paper would pass one

The key states no required-reading share, so no floor is declared rather than inventing one.
For the record (verified by inspection, not encoded): all 8 questions carry at least one
`blackburn-think` locator on the key entry or a criterion, so a hypothetical
`{tier: required, min_share: "1", applies_to: "all"}` would be satisfied at 20/20. The
omission is not hiding a failure.

## 5. Sources and locators

### 5.1 What the key cites, and what I declared

| key's citation | declared as |
|---|---|
| "Blackburn, Chapter 5" (front matter, every `**Source:**` line) | `blackburn-think`, scheme `chapter`, value `"5"`, **verified** |
| named sections — "Anselm's Argument: Dreamboats and Turkeys", "Elephants and Tortoises", "The Wise Architect", "The Problem of Evil", "Miracles and Testimony", "Infini—Rien" | scheme `section`, value = the title as the key gives it, **pending** |
| "full-TXT lines 2066–2088" and 9 other ranges | scheme `fulltxt_line`, `range: {from, to}`, **pending** |
| `[[Part-5-God#The ontological argument]]` and siblings | `part-5-god-notes`, scheme `heading` (the heading that exists), **verified**; plus one `path` locator |

Tiers: `blackburn-think` = `required` (the course HUB's "**Required (primary):** Blackburn's
*Think* — the sole primary text", hence also `category: primary`); `part-5-god-notes` =
`supplemental` (§2.6.2's "a course wiki page"). The key states no tier for the note, only
that it is a "Study aid".

### 5.2 Why `fulltxt_line` is a new scheme name

The key's line numbers belong to a Calibre **text extraction**, not to the printed book's
own lineation. §2.5.1's `line` is a *positional* scheme — the source's own numbering — and
using it would assert that these numbers index Blackburn. They do not; and the key's own
disclosure says the extract "was deleted after generation and verification", so the numbered
artifact no longer exists. §2.5.1 makes scheme names an open declared vocabulary, so I
declared `fulltxt_line` and left the scheme **pending**: **the honest status for a
coordinate system whose artifact is gone.** Every locator on it is `pending`.

I marked `chapter` verified on the strength of three vault records that agree (key front
matter, the note's `## Source` section, the course HUB), not on a fresh pass through the
book — the value is a constant ("5") and none of the three records disputes it. **If a
stricter reading of "checked against the source itself" is wanted, `chapter` should be
`pending` too;** nothing else in the document depends on it, since floors are not declared.

No `print_page`, `pdf_page` or `physical_page` scheme is declared *at all*. No page number
appears anywhere in the fixture, because none was verified. That is §2.5.2's "no invented
page ranges" applied by refusing the coordinate system rather than by guessing inside it.

### 5.3 The note's chapter span: a range I could not honestly record

`Part-5-God.md`'s footnote says "Chapter 5 spans full-text lines 1941–2514". Every range the
key cites (2066–2088 … 2390–2478) falls inside it — a consistency check that passed. But
`sources[].ranges[].status` is only `verified | derived`, and this range is neither: it was
not checked against the source (the extract is gone) and it was not computed from another
pagination. So the fact lives in the source's `note` prose, not in `ranges[]`. **There is no
state for "recorded from an artifact that has since been destroyed."**

### 5.4 The key's wikilink anchors do not resolve

`Part-5-God.md` is a navigation hub. Its only headings are `Chapter map`, `Sub-pages`,
`Dialectical conclusions`, `Cross-references`, `Source`. The argument headings the key links
to — `The ontological argument`, `The cosmological argument`, `The argument from design`,
`Miracles and testimony`, `Pascal's wager` — live in the sibling files
`Part-5-God/Arguments.md`, `Problem-of-Evil.md` and `Faith-and-Reason.md`.

Each `heading` locator therefore names the heading that actually exists and says in its
`note` which file carries it. For Q4 the key's anchor is `#The problem of evil`, which exists
nowhere as a heading; the nearest real heading (`Epicurean pressure`, in
`Problem-of-Evil.md`) is what I cited, with that stated in the note rather than silently
substituted.

## 6. The submission is synthetic

`submission_id: "synthetic_exam05_response_001"` — the label is in the identifier, so no
consumer can mistake it for a real attempt; this note says it too. No student wrote it.

It was written to be plausible second-year graduate work with deliberate, realistic
imperfections, so that the report exercises every award shape:

- wrong on Q3 (picks option D, reading Philo's organism analogy as a positive conclusion);
- Q6: both objections named, neither developed → 1/2 + 1/2 on two criteria;
- Q7: complete → 4/4;
- Q8: strong thesis, reconstruction and false-options objection; the
  ignorance/assignment point is asserted rather than argued → 1/2.

## 7. What the key states vs what the bundle says

### 7.1 Deliberate, disclosed changes to the paper's text

1. **`(1 point)` / `(4 points)` markers removed from stems.** `points` is a structural field
   and §7 requires the renderer to compute the display number; leaving the marker in the
   prompt would print the weight twice. Nothing else in a stem changed.
2. **Q8's block quote inlined.** The paper sets the quoted speaker in a blockquote and then a
   separate instruction paragraph. A `prompt` is one plain-text string, so the two are joined
   with the quotation marks preserved.
3. **Markdown emphasis stripped** (`*a posteriori*` → `a posteriori`), per §1: question
   content is plain text, not Markdown.

### 7.2 Types

Q1–Q5 are `single_choice` (1 point each). Q6, Q7, Q8 are `short_answer`. Q8 is the paper's
"Brief Argument/Application" — 7 points, 7 minutes, 22 lines — and the brief says
`short_answer` for everything that is not MCQ, so it is not `essay`. Consequence worth
knowing: **the fixture contains no `essay` question, so the essay branch of check 3 is
untested here.**

### 7.3 Points and time

5×1 + 4 + 4 + 7 = **20**, matching the key. `estimated_minutes` 1,1,1,1,1,4,4,7 = **20**,
matching the key's timing audit (5 + 8 + 7). `time_limit_minutes: 20`.

The course state file says `duration_minutes: 30` for exam-05. I used 20 — the key says
"Intended time: 20 minutes" and the paper says "Time: 20 minutes". The 30 is recorded here
as a contradiction between the course record and the paper; I did not average them or pick
the more generous one.

### 7.4 Rubrics

Criteria follow the key's own point bullets, one criterion per bullet: 4 for Q6, 4 for Q7,
5 for Q8 (1 + 2 + 2 + 1 + 1 = 7). The key's per-element weights have **no field** in 0.11.1
(§4.2 removed per-criterion maxima), so each weight is stated in the criterion's
`description` prose ("weights this element at 2 of the question's 7 points"). That is the
only place the key's arithmetic survives, and it had to be kept: without it a grader cannot
tell a 2-point element from a 1-point one.

### 7.5 Word limits: none, because the key states none

The key gives no length limit and the paper prints no range. So no `suggested_word_count`
anywhere and no `process_notes`. **Check 14 is vacuous for this fixture** — worth saying
plainly, since "clean" on check 14 here means "nothing to check", not "the count is right".

### 7.6 Coverage

Lifted from the key's "Coverage audit" table and its "Proportionality and omissions" list.
Ambiguity handled in §9.2.

## 8. Validation

`validate.py` was copied from `Agents/Design/linter/tests/fixtures/validate.py` **verbatim**
(`cmp` confirms it is identical). **No constant needed adapting:** its `FILES` are built from
`HERE` (the script's own directory), so the copy validates the documents next to it; its
`HARNESS` already names `Agents/Design/verify_v111.py` and its `SPEC` already names
`assessment-format-spec-v0.11.1.md`, and the harness it loads pins `VERSION = "0.11.1"`.
Pointing it at the real vault paths was the only requirement, and those paths were already
correct.

Before writing anything I ran it against the shipped fixture's own three documents to confirm
the harness self-run is clean in this environment (`checks=4005 failures=0 warnings=0`), so a
later failure could not be blamed on a pre-broken harness.

Non-vacuity checks (each run in place, then the documents rebuilt):

| mutation | result |
|---|---|
| `total_awarded_points` "35/2" → "18" | `FAIL: report: report total 18 != sum of awards 35/2` |
| Q6 `awarded_points` "3" → "7/2" | `FAIL: report q6: criterion awards sum 3 != awarded 7/2` (+ total mismatch) |
| declare `print_page` pending and cite it `verified` | `FAIL: key q1: verified locator on positional scheme 'print_page' not backed by a verified declaration or range` |

So checks 6 and 10 really fire on this fixture; "clean" is not silence.

## 9. What I could not express, and where the spec is ambiguous

1. **The key's "Acceptable alternatives"** (Q6: the anthropocentric-privilege line or the
   generation/vegetation analogy earns the evidential point; apprentice / multiple / dead
   deity earns the scope point). The generation analogy is folded into `q6_c3`'s description
   as one of the accepted grounds, but there is no way to declare "this *other* line of
   argument satisfies this criterion" as structure — only as prose a grader must read.
2. **Coverage's unit is the segment; the key's audit unit is the learning objective.** §11
   explicitly refuses learning-objective ids, so the key's six-row objective table cannot be
   keyed. The course state file records `covers_segment_ids: ["part-5-god"]` for exam-05, so
   the whole paper maps to that one segment and `assessed` becomes nearly vacuous (one row,
   eight question ids). The audit's real content ends up in `omitted[]`, which is honest — the
   key's interesting claim is about what it leaves out, not what it reaches. A paper whose
   scope is a single segment simply has nowhere else to put "which argument cluster each
   question tests".
3. **Q8's "Strong-answer elements may include"** (four bullets: belief not immediately
   voluntary; rival religions multiply options; infinite utility needs justified
   probabilities; the objection targets practical rationality). The key assigns them **no
   points** — they are qualities, not criteria. Adding them as criteria would silently change
   the rubric from the key's 1/2/2/1/1, so they are not in the bundle at all. This is the
   clearest loss in the translation: a fifth of the key's guidance for Q8 has no home.
4. **The mastery gate** (§3) — recorded in the course state, unstateable from the key.
5. **The key's "Source and research disclosure"** (authority of the original over the note;
   the extraction gap; 12,490 words) has no field. A fragment went into
   `blackburn-think`'s `note` (why every line citation is pending); the rest is only here.
6. **A "verified" locator on a non-positional scheme is ungated.** §8 check 6 gates `verified`
   only for `print_page`, `pdf_page`, `physical_page` and `line`. A `heading` or `path`
   locator marked `verified` passes even if the source declares that scheme `pending`, and
   even if the heading does not exist — nothing checks that a heading's text occurs in the
   file, because the format has no way to read the file. My heading locators are `verified`
   because I did check them by hand; a validator cannot reproduce that.
7. **No state for a destroyed artifact.** `verified` and `derived` are the only range states,
   and `pending` is not available for a range (§2.5.1's table), although it is for a scheme
   and for a locator. That asymmetry is what forced the chapter span out of `ranges[]` (§5.3).
8. **`short_answer` with a 5-criterion, 7-point argument.** The format permits it
   (`response_lines` is the only type-specific requirement, and `analytic_rubric` is allowed
   for short answers), but there is no way to say "this is argumentative rather than
   recitational" — the paper's own section name carries that, and the section title is the
   only place it survives.

## 10. Report arithmetic, spelled out

| question | max | award | how |
|---|---:|---:|---|
| q1 | 1 | 1 | single_choice, all-or-nothing, selected = correct |
| q2 | 1 | 1 | " |
| q3 | 1 | 0 | selected d, correct c |
| q4 | 1 | 1 | " |
| q5 | 1 | 1 | " |
| q6 | 4 | 3 | 1 + 1 + 1/2 + 1/2 |
| q7 | 4 | 4 | 1 + 1 + 1 + 1 |
| q8 | 7 | 13/2 | 1 + 2 + 2 + 1/2 + 1 |
| **total** | **20** | **35/2** | 4 + 3 + 4 + 13/2 |

Every award is a canonical rational string in lowest terms; `35/2` is integral in no smaller
form, so it stays a fraction (display: 17.5). Single-choice grading is §3.2 all-or-nothing —
**§3.3's partial-credit formula never applies here, because the paper has no
`multiple_select` question.** The brief's "§3.3 arithmetic" therefore has no purchase on
this paper; the fractional awards in the report are §4.2 rubric rationals, not partial
credit.


**Version hop.** Migrated to 0.11.2 by its version string and nothing else (§10.2): 0.11.2 adds a
translation convention for a gate whose source records no mechanism, and changes no rule this
document is checked against, so the verdict is unchanged. The harness that validates this triple
is `Agents/Design/verify_v112.py`.
