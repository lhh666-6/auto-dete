# JSS R18 Implementation Plan

**Design:** `docs/superpowers/specs/2026-08-26-jss-r18-experiment-format-design.md`
**Baseline:** `release-staging/2026-08-26-option-a-r17-rc4-g10-final/`
**Working directory:** `revisions/2026-08-26-jss-r18/`
**Target:** Journal of Systems and Software regular research article
**Personal metadata:** deferred; preserve `AUTHOR_INPUT_NEEDED`

`writing-plans` is not installed in this environment. This document is the detailed execution
fallback required by the approved brainstorming design.

## Task 1 — Establish an isolated, hash-bound R18 baseline

**Files/directories**

- Create `revisions/2026-08-26-jss-r18/`.
- Copy the required paper and source trees from the sealed R17/G10 directory.
- Create `baseline-copy-manifest.json` and `BASELINE.md` in the R18 workspace.

**Procedure**

1. Verify the sealed package's existing release/source/evidence manifests before copying.
2. Resolve the exact R17 paper, source, paper-input, and build-tool paths.
3. Copy only the declared R18 inputs; never copy from the stale top-level `jss/` tree.
4. Record original path, copied path, byte count, and SHA-256 for every copied file.
5. Verify all copied hashes and snapshot R17/G10 directory metadata to prove it was not changed.

**Gate**

- Baseline manifests pass.
- Copied hashes match.
- Git/status check confirms no R17/G10 file was modified.

## Task 2 — Define and freeze the AI-origin fixture

**Files**

- `fixtures/ai-origin/input.txt`
- `fixtures/ai-origin/prompt.txt`
- `fixtures/ai-origin/raw-response.txt`
- `fixtures/ai-origin/candidate.json`
- `fixtures/ai-origin/generation-metadata.json`
- `fixtures/ai-origin/manifest.json`

**Procedure**

1. Write a three-field synthetic administrative record with no personal or licensed data.
2. Record the exact schema-conversion prompt.
3. Produce one hosted-Codex response and freeze the first schema-valid output.
4. Preserve the raw response separately from normalized JSON.
5. Record only exposed service/model/runtime fields; set unavailable fields to
   `not_exposed_by_host`.
6. Hash the complete fixture bundle.

**Gate**

- Candidate satisfies the repository schema.
- Raw and normalized artifacts are distinct and hash-linked.
- No claim of model accuracy or exact-response regeneration appears in metadata or paper notes.

## Task 3 — Add lifecycle evidence through TDD

**Initial test ownership**

- Add an R18 test module beside the copied experiment code.
- Do not change production behavior unless a failing test demonstrates that the existing public
  interface cannot execute a designed case.

**Red-green sequence**

1. RED: fixture loader rejects missing/unhashed fixture files.
2. GREEN: minimal fixture loader and manifest verifier.
3. RED: A1 all-Accept expected transition/lineage test.
4. GREEN: minimal R18 scenario adapter using existing production services.
5. Repeat red-green for A2 one-Correction, A3 all-Correction, A4 mixed/copy-forward, A5 stale
   replay, and A6 invalid-item whole-batch rejection.
6. RED: rejected-case digest changes are detected.
7. GREEN: canonical before/after database digest recording.
8. Refactor only after every focused test passes; run cumulative tests after each refactor.

**Evidence contract per case**

- input/fixture ID;
- candidate, certificate, authorization, transition, version, and source identifiers;
- persisted values and source-map snapshot;
- forward and reverse trace results;
- pre/post canonical database digest;
- expected and observed outcome;
- command exit status and exception details.

**Gate**

- Every new behavior was observed failing before implementation.
- A1–A4 each commit exactly one expected version.
- A5–A6 reject with identical pre/post canonical database digests.
- Existing relevant regression tests remain green.

## Task 4 — Freeze R18 evidence and normalized paper inputs

**Files**

- `evidence/raw/ai-origin-lifecycle/<run-id>/`
- `evidence/paper-inputs/ai_origin_lifecycle_summary.json`
- `evidence/claim-evidence-ledger.json`
- `evidence/manifest.json`
- `evidence/receipt.json`

**Procedure**

1. Execute the lifecycle suite once from a clean declared environment into a non-overwriting run
   directory.
2. Preserve stdout, stderr, case JSON, database snapshots/digests, environment, command, and
   receipt.
3. Normalize only after the raw run succeeds.
4. Verify source/config/lock/fixture hashes and zero command failures.
5. Retain any failed run unchanged and use a new run directory for a corrected attempt.

**Gate**

- Six unique cases, six expected outcomes, zero command failures.
- Raw-to-normalized lineage and all manifests pass.
- Retained R17 numbers still point to R17 frozen inputs; new R18 statements point only to R18
  inputs.

## Task 5 — Execute `literature`

**Scope**

