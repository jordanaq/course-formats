# Translation notes — `daily-mip-01-01` (Modern Israel and Palestine, Lecture 01, Exam 01)

Source key: `Agents/Courses/History/Modern Israel and Palestine/Unit 01 — Zionism and Palestine,
c. 1880–1948/Lecture 01 — …/Exam 01/Keys/Modern-Israel-Palestine-L01-Instructor.md`
Spec: `Agents/Design/assessment-format-spec-v0.11.0.md`

Everything below is either a place where the key's prose had to be interpreted, or a field
deliberately left out. Nothing outside this file was invented to make a validator pass.

---

## 1. Structure

- **The key has no section headings.** It runs Q1 … Q5 under `## Question N` headings, and its own
  timing audit groups Q1–Q4 (short answers) apart from Q5 (essay). I therefore used two sections —
  `short_answers` ("Section I — Short answers (20 pts)", Q1–Q4) and `mini_essay`
  ("Section II — Mini-essay (10 pts)", Q5). The section *titles* are mine; the grouping is the
  key's. A one-section paper would also have been faithful; the two-section split was chosen
  because the brief states the paper has a short-answer section and further sections.
- Question **IDs are `q1`…`q5`** and alternatives are `q1_<term>`; display numbers are derived
  from array order per §2.1, so the ids carry no numbering claim.
- **Assessment id** is `daily-mip-01-01`, taken from the key's `exam_id` frontmatter. It is
  deliberately *not* `mip_l01_exam_01`, which is Appendix I's worked example of a **different**
  paper for the same lecture (single-choice + Pinsker + essays), so the fixture cannot be confused
  with it.

## 2. Question 1 — the pool question (`capped` credit)

- The key says "5 pts, 2/2/1" and, in its own note, "award 2/2/1 across the three chosen terms —
  full definition + significance earns 2; a solid but partial answer earns 1". That is a purse of
  5 over eight 2-point items, choose 3 — the exact shape §2.4.2's `capped` mode was added for.
  Translated as `{"mode": "capped"}`, `choose_n: 3`, `points: "5"`, eight alternatives at
  `points: "2"`.
- The **2/2/1** split is not encoded as per-criterion maxima (rubrics have none, §4.2). It lives
  where the key puts it: in the grader's freedom to award any rational in `0 … 2` per term, with
  the group clipped at 5. Each alternative carries exactly **one** criterion ("definition +
  significance"), as the brief requires; the key's "2 for full, 1 for partial" is stated inside
  that criterion's `description`.
- **Alternative prompts are derived, not quoted.** The key gives each term as a bold term plus a
  definition; the definition belongs in the answer key, so each alternative's `prompt` is the term
  plus the group's own instruction ("identify and briefly explain …, with its significance for the
  period 1880–1914"). Term names and spellings are the key's (`Filastin`, `Hibbat Zion (Lovers of
  Zion)`, `Tanzimat (1839–1876)`, `Jewish National Fund (Keren Kayemet, 1901)`).
- "**Old Yishuv vs. New Yishuv**" is one of the key's eight terms and so one alternative covering
  both halves — not two alternatives.
- The group `prompt` restates the count ("three of the following eight terms") and, because the
  credit is `capped`, the per-item worth — §7 requires both to be visible.

## 3. Points, timing, answer space

- Points are the key's exactly: Q1 5, Q2 5, Q3 5, Q4 5, Q5 10 → **30 total**, matching the key's
  "Total: 30 points".
- `estimated_minutes` come from the key's own **timing audit** (Q1 3.5, Q2 3, Q3 3, Q4 3, Q5 12).
  The eight Q1 alternatives each get `1` minute: the audit budgets 3.5 for three terms, and
  alternatives need a positive estimate. Sum of question estimates = 24.5 min against a 30-minute
  limit, consistent with the key's "~24–26 min active".
- **`response_lines` is invented** (Q1 alternatives 4, Q2–Q4 8, Q5 30). The key states no printed
  answer space; `response_lines` is presentation only (§2.2) and changes no score. The student
  response's own header says "≤120 words each" for Q1–Q4, but that instruction is in the response
  document, not the key, so it was **not** translated into word limits.

## 4. Word limit (Q5 only)

- The key states one cap: "Mini-essay (10 pts, ≈ half the exam time, ≤300 words)". Q2–Q4 state no
  cap, so they carry no `suggested_word_count`.
- `max: 300`, `enforcement: "recorded"` (the key treats the cap as a discipline note, not a
  deduction — its grading note says to use the key for weak areas, not to penalise), with the
  required `note` stating the consequence.
- **`min: 1` is not the key's.** The schema requires `min`, and the key states no floor. `min: 1`
  is the spec's own convention for a cap-only range (Appendix K.1, "a capped range" vector uses
  `min: 1, max: 120`); it means "any non-empty answer", and no response can breach it.
- The submission's Q5 is the vault's real student essay, **425 words** under §2.2.1's counting
  rule (recomputed by the validator, not copied from the feedback file's prose), so the report
  carries one `process_notes` entry: `count 425, bound "max"`. Nothing was deducted for it.

## 5. Sources and locators

Three sources, one per work the key actually cites:

| id | tier | why |
|---|---|---|
| `smith` | `required` | The lecture's "Required Primary Reading" (Smith, Ch. 1). Cited throughout. |
| `avineri` | `required` | "Required Secondary Reading" (Avineri, Chs. 9 and 11). |
| `mip_l01_lecture` | `required` | The course lecture note, cited once as "Lesson 01 Key Concepts". |

- **The lecture note's tier is a judgment call.** It is not on the reading list — it is the
  lecture — but it is assigned course material and testable, which is §2.6.2's `required`. It is
  not `supplemental` (that is for *consulted, not assigned* material such as a reference work).
  Flagged because a different reader could file it as `supplemental`; nothing in this document's
  arithmetic depends on the choice, since no `floors` are declared (§6 below).
- **The optional-tier readings are not sources.** Hertzberg, Avineri Ch. 7, Laqueur, Shlaim,
  Tessler and Gelvin are named in the key only to say they are *not* tested here. Declaring them
  as `sources[]` would assert citations the paper does not make, so they appear as `coverage`
  omissions instead. `Hertzberg` in particular was removed from Q4 by the key ("Q4 was tightened
  to cite Avineri Ch. 11 only"), so it is not cited anywhere.
- **Schemes.** Smith declares `chapter`, `section`, `document` (all `verified`) and `print_page`
  (`pending`, with a source note saying pagination is unverified). Avineri declares `chapter`
  (`verified`). The lecture note declares `heading` (`verified`). `document` is a declared,
  non-positional scheme for Smith's numbered documents (1.1–1.3), which the key cites by number;
  `section` carries Smith's own section titles, which the key names verbatim.
- **No page numbers anywhere.** The key states none, so none appear. The lecture note *does* give
  "pp. 13–49" for Smith Ch. 1 and page counts for Avineri, but the key does not cite them, and
  copying a range from a different document would be exactly the invented pagination §2.5.2
  forbids. `print_page` is declared `pending` precisely so the absence is recorded rather than
  implied.
- **`"Key Concepts"`** as the lecture-note heading value is a one-step derivation: the key says
  "Lesson 01 Key Concepts", and the lecture note has a `## Key Concepts` heading (checked in the
  file). Recorded here because the heading text is not in the key.

