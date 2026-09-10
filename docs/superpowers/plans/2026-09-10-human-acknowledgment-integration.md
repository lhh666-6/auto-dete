# Human Acknowledgment Annotation Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce and publish a reproducible `latest/` JSS submission candidate that integrates Xuan Wentao's 325-row blinded manual acknowledgment annotation into the r28 paper and supplement.

**Architecture:** Copy the sealed r28 tree into a new mutable release directory, add one self-contained evidence module that joins the completed workbook to frozen audits and calculates agreement, then drive manuscript tables and claims from those outputs. Preserve historical rule measurements, distinguish author-involved human-rule agreement from inter-human reliability, and verify both numerical and rendered PDF outputs before publication.

**Tech Stack:** Python 3.12, `openpyxl`, standard-library `csv/json/hashlib/unittest`, NumPy, LaTeX/latexmk, Poppler, Git over SSH.

**Spec:** `docs/superpowers/specs/2026-09-10-human-acknowledgment-integration-design.md`

## Global Constraints

- `r27-jss/current` is a sealed r28 source and must remain byte-for-byte unchanged.
- The manual annotator is second author Xuan Wentao; never call the procedure independent third-party annotation.
- Preserve the deterministic v2.1 labels and treat the manual labels as a separate human-rule semantic audit.
- Match exactly 325 unique workbook rows to exactly 325 frozen audit rows; fail closed on any ambiguity.
- Keep A2, A3, A6, and B4 separate, and interpret A3 as exploratory because its target field was not uniquely specified.
- Use 5,000 bootstrap replicates with base seed `20260910`.
- Final outputs are `latest/paper/main.pdf` and `latest/paper/supplement.pdf`.
- Push the completed integration to `origin/main` using the configured SSH remote.

---

### Task 1: Create the mutable release candidate

**Files:**
- Create: `latest/` as a mechanical copy of `r27-jss/current/`
- Create: `latest/evidence/human-acknowledgment-annotation-2026-09-10/completed-blind-annotation.xlsx`
- Create: `latest/evidence/human-acknowledgment-annotation-2026-09-10/frozen-semantic-audit-with-text.csv`

**Interfaces:**
- Consumes: sealed r28 tree and the completed external workbook.
- Produces: isolated release tree and stable evidence input paths used by every later task.

- [ ] **Step 1: Verify sources and destination**

Run: `Test-Path r27-jss/current; Test-Path latest; git status --short`

Expected: source is `True`, destination is `False`, and the only pending file is this plan before it is committed.

- [ ] **Step 2: Copy the sealed candidate and workbook**

Run a literal-path recursive `Copy-Item` from `r27-jss/current` to `latest`, create the evidence directory, copy the workbook under the stable ASCII filename, and copy the frozen r21 semantic audit with assistant text into the evidence module. The latter is required because the sealed r28 candidate carries only the paper snapshot under `baseline-v8/`, not this analysis input.

- [ ] **Step 3: Verify the source tree was not changed**

Run: `git diff --no-index -- r27-jss/current latest`

Expected at this stage: only the newly added evidence directory differs.

### Task 2: Build the agreement analysis with TDD

**Files:**
- Create: `latest/evidence/human-acknowledgment-annotation-2026-09-10/test_analyze_acknowledgment_annotation.py`
- Create: `latest/evidence/human-acknowledgment-annotation-2026-09-10/analyze_acknowledgment_annotation.py`

**Interfaces:**
- Consumes: `completed-blind-annotation.xlsx`, the frozen r21 semantic audit, and `latest/evidence/r3-audit-verified/recognition_semantic_audit_v2.csv`.
- Produces: `normalize_text(str) -> str`, `agreement_metrics(list[dict], label_field: str) -> dict`, `bootstrap_intervals(list[dict], unit: str, replicates: int, seed: int) -> dict`, and `run_analysis(paths, output_dir) -> dict`.

- [ ] **Step 1: Write failing validation and metric tests**

Tests must assert exact 325-row matching, failure on duplicate text, the four confusion cells, agreement, kappa, AC1, PABAK, deterministic bootstrap output, and the known v2.1 headline values: 286/325 overall, A2 81/86, A3 56/88, A6 69/69, and B4 80/82.

- [ ] **Step 2: Run the tests and verify RED**

Run: `python -B -m unittest -v test_analyze_acknowledgment_annotation.py`

Expected: import failure because `analyze_acknowledgment_annotation.py` does not exist.

- [ ] **Step 3: Implement the minimum deterministic analysis**

The script must validate inputs, perform the two joins, compute the specified coefficients, resample cases/models/cells with NumPy's seeded generator, write all CSV/JSON/Markdown outputs, and return a summary dictionary. It must not edit the input workbook.

- [ ] **Step 4: Run tests and verify GREEN**

Run: `python -B -m unittest -v test_analyze_acknowledgment_annotation.py`

Expected: all tests pass with no warnings or errors.

### Task 3: Freeze reproducible analysis outputs

**Files:**
- Create: `latest/evidence/human-acknowledgment-annotation-2026-09-10/normalized-labels.csv`
- Create: `latest/evidence/human-acknowledgment-annotation-2026-09-10/agreement-summary.csv`
- Create: `latest/evidence/human-acknowledgment-annotation-2026-09-10/disagreements-v2.csv`
- Create: `latest/evidence/human-acknowledgment-annotation-2026-09-10/bootstrap-intervals.csv`
- Create: `latest/evidence/human-acknowledgment-annotation-2026-09-10/analysis-report.json`
- Create: `latest/evidence/human-acknowledgment-annotation-2026-09-10/analysis-report.md`
- Create: `latest/evidence/human-acknowledgment-annotation-2026-09-10/input-hashes.sha256`
- Create: `latest/evidence/human-acknowledgment-annotation-2026-09-10/README-REPRODUCE.md`
- Create: `latest/paper/tables/generated/acknowledgment_human_rule.tex`