- Targeted update, not a second broad review.
- Primary targets: authoritative provenance model, foundational database provenance, ToolGate,
  CapChain, and any source needed for deletion/tombstone or portability wording.

**Procedure**

1. Check existing project bibliography, Paperpile availability, scholarly source availability,
   and recent scout reports.
2. Search primary/authoritative sources for the specific missing claims.
3. Verify existence, title/author/year, and every DOI programmatically before insertion.
4. Prefer published versions and reuse existing keys.
5. Update `docs/literature-review/literature_summary.md` and its self-contained bibliography.
6. Validate the R18 bibliography and record Paperpile membership as verified or unavailable—not
   inferred.

**Gate**

- No unverified DOI or unsupported attribution.
- Literature summary remains outside the paper directory.
- Every new paper paragraph sentence has a verified source mapping.

## Task 6 — Execute `paper-skill`

**Expected paper edits**

- `sections/01-introduction.tex`: concise AI-candidate/Correction example and narrowed gap.
- `sections/02-related-work.tex`: seven-dimension ToolGate/CapChain matrix and foundational
  provenance grounding.
- `sections/05-transactional-realization.tex`: explicit generator-outside-boundary statement.
- `sections/07-evaluation-protocol.tex`: AI-origin fixture and six-case protocol.
- `sections/08-results.tex`: bounded six-case observations only.
- `sections/09-discussion-threats.tex`: hosted-model metadata, deletion/tombstones, manual
  fallback, database portability, and no accuracy/user/production claims.
- `artifact_appendix.tex`: corrected tamper-probe wording and R18 fixture/evidence lineage.
- `declarations.tex`: accurate AI-assistance wording; personal fields untouched.
- Generated evidence table(s), claim-evidence ledger, citation ledger, highlights, abstract,
  cover letter, and README as needed for consistency.

**Gate**

- Every numeric/pass-fail claim maps to a JSON path.
- Abstract ≤250 words; highlights 3–5 items and ≤85 characters each.
- No stale R17 timing value or unsupported R18 generalization.
- Seven-dimension quality score reaches at least 28/35 before submission-stage work.

## Task 7 — Execute `latex-template`

**Mode**

- Report first.
- Do not force generic `article`/biblatex conventions onto the JSS `elsarticle`/natbib source.
- Apply only safe venue-compatible items and only after the protocol's apply confirmation rule.

**Gate**

- A dated compliance report distinguishes legitimate journal divergence from true preamble
  defects.
- Any applied change is followed by compilation.

## Task 8 — Execute `academic-figure-skill`

**Figure contract**

- Figure 1: communicate the untrusted candidate → bound authorization → atomic authoritative
  transition boundary.
- Figure 2: communicate evidence layers and their limits.
- Figure 3: communicate the complete fixed performance grid without hiding negative deltas.

**Procedure**

1. Load the required figure-contract, palette, typography, journal, export, and QA references.
2. Audit existing SVG/PDF masters at final print size and in grayscale.
3. Update Figure 1 only if the new generator-outside-boundary clarification is absent.
4. Preserve editable text and vector paths; do not submit the AI ideation raster.
5. Export vector PDF masters and 300-dpi previews; update figure provenance and QA reports.

**Gate**

- No clipping, overlap, raster payload, color-only encoding, or unreadable text.
- Figure numbers/captions and prose agree with the final paper.

## Task 9 — Execute `pre-submission-report` and resolve findings

**Procedure**

1. Run integrity checks for placeholders, citations, sections, references, and the JSS
   single-anonymized policy.
2. Compile, verify DOIs/citations, and run adversarial scientific/technical checks.
3. Consolidate findings into P0/P1/P2.
4. Fix every scientific or technical P0/P1 issue in scope and rerun affected gates.
5. Record deferred author identity/funding/CRediT/DOI fields as an author-input gate, not a hidden
   technical pass.

**Gate**

- No unresolved Critical/Major scientific or technical issue.
- Report clearly distinguishes technical readiness from author-controlled submission readiness.

## Task 10 — Final LaTeX, clean-copy, and release verification

**Procedure**

1. Compile with the available equivalent clean pdflatex/BibTeX chain if local `latexmk` still
   lacks Perl.
2. Inspect the full log: errors, warnings, overfull/underfull boxes, undefined citations/refs, and
   source pathologies.
3. Render and visually inspect every changed page plus all figures/tables at original resolution.
4. Run citation cross-reference and full bibliography validation after new citations.
5. Build a non-overwriting R18 release candidate and manifests.
6. Verify from a clean copied/extracted tree; run an independent one-byte tamper probe on a copy.
7. Re-read this plan and verify every completion criterion with fresh command output.

**Gate**

- Clean build and manifest verification pass.
- Tamper probe reports only the deliberately changed copied file.
- R17/G10 remains unchanged.
- Final handoff identifies any remaining author-only input without claiming the submission is
  administratively complete.