## 6. Gate and floors — both included

- **Gate included.** The key says "Formative (soft mastery)" and "Formative exam under
  soft-mastery policy — completion advances regardless of score". Translated as
  `{"mastery": true, "mode": "completion"}` with that sentence as the note, matching the spec's own
  treatment of soft mastery in Appendix I.1. Note the sibling `HUB.md` says "mastery gate: no
  progression block", which reads as `mastery: false`; the key — the authority here — says
  soft mastery, and Appendix I already encodes that as `mastery: true, mode: completion`.
- **`floors` included — after a spec correction.** The key claims the paper is "grounded in
  Lecture 01's required readings only … strictly required-only", i.e. `min_share: "1"`. Under
  **v0.11.0** that was unrepresentable: §2.6.4 evaluated an alternative set one alternative at a
  time, so the capped pool (8 × 2 points, `choose_n: 3`, a 5-point purse) could contribute at
  most 2 of its 5 points and the paper's maximum grounded share was 27/30 = `9/10`. Rather than
  invent `9/10`, the first translation omitted the floor and kept the claim in `coverage.note`.
  **v0.11.1** replaced the per-alternative rule with a per-selection one —
  `min(sum of the choose_n least-grounded alternatives, group.points)` — under which the pool
  grounds `min(2+2+2, 5) = 5`, every question in this paper is grounded in `required` sources,
  and `min_share: "1"` validates. The floor is now declared; the `coverage.note` that stood in
  for it is gone.

## 7. Coverage

- Translated from the key's "Coverage audit" paragraph. `scope` has a single segment, `mip-l01`
  (kind `lecture`), because the key's own record is per lecture; splitting it into lecture parts
  would invent segment boundaries the key never draws.
- `assessed`: `mip-l01` reached by `q1`–`q5` (the group counted once, by its own id).
- `omitted`: the six optional-tier readings, each `reason: "scope"` — the key's own reason
  ("deliberately NOT tested here — they are covered by Exam 02 (extension)"). `reason` is
  `scope`, not `deferred`, because they are not postponed within *this* paper; they belong to a
  different assessment.
- Documents 1.1–1.2 are **not** listed as omissions: the key says they "are not standalone items
  but are testable via Q2/Q3", i.e. they are reached, not left out.
