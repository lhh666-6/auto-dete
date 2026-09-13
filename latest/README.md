# Frozen manuscript — r31 JSS submission version

Final checks: [September 13 submission report](docs/FINAL-TONE-2026-09-13.md). For complete raw-record reproduction use the repository-root [reviewer guide](../REVIEWER_GUIDE.md), including `r21-jss/` and Git LFS.

R30: authors are Liang Hanghao, Xuan Wentao, and Peng Peng (sole corresponding author). [Contribution record](docs/AUTHORSHIP-AND-CREDIT-r30-zh.md), [closeout report](docs/R30-CLOSEOUT-zh.md), and [AI-assisted disagreement review](evidence/acknowledgment-ai-review-2026-09-12/README.md). Original annotation labels and reported statistics are unchanged. Fixed submission archive: https://github.com/lhh666-6/auto-dete/tree/r31-jss-2026-09-13/latest.

R29 review report: [review and changes](docs/R29-REVIEW-INTEGRATION-zh.md). This revision integrates the coauthor's narrative recommendations; historical checks are in [R29 verification](docs/R29-VERIFICATION.json).

Source handoff tag: `r28-jss-2026-09-10`. Current frozen version: main 60 pages; supplement 20 pages; 54 citations.
The submission PDFs are compiled from `paper/main.tex` and `paper/supplement.tex`; edit the LaTeX sources rather than the PDFs.

Second author Xuan Wentao (X.W.) completed a blinded author annotation of all 325 textual-acknowledgment outputs and recorded a rationale for every label. The resulting human--rule agreement analysis is integrated into the manuscript and supplement, while the 39 disagreements remain without human adjudication and the frozen rule-hit labels are unchanged. The separate benign-endpoint annotation still comprises X.W. and one non-author volunteer, with adjudication by the first author; its 11 terminal-completion versus strict-trajectory disagreements remain visible. No hosted-model call was rerun.

The new evidence archive is `evidence/human-acknowledgment-annotation-2026-09-10/`; it contains the completed workbook, frozen joined inputs, hashes, normalized labels, all disagreements, deterministic analysis code and tests, bootstrap summaries, and the exact reproduction command. The earlier r28 handoff checks remain documented in `evidence/r28-handoff-verification/verification.json`.

Historical post-r28 checks (before the September 11 refinement): 325/325 annotation rows matched once; 7 integration/manifest tests passed; the full Python implementation suite passed 389/389; 19 formal witness tests passed; the archived batch package structure gate passed; both LaTeX PDFs compiled with no errors, undefined references/citations, multiply defined labels, or overfull boxes. See `evidence/human-acknowledgment-annotation-2026-09-10/FINAL-VERIFICATION.md`.

The September 11 refinement, fresh checks, reproduction commands, and remaining author decisions are documented in `REVISION-NOTES-2026-09-11.md`. Those dated notes describe earlier stages; the final prepared version is identified by the September 13 freeze report.

The original 1,260 model-run records remain frozen. Performance describes the v8 snapshot. Old dated reports are historical, not the current verification summary. The current manifest retains the filename `MANIFEST-r27.json` for compatibility and identifies this post-r28 integration in its revision field.

## Short keyless reproduction path

With the documented Python dependencies installed, no credentials, hosted-model access, or network are needed for these checks. Use a disposable working copy for code execution and compilation, and place derived experimental output outside the sealed tree. Compilation replaces local PDF files; it does not reproduce their bytes deterministically.

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
     UNSAT mapping mutants). In a separate working copy, rebuild that freeze from source with
     `python conformance/generate_formal_refinement_records.py --output <fresh-dir>`
     and verify the generated manifest and receipts there. Do not edit the active-freeze pointer in this sealed package.
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