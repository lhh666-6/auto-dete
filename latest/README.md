# Current manuscript — r29 review integration

R29 review report: [review and changes](docs/R29-REVIEW-INTEGRATION-zh.md). This revision integrates the coauthor's narrative recommendations; current checks are in [R29 verification](docs/R29-VERIFICATION.json).

Source handoff tag: `r28-jss-2026-09-10`. Current integrated candidate: main 62 pages; supplement 20 pages; 54 citations.
The submission PDFs are compiled from `paper/main.tex` and `paper/supplement.tex`; edit the LaTeX sources rather than the PDFs.

Second author Xuan Wentao (X.W.) completed a blinded author annotation of all 325 textual-acknowledgment outputs and recorded a rationale for every label. The resulting human--rule agreement analysis is integrated into the manuscript and supplement, while the 39 disagreements remain unadjudicated and the frozen rule-hit labels are unchanged. The separate benign-endpoint annotation still comprises X.W. and one non-author volunteer, with adjudication by the first author; its 11 terminal-completion versus strict-trajectory disagreements remain visible. No hosted-model call was rerun.

The new evidence archive is `evidence/human-acknowledgment-annotation-2026-09-10/`; it contains the completed workbook, frozen joined inputs, hashes, normalized labels, all disagreements, deterministic analysis code and tests, bootstrap summaries, and the exact reproduction command. The earlier r28 handoff checks remain documented in `evidence/r28-handoff-verification/verification.json`.

Historical post-r28 checks (before the September 11 refinement): 325/325 annotation rows matched once; 7 integration/manifest tests passed; the full Python implementation suite passed 389/389; 19 formal witness tests passed; the archived batch package structure gate passed; both LaTeX PDFs compiled with no errors, undefined references/citations, multiply defined labels, or overfull boxes. See `evidence/human-acknowledgment-annotation-2026-09-10/FINAL-VERIFICATION.md`.

The September 11 refinement, fresh checks, reproduction commands, and remaining author decisions are documented in `REVISION-NOTES-2026-09-11.md`. This is a revised submission candidate, not a declaration of submission readiness.

The original 1,260 model-run records remain frozen. Performance describes the v8 snapshot. Old dated reports are historical, not the current verification summary. The current manifest retains the filename `MANIFEST-r27.json` for compatibility and identifies this post-r28 integration in its revision field.

## Short keyless reproduction path

With the documented Python dependencies installed, no credentials, hosted-model access, or network are needed for these checks. Every command below writes to a fresh path and leaves the frozen
evidence untouched.

1. **Fetch the pinned version.** Clone the repository and check out the commit or
   tag the paper cites.
2. **Verify the package.** From this directory: `python verify_latest.py` —
   re-hashes every shipped file and confirms the recorded page counts; it reports
   zero missing, extra, or mismatched entries.
3. **Exercise the admission relation.** From `code/implementation-fixed/`:
   - `python -B -m pytest tests/integration/test_value_equality_admission.py -q -p no:cacheprovider`
     covers an equal-value unchanged submission copying its source forward and a
     pure canonical no-op being rejected fail-closed;
   - `python conformance/run_catalogue.py --output <fresh-dir>` runs the declared
     fault catalogue against the reference realization, and
     `python conformance/verify_catalogue_results.py <fresh-dir>` checks the result;
   - `python conformance/verify_formal_refinement_records.py` checks the deposited
     29-case formal--concrete refinement freeze (nine SAT projections, twenty
     UNSAT mapping mutants). To rebuild that freeze from source instead, run
     `python conformance/generate_formal_refinement_records.py --output <fresh-dir>`
     and point `conformance/ACTIVE_REFINEMENT_FREEZE.txt` at it.
4. **Reproduce the annotation analysis.** From
   `evidence/human-annotation-2026-09-10/`: `python -B recompute_irr.py
   --labels labels-A1-A2-normalized.csv --out <fresh.json> --replicates 5000
   --seed 20260910`, about six seconds, reproducing `recomputed-irr.json`.
5. **Compile the paper.** From `paper/`: `latexmk -pdf main.tex` and
   `latexmk -pdf supplement.tex`. The repository `.latexmkrc` keeps
   intermediates in `out/` and copies the final PDFs beside the sources; delete
   `out/` afterwards, since it is excluded from the manifest but is not part of
   the package.

Runtime verification in this package was performed on CPython 3.11.9; the
implementation, the catalogue, and the analysis scripts all run in that
environment.

Use new output paths outside this sealed tree for reruns. Formal gate, from this directory: `./formal/alloy/batch/verify_batch_package.ps1 -RequireRawResults`. To re-execute the Alloy batch rather than verify it, use `./formal/alloy/batch/run_batch_alloy.ps1 -FreezeId <new-id> -OutputRoot <dir-outside-this-tree>`, which runs the 72 commands on the bundled `tools/jre21` runtime and leaves the sealed tree untouched; omitting `-OutputRoot` writes a new freeze inside the tree. Witness tests, from code/formal-fixed/: `python -B -m unittest discover -s tests -v`. Full package verification against the manifest, from this directory: `python verify_latest.py`.