**Interfaces:**
- Consumes: `run_analysis` from Task 2.
- Produces: stable manuscript inputs and an auditable analysis archive.

- [ ] **Step 1: Run the full 5,000-replicate analysis**

Run the script from its evidence directory with explicit workbook, source-audit, repaired-audit, output, and LaTeX-table arguments.

- [ ] **Step 2: Independently reconcile outputs**

Use a separate one-shot Python calculation to require 325 unique IDs, 39 disagreements, confusion totals of 325, human positives of 241, v2.1 positives of 272, and overall agreement of 286.

- [ ] **Step 3: Hash all immutable inputs**

Record SHA-256 hashes for the workbook, r21 semantic audit, and repaired v2.1 audit using repository-relative paths.

### Task 4: Integrate the experiment into the manuscript

**Files:**
- Modify: `latest/paper/sections/07-evaluation-protocol.tex`
- Modify: `latest/paper/sections/08-results.tex`
- Modify: `latest/paper/sections/09-discussion-threats.tex`
- Modify: `latest/paper/sections/declarations.tex`
- Modify: `latest/paper/supplement.tex`
- Modify: `latest/paper/AUTHOR_INPUT_NEEDED.md`

**Interfaces:**
- Consumes: generated table and analysis report from Task 3.
- Produces: scientifically qualified main-text, supplement, limitations, and author contribution statements.

- [ ] **Step 1: Update methods and blinding language**

Describe X.W. as the author annotator, list withheld metadata, state the exact text join, and distinguish human-rule agreement from inter-human reliability.

- [ ] **Step 2: Update results from generated evidence**

Report the overall descriptive value and the four scenario agreements, with A3 explicitly interpreted as construct ambiguity. Include the generated supplement table.

- [ ] **Step 3: Update threats and declarations**

Replace obsolete claims that the textual indicators lack human annotation; state the single-author-coder and no-adjudication limitations; credit Xuan Wentao for conducting the blinded experiment.

- [ ] **Step 4: Scan for contradictions**

Run `rg` for `not human-annotated`, `no independent human`, `325 acknowledgment`, and `Xuan Wentao`, then inspect every hit and remove stale assertions without changing statements about the separate benign-completion study.

### Task 5: Update release metadata and manifest

**Files:**
- Modify: `latest/README.md`
- Modify: `latest/修改申明-REVISION-DECLARATION-zh.md`
- Modify: `latest/MANIFEST-r27.json`
- Create: `latest/evidence/human-acknowledgment-annotation-2026-09-10/CHANGELOG.md`

**Interfaces:**
- Consumes: final analysis and manuscript tree.
- Produces: a self-describing newest release with integrity metadata.

- [ ] **Step 1: Update release-facing prose**

Identify `latest/` as the post-r28 integrated candidate, list the new annotation evidence, and retain the historical r28 tag as the source baseline.

- [ ] **Step 2: Rebuild the manifest**

Use the repository's existing manifest builder or schema. Exclude ephemeral LaTeX and render files, record the new revision identity, and hash every packaged file expected by the schema.

- [ ] **Step 3: Verify the manifest**

Run the existing package manifest verifier and require zero missing, extra, or hash-mismatched entries.

### Task 6: Compile and visually verify both final PDFs

**Files:**
- Modify/create: `latest/paper/main.pdf`
- Modify/create: `latest/paper/supplement.pdf`
- Create temporarily: `latest/tmp/pdfs/` render output; remove it after inspection.

**Interfaces:**
- Consumes: all LaTeX sources and generated tables.
- Produces: the two final submission PDFs.

- [ ] **Step 1: Mark the PDF edit operation once**

Run the PDF artifact marker with operation `edit`, expected output count `2`, and output format `pdf` immediately before the first compilation command.

- [ ] **Step 2: Compile main and supplement**

Run `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` and the equivalent command for `supplement.tex` from `latest/paper`.

- [ ] **Step 3: Enforce log quality gates**

Require successful exit codes and scan logs for undefined references/citations, missing files, fatal errors, and newly introduced overfull boxes.

- [ ] **Step 4: Render and inspect every page**

Use Poppler to render both PDFs. Build contact sheets, inspect all pages, then inspect changed-method/results/supplement/declarations pages at full resolution. Fix and repeat compilation/rendering until no clipping, overlap, broken glyphs, or table overflow remains.

- [ ] **Step 5: Verify PDF structure**

Use `pdfinfo` and `pypdf` to confirm page counts, extractability, expected section text, and absence of blank pages.

### Task 7: Final verification, commit, and SSH push

**Files:**
- Verify: all tracked changes under `latest/` and the plan/spec documents.

**Interfaces:**
- Consumes: completed candidate and fresh verification evidence.
- Produces: published `origin/main` commit.

- [ ] **Step 1: Run focused and package checks**

Run analysis unit tests, the full analysis reconciliation, LaTeX builds, manifest verification, and relevant existing r28 witness/agreement gates. Record actual exit codes and counts.

- [ ] **Step 2: Inspect repository changes**

Run `git status --short`, `git diff --stat`, `git diff --check`, and targeted diffs for every manuscript and metadata file. Confirm `r27-jss/current` has no modifications.

- [ ] **Step 3: Commit the integrated release**

Stage the plan and `latest/`, re-run cached-diff checks, and commit with message `paper: integrate blinded acknowledgment annotation`.

- [ ] **Step 4: Push and verify the remote**

Run `git push origin main`, fetch the remote, and require `git rev-parse HEAD` to equal `git rev-parse origin/main`.