- No supplemental research is claimed, per the key ("No supplemental research used") — reflected in
  the note rather than as an omission entry, since "nothing was consulted" is not an omission.

## 8. Quote log

Six entries, all from the key's own "Quote-verification log (2026-08-11)" and all `verified`,
because that is the status the key records:

1. "tossed about like a ball between its powerful neighbours" — Avineri Ch. 11.
2. "In contrast to the Christian ostentation, Jews accepted their official equality cautiously and
   without fanfare." — Smith Ch. 1. The key's log truncates this with "…"; the full sentence is
   quoted because the key gives it in full under Q2, point 2. Nothing was reconstructed.
3. "Herzl appears to tilt toward a solution based on the historical homeland of the Jewish people"
   — Avineri Ch. 9.
4. "foreign seizure of the land of Palestine" — Smith, Document 1.3.
5. "forced to emigrate and leave the country" — Smith, Document 1.3.
6. "referred to Palestine as an entity and to its readers as 'Palestinians.'" — Smith, section
   "Growing Apprehension: Palestine and the Arab World".

The key's caveat that **"dispossession" does not appear in Smith Ch. 1** (it is the lecture's gloss)
is not a quotation, so it is not a log entry; it is recorded here and kept in the reference answer
wording for Q5's first criterion ("the prompt's claim").

## 9. Submission

- Built from the vault's real student response
  (`Responses/Modern-Israel-Palestine-L01-Student.md`), not written from scratch — a fixture that
  agrees with the corpus is a better test than one that agrees with itself.
- **Q1 was split**: the response gives three numbered terms in one block; each numbered item became
  that alternative's `text`, unaltered. No wording was added, cut or reordered.
- Q2–Q5 are verbatim, including the student's own emphasis (`_al-Karmil_`, `_Filastin_`,
  `_Jewish National Fund_`) and its typographical errors ("It's most significant figure").
- Three alternatives answered against `choose_n: 3` → `ignored_alternative_ids: []`. **No
  over-answer case is exercised** by this fixture; a fourth answer would have been the natural way
  to test §2.4.4, but adding one would mean writing student text that does not exist.

## 10. Report

- Awards reproduce the vault's second regrade (`Feedback/…-Regraded-2026-09-14-v2.md`), so the
  fixture and the corpus agree: Q1 9/2, Q2 4, Q3 7/2, Q4 5/2, Q5 17/2 → **23/30**.
- The `capped` group's counted awards sum to 9/2, **below** the 5-point ceiling, so the cap does
  not bind and `uncapped_awarded_points` is correctly **absent** (§6: present exactly when the cap
  bound). This fixture therefore exercises the `capped` arithmetic but not the clipping branch. A
  variant that does: three terms at 2, 2, 2 → `awarded_points "5"` with
  `uncapped_awarded_points "6"`; not included, because it would contradict the real graded record.
- `criterion_scores` for the group are ordered by the group's alternative order (tanzimat,
  hibbat_zion, jnf — which is also their paper order), each carrying `alternative_id`.
- Locators in the report are sparse and only where they ground a remark; no locator was added to
  fill a field (§9, grading-agent rule 8).
- `process_notes` holds the single Q5 word-limit breach. No other limit exists on this paper, so
  nothing else could be recorded.

## 11. Not translated

- The key's **timing audit table** (per-item minutes and slack) and **note-generation design**
  paragraph are planning prose, not assessment content; the only part that had a field was the
  per-item minutes, used for `estimated_minutes`.
- The key's **"Grading note"** ("use the key to identify weak areas for spaced retrieval, not to
  gate progression") has no field: the format records a gate, not advice about what to do with a
  score (§2.6.3, last bullet).
- The key's **frontmatter** (`course`, `kind`, `exam_id`) is represented only by `scope.course.id`
  and the assessment id; `kind: exam-key` is a file role, not a document field.


**Version hop.** Migrated to 0.11.2 by its version string and nothing else (§10.2): 0.11.2 adds a
translation convention for a gate whose source records no mechanism, and changes no rule this
document is checked against, so the verdict is unchanged. The harness that validates this triple
is `Agents/Design/verify_v112.py`.


**Criterion weights (0.11.3).** Recorded from the source key, which states them:
`## Question 2 — Short answer (5 pts, 2/2/1)` (also Q3 and Q4) and
`## Question 5 — Mini-essay (10 pts, …)` / `**Key points (4/3/3):**`. Q1's pool states
`award 2/2/1 across the three chosen terms — full definition + significance earns 2`, so each
alternative's single criterion is worth `2` and the group's 5-point ceiling is the §2.4.2 cap,
not a partition. Every rubric here sums exactly to its question: `2+2+1 = 5`, `4+3+3 = 10`.
