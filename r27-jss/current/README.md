# r27 scope-alignment candidate — 2026-09-09

Main: `paper/main.pdf` (56 pages); supplement: `paper/supplement.pdf`
(11 pages). Current manifest: `MANIFEST-r27.json`.
Review decisions: `docs/R27-REVIEW-DISPOSITION-zh.md`.

Current witness: `code/formal-fixed/observation_witnesses.py`.
Current report: `evidence/r27-witness/observation-witness-report-v5.json`.
Five original pairs and copy-forward control are unchanged; an additional D_C
pair isolates candidate identity. All 19 witness tests passed in this revision.
Run in `code/formal-fixed/`: `python -m unittest discover -s tests -v`.

Implementation sources/tests match r26 byte for byte. Its 389-test isolated run
is retained as prior verification, not claimed as rerun here. Model/runtime
dependencies remain included under `formal/` and `tools/`.

The input audit checks 1,260 prepared/prompt contexts and declaration structure;
the fourteen-scenario table states endpoint limits, not semantic validation.
Regenerate with `code/scripts/audit_scenario_inputs.py --final-root <Final> --output <new.json>`.
Existing interval calculations are explicitly not cluster-adjusted.

Use the unified ZIP for complete immutable v8 raw evidence plus current code and
manuscript. Its top-level manifest and extended source crosswalk bind both layers.
Old manifests, reports and version-specific packaging scripts describe prior
versions; they are not the current package index. Caches are excluded.

Annotation, authorship and public release remain pending. Performance stays v8.
