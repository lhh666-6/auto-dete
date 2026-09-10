# r27 scope-alignment candidate — 2026-09-10

Main: `paper/main.pdf` (58 pages); supplement: `paper/supplement.pdf`
(12 pages). Current manifest: `MANIFEST-r27.json`.
Review decisions: `docs/R27-REVIEW-DISPOSITION-zh.md`.

Current witness: `code/formal-fixed/observation_witnesses.py`.
Current report: `evidence/r27-witness/observation-witness-report-v5.json`.
Five original pairs and copy-forward control are unchanged; an additional D_C
pair isolates candidate identity. All 19 witness tests passed in this revision.
Run in `code/formal-fixed/`: `python -m unittest discover -s tests -v`.

The r27 formal catalogue now has 34 Alloy commands per profile (68 total),
including `LegalAdmissionTraceCompleteUnderWellFormedPre` and its mutation
control under `evidence/r27-trace-mutation/`. The assertion is conditional on a
trace-complete pre-state with no stray successor-version transition; those are
the preconditions the concrete service enforces through reverse-trace
validation and compare-and-swap. Deleting the post-state certificate binding
flips the assertion from UNSAT to SAT.

The r27 benign-completion endpoint has two independent non-author human
annotators; full analysis is under `evidence/human-annotation-2026-09-10/`.
Main-text intervals are case-level; the archive also provides model- and
cell-level cluster-robust bootstrap intervals.

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

Annotation and authorship are recorded; the second author's email and a DOI
remain pending for final submission. Performance stays v8.
