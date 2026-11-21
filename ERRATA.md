# Format errata

This file records conflicts found **inside the canonical formats**. App-specific profiles,
fixture conversions, and product decisions stay in the consuming repositories
(`course-organizer/docs/spec-reconciliation.md` and `assessment-cli/docs/PLAN.md`).

Current release: `v0.13.0` — assessment `0.12.1`, submission `0.5`, course `0.1.11`.
The assessment/submission errata below were resolved in `v0.12.1`; `v0.12.2` adds the
course-structure spec unchanged; `v0.12.3` adds the `studentVisible` projection annotations
and no format change; `v0.13.0` moves the artifacts to the repository root and changes no
format.

## Layout change in v0.13.0

`schemas/`, `specs/` and `fixtures/` now sit at the repository root and `releases/<release>/`
holds only `manifest.json`. A release is the tag plus that manifest; the directory copies that
`v0.12.0`–`v0.12.2` carry are history and stay untouched, and `v0.12.3`'s copies remain in its
tag. Nothing a consumer validates changed: `v0.13.0` carries the same schema, prose and
fixtures it inherited from `v0.12.3` byte-for-byte, so format versions stay at assessment
`0.12.1` / submission `0.5` / course `0.1.11`. What changes is where a manifest's paths point:
root-relative from `v0.13.0`, `releases/<release>/…` before it. Consumers must read paths from
the manifest rather than composing them. `tools/release-check/check_release.py` now enforces
the manifest pins, schema meta-validation, vector counts and spec-block drift against either
the working tree or a tag.

## Added in v0.12.3

Not a conflict, but a change to the assessment bundle schema that release notes must carry. The
bundle schema released in `v0.12.3` (now `schemas/assessment-bundle.schema.json`) annotates 75 property
occurrences with the custom keyword `studentVisible: true`; the extension key `format_version` is
annotated too, so a projection can report which format it rendered. It is an annotation for a
projection consumer only: shapes, values, required fields and validation verdicts are identical
to `v0.12.2` (checked over 1,615 documents, 204 of them valid). The assessment format version
therefore stays `0.12.1`.

Annotated: root `format_version` and `assessment`; the `assessment` metadata, sections, sources,
scope, gate and delivery occurrences; `section` id/title/instructions/source_material/questions;
every `question` branch (identity, type, prompt, points, estimated minutes, and that branch's own
options/scoring/word-count/alternative fields); `option`; `word_count`; `credit.mode`; `source`
id/citation/tier/category; `scope` course/segments; `course_ref` and `segment_ref`; `gate`
mastery/mode/threshold_share; `delivery.mode`.

Deliberately unannotated: root `answer_key` and `quote_verification`; `assessment.floors` and
`assessment.coverage`; locators and their positions/statuses; `derived_from`; the free-text
`note` fields on `source`, `scope` and `gate`. `source.schemes` and `source.ranges` stay invisible
pending review of real examples. Absence of `studentVisible: true` means a property is excluded,
and a projection must fail closed on unclassified fields, malformed annotations, ambiguous
`oneOf` branches and unresolvable `$ref`s. Annotations sit on occurrences, never on the shared
`$defs` scalars (`id`, `nonempty`, `point_value`). The spec's Appendix A.1 block carries the same
annotated schema, kept identical by hand as with every earlier release.

Open: whether `source.ranges`/`schemes` and the deferred `note` fields are ever safe to show, and
whether the projection consumer resolves branches well enough to use the annotations. §1.1 and §7
remain the authority for what a student may see.

## Resolved in v0.12.1

| Area | What conflicted | Resolution | Normative text |
| --- | --- | --- | --- |
| Feedback completeness | Submission §6 and §8 check 6 said feedback was all-or-nothing per document; §6.1 and §8 check 9 allowed partial feedback with `complete: false`. | Partial feedback is legal while `grading.complete` is `false`. Once it is `true`, every question carries feedback. | Submission §6, §6.1, §8 check 6 |
| Counted alternatives | Submission §11 appeared to put every answered alternative in `counted_alternative_ids` and also put the extras in `ignored_alternative_ids`; assessment §2.4.4 grades only the first `choose_n` in paper order. | `counted_alternative_ids` is the first `choose_n` answered alternatives in the group's order; `ignored_alternative_ids` is the rest. The arrays partition the answered alternatives. | Submission §8 check 7, §11; schema descriptions; assessment §2.4.4 |
| Capped groups | Assessment §8 check 5 and §9 generation step 6 stated `group.points / choose_n` unconditionally; §2.4.2 and §8 check 15 allow `capped` groups with their own alternative maxima. | The equality applies only under `equal` credit (also the default when `credit` is absent). Under `capped`, each alternative keeps its own maximum and the group's `points` is the ceiling. | Assessment §8 check 5, §9 step 6 |
| Unweighted rubrics | Assessment §4.2.1 said an unweighted rubric's total is clipped at the question maximum; §4.2 and §8 check 8 require the recorded award to be the exact sum of the criterion awards within the maximum. | No post-hoc clipping. Each criterion remains awardable up to the question's points, but the grader must keep the exact sum at or below the question maximum. | Assessment §4.2, §4.2.1, §8 check 8, §9 grading step 5 |
| Sidecar reports | Course v0.1.11 §1.5 lists `Responses/<id>.report.json`; assessment §6 defers a new report and submission §12 puts it out of scope. | A 0.11.3 sidecar report is historical. This format neither produces nor consumes one; a course profile that accepts one declares a compatibility extension. | Submission §12; assessment §6 |
| Version and examples | Current appendix bundles still carried `0.11.3`; several appendices embedded the old submission map and grading report without labelling them. | Current bundle examples carry `format_version: "0.12.1"`. The 0.11.3-era submission and report examples remain as explicitly historical shape notes. | Assessment Appendix B, F, G, H, I |
| Paired submission citations | The assessment spec cited `submission-format-spec-v0.3.md` while the paired submission revision is 0.5. | Current references name the unversioned `submission-format-spec.md`; historical version names remain only where the text is describing history. | Assessment throughout |

## Open items

These are not silently decided. Each needs either a format change or a recorded
"spec is silent" decision.

| Area | Question | Where it belongs |
| --- | --- | --- |
| Ignored over-answer word checks | Does an ignored alternative's text still get a `process_notes` breach entry, or only the counted alternatives? | Assessment §2.2.1/§8 check 14 and submission §11 |
| Pending locators | The wording around `pending` provenance and what a validator may conclude from it needs a single reading. | Assessment §2.5 and §8 check 6 |
| Rubric prose caps | When a rubric description states a prose cap ("no more than 2 points for X"), how does it reconcile with the free-rational award rule? | Assessment §4.2.1 |
| Course-spec findings | Lecture ID padding, legacy state field counts, required-field counts, discovery ambiguity, and the stale `submission-format-spec-v0.3.md` citation. | Course-structure spec once it moves here (C01–C05 in `course-organizer/docs/design-review.md`) |
| Schema generation and drift | The specs embed copies of the schemas. A generator must make the canonical schema files the only editable source; the drift **check** now exists (`tools/release-check/`), the generator does not. | `tools/` |
| Prose examples as tests | The current appendix bundles are not yet extracted into the release fixtures or validated alongside the schema. | `fixtures/`, `tools/` |
| Linter migration | The Python linter still scrapes fenced markdown and expects versioned filenames. | `tools/linter/` |

## Adding an entry

1. Cite the section in each document that disagrees.
2. State the resolution as normative text, or mark the silence as a deliberate decision.
3. Update the paired specs and schemas in one release; never edit a tagged release.
4. Add a conformance vector when the resolution changes arithmetic or validation.
