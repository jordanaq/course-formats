# Format errata

This file records conflicts found **inside the canonical formats**. App-specific profiles,
fixture conversions, and product decisions stay in the consuming repositories
(`course-organizer/docs/spec-reconciliation.md` and `assessment-cli/docs/PLAN.md`).

Current release: `v0.12.1` — assessment `0.12.1`, submission `0.5`.

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
| Schema generation and drift | The specs embed copies of the schemas. A generator and drift check must make the canonical schema files the only editable source. | `tools/` |
| Prose examples as tests | The current appendix bundles are not yet extracted into the release fixtures or validated alongside the schema. | `releases/<release>/fixtures/`, `tools/` |
| Linter migration | The Python linter still scrapes fenced markdown and expects versioned filenames. | `tools/linter/` |

## Adding an entry

1. Cite the section in each document that disagrees.
2. State the resolution as normative text, or mark the silence as a deliberate decision.
3. Update the paired specs and schemas in one release; never edit a tagged release.
4. Add a conformance vector when the resolution changes arithmetic or validation.
