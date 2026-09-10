# r27 scope-alignment candidate — 2026-09-10 (revision 2)

Main: `paper/main.pdf` (58 pages); supplement: `paper/supplement.pdf`
(14 pages). Current manifest: `MANIFEST-r27.json`.
Review decisions: `docs/R27-REVIEW-DISPOSITION-zh.md`.

Current witness: `code/formal-fixed/observation_witnesses.py`.
Current report: `evidence/r27-witness/observation-witness-report-v5.json`.
Five original class pairs, the additional candidate-identity pair, and the
copy-forward control are retained; all 19 witness tests passed in this revision.
Run in `code/formal-fixed/`: `python -m unittest discover -s tests -v`.

The r27 formal catalogue has 34 Alloy commands per profile (68 total),
including `LegalAdmissionTraceCompleteUnderWellFormedPre` and its mutation
control under `evidence/r27-trace-mutation/`. The positive assertion is
conditional on a trace-complete pre-state with no stray successor-version
transition; those dependencies are implemented by predecessor-prefix trace
validation, the per-record uniqueness constraint on fact transitions, and
compare-and-swap admission with in-transaction revalidation. Deleting the
post-state certificate binding flips the assertion from UNSAT to SAT. The
packaged `formal/alloy/batch/verify_batch_package.ps1 -RequireRawResults`
gate passes against the delivered package.

The r27 benign-completion endpoint was coded by one author (X.W.) and one
non-author volunteer. The non-author coder was blind to the deterministic rule
labels, configuration identifiers, prompt variants, repetitions, and study
hypotheses; the author coder was blind to the rule labels and configuration
identifiers at coding time but was not blind to the study hypotheses. The 12
pre-adjudication disagreements (11 human--rule cases and T153) were adjudicated
by the other author and are reported as author-involved annotation and author
adjudication, not as independent third-party annotation. Full analysis is under
`evidence/human-annotation-2026-09-10/`, including the 360-row normalized labels
(`labels-A1-A2-normalized.csv`), the standard-library recomputation script
(`recompute_irr.py`), and the (unused) third-party adjudication protocol and
blank template. The supplement adds per-model missingness and
case-/model-/cell-level interval tables; the main-text intervals are case-level
and follow the packaged recomputation script.

The minimal ordinary approval/audit-log baseline is under
`evidence/r27-standard-practice-baseline/`. It agrees with the candidate-bound
policy on seven of eight single-history cases, diverges only on equal-valued
candidate substitution, reconstructs per-field sources from its audit log, but
cannot uniquely attribute the reviewed candidate or the proposed value.

Implementation sources/tests match r26 byte for byte. Its 389-test isolated run
is retained as prior verification, not claimed as rerun here. Model/runtime
dependencies remain included under `formal/` and `tools/`.

The input audit checks 1,260 prepared/prompt contexts and declaration structure;
the fourteen-scenario table states endpoint limits, not semantic validation.
Regenerate with `code/scripts/audit_scenario_inputs.py --final-root <Final> --output <new.json>`.

Use the unified package for complete immutable v8 raw evidence plus current code
and manuscript. Its top-level manifest and extended source crosswalk bind both
layers. Old manifests, reports and version-specific packaging scripts describe
prior versions; they are not the current package index. Caches are excluded.
Local absolute paths in the current-package logs were normalized to `<PROJECT_ROOT>`; the historical `baseline-v8/` export is retained byte-for-byte and may contain author-local paths inside historical logs.

The second author's email and a DOI remain pending. Performance stays v8.
