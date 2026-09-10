# Human Acknowledgment Annotation Integration Design

## Objective

Create a new submission candidate under `latest/`, based on the sealed r28 tree at `r27-jss/current`, that incorporates Xuan Wentao's completed blinded manual annotation of the 325 textual acknowledgment outputs. Preserve the frozen benchmark records and the r28 rule labels, add a reproducible human-versus-rule analysis, revise the manuscript and supplement without overstating independence, compile both PDFs, verify their rendering, and publish the result on `main` through the existing SSH remote.

## Scientific interpretation

The manual labels were assigned by the second author, Xuan Wentao. The procedure is therefore author-involved blinded annotation: the annotator did not see the earlier labels, model configuration identifiers, run identifiers, or scenario identifiers while coding, but an author cannot be described as an independent third-party reviewer and was not blind to the general study hypothesis.

The deterministic v2.1 labels remain the frozen reported rule-hit measurements. The manual labels are an additional semantic audit and do not overwrite those measurements. Agreement is reported as human-rule agreement, not inter-rater reliability and not adjudicated truth.

Overall agreement may be reported descriptively, but scenario-level results are primary because A3 lacks a uniquely specified target field. A2, A3, A6, and B4 must remain separate; A2 and A3 must not be merged into a single validated context-mismatch endpoint.

## Data flow

1. Read the completed workbook and require exactly 325 unique case IDs, a binary label for every row, a rationale for every row, and an endpoint in `{context, stale}`.
2. Normalize only line endings and surrounding whitespace in `assistant_text` for matching. Do not alter the stored source text.
3. Join all 325 workbook rows exactly once to the frozen r21 semantic-audit rows by normalized assistant text.
4. Join those rows by `run_id` to the r28 v2.1 audit so each case receives scenario, model configuration, historical rule label, repaired rule label, and repair status.
5. Abort on missing, duplicate, or ambiguous matches, non-binary labels, endpoint mismatches, or unexpected denominators.
6. Emit normalized labels, confusion tables, disagreement rows, and machine-readable and narrative reports from one deterministic analysis script.

## Statistical outputs

The primary comparison is the completed manual label versus the repaired v2.1 rule label. The archive also retains the comparison with the historical rule label for provenance.

For the overall set, each endpoint, each scenario, and each model configuration, report denominators, positive counts, the 2 by 2 confusion matrix, percent agreement, Cohen's kappa, Gwet's AC1, and PABAK. Use 5,000 deterministic bootstrap replicates with base seed `20260910` for case-, model-, and model-by-scenario-cell resampling. Record undefined kappa replicates rather than silently coercing them.

The manuscript must identify the observed v2.1 comparison: 286/325 overall agreement, with 81/86 for A2, 56/88 for A3, 69/69 for A6, and 80/82 for B4. It must interpret the low A3 agreement as evidence of scenario/rubric ambiguity rather than model failure or annotator error.

## Release structure

Copy `r27-jss/current` to `latest/` without modifying the sealed source tree. Add a focused evidence directory at `latest/evidence/human-acknowledgment-annotation-2026-09-10/` containing:

- the completed source workbook under a stable ASCII filename;
- a SHA-256 record for the workbook and analysis inputs;
- the deterministic analysis script and its unit tests;
- normalized per-case labels;
- overall and stratified confusion/agreement tables;
- the unadjudicated disagreement list;
- bootstrap intervals and valid-replicate counts;
- JSON and Markdown analysis reports;
- a reproduction README.

Do not copy the teaching PDF or HTML reader unless required to reproduce the statistical join. The completed workbook, frozen source audit, repaired audit, script, and documented commands are sufficient.

## Manuscript changes

Update the evaluation protocol to describe the 325-row author-involved blind annotation, the information withheld during coding, the exact join, and the distinction between human-rule agreement and inter-human agreement.

Update the results with a concise headline and scenario-stratified findings. Preserve the earlier benign-completion human study as a separate experiment.

Update the discussion and threats to remove the obsolete claim that the textual indicators were not human-annotated, while retaining limitations from author involvement, absence of a second semantic coder, prevalence sensitivity, and A3 target ambiguity.

Update the supplement with the full method, confusion matrices, agreement coefficients, bootstrap sensitivity, disagreement retention, and evidence paths. Generate LaTeX tables from the analysis outputs where practical so counts are not copied manually.

Update declarations and CRediT text to state that Xuan Wentao conducted the blinded manual annotation and contributed Investigation, Validation, Data curation, Formal analysis, and Writing--review and editing. Do not imply third-party independence.

Update `latest/README.md`, author-action notes, revision declaration, and manifest so they identify this as the newest candidate and no longer say that the 325 outputs lack human annotation.

## Verification and publication

Run the analysis unit tests before implementing the analysis script and observe the required red-green cycle. Re-run the complete analysis after implementation and verify all expected denominators, joins, confusion totals, and headline values.

Compile `latest/paper/main.tex` and `latest/paper/supplement.tex` with the existing LaTeX toolchain. Treat unresolved references, missing citations, LaTeX errors, and overfull boxes caused by the new material as failures. Render every page of both final PDFs and inspect the full-page contact sheets plus pages containing changed material for clipping, overlap, broken glyphs, table overflow, and inconsistent pagination.

Run the relevant existing package verification gates that do not mutate the sealed r28 tree. Rebuild the manifest after all content is final, verify it against the new `latest/` tree, inspect `git diff`, commit the integrated candidate, push `main` to `origin` through SSH, and verify that the remote branch points to the pushed commit.
