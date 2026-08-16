# Auto-Decte ESWA Manuscript Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce an independently compilable, double-anonymized ESWA manuscript and submission package grounded only in verified experiment artifacts, then score its quality and estimate publication prospects.

**Architecture:** Create a new `eswa/` LaTeX project beside the preserved `lncs/` project. Split the journal paper into focused section files, import all quantitative content from manifest-verified experiment outputs, replace generated engineering images with author-controlled vector diagrams, and keep identity-bearing submission files separate from the anonymous manuscript.

**Tech Stack:** Elsevier `elsarticle`, BibTeX, TikZ/PGF, booktabs, siunitx, xcolor, pdflatex/latexmk, Python-generated PDF/SVG plots and LaTeX tables, DOI/Crossref/publisher verification, PDF visual QA.

---

## File Structure

- `eswa/main_anonymous.tex`: anonymous ESWA manuscript entry point.
- `eswa/title_page.tex`: separate title page; uses anonymous drafting metadata until definitive author data is supplied.
- `eswa/sections/01_introduction.tex`: problem, gap, question, and contribution hierarchy.
- `eswa/sections/02_related_work.tex`: document intelligence, HITL, selective prediction, provenance, and trustworthy AI.
- `eswa/sections/03_formal_model.tex`: planes, transitions, invariant, propositions, and scope.
- `eswa/sections/04_methodology.tex`: perception, abstention, candidate isolation, retrieval, LLM, offline flow.
- `eswa/sections/05_experimental_protocol.tex`: synthetic generation, baselines, metrics, fault matrix, and statistics.
- `eswa/sections/06_results.tex`: artifact-grounded recognition, trust, resilience, ablation, and latency results.
- `eswa/sections/07_industrial_context.tex`: deployment context and data-governance constraints.
- `eswa/sections/08_discussion.tex`: interpretation, implications, and relation to prior work.
- `eswa/sections/09_limitations.tex`: external validity, construct validity, and unmeasured human outcomes.
- `eswa/sections/10_conclusion.tex`: supported takeaways only.
- `eswa/sections/declarations.tex`: data availability, funding, competing interests, and AI-use declaration.
- `eswa/references.bib`: verified bibliography.
- `eswa/styles/trust-teal.tex`: color and TikZ style definitions.
- `eswa/figures/vector/`: author-controlled TikZ sources and rendered vector diagrams.
- `eswa/figures/generated/`: plots copied from the experiment manifest.
- `eswa/tables/generated/`: LaTeX tables copied from the experiment manifest.
- `eswa/artifacts/`: experiment manifest and result evidence.
- `eswa/highlights.txt`: three to five ESWA highlights.
- `eswa/cover_letter.md`: journal-specific cover letter.
- `eswa/figure_captions.txt`: separate captions for submission.
- `eswa/submission_checklist.md`: official requirement trace.
- `eswa/supplementary.tex`: extended experiment and reproducibility material.
- `eswa/reviews/eswa-readiness-assessment.md`: final 35-point score, rejection risks, and publication estimate.
- `eswa/reviews/code-paper-alignment.md`: claim-by-claim implementation support matrix.

### Task 1: Scaffold the independent Elsevier project

**Files:**
- Create: `eswa/main_anonymous.tex`
- Create: `eswa/title_page.tex`
- Create: `eswa/styles/trust-teal.tex`
- Create: `eswa/sections/*.tex`
- Create: `eswa/.latexmkrc`
- Create: `eswa/references.bib`

- [ ] **Step 1: Verify the local Elsevier class**

Run `kpsewhich elsarticle.cls`.

Expected: an absolute path to `elsarticle.cls`. If absent, install the official MiKTeX `elsarticle` package before writing a substitute class.

- [ ] **Step 2: Create a minimal anonymous manuscript**

Create `eswa/main_anonymous.tex`:

```tex
\documentclass[preprint,12pt,authoryear]{elsarticle}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{siunitx}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{tikz}
\usepackage{hyperref}
\usepackage{lineno}
\input{styles/trust-teal}

\journal{Expert Systems with Applications}

\begin{document}
\begin{frontmatter}
\title{Auto-Decte: Trust-Constrained Document Intelligence through Candidate--Fact Separation and Selective Abstention}
\author{Anonymous authors}
\begin{abstract}
This anonymous drafting abstract will be replaced only after the verified experiment artifacts are available.
\end{abstract}
\begin{keyword}
document intelligence \sep human-in-the-loop \sep selective prediction \sep data provenance \sep trustworthy AI
\end{keyword}
\end{frontmatter}
\linenumbers
\input{sections/01_introduction}
\input{sections/02_related_work}
\input{sections/03_formal_model}
\input{sections/04_methodology}
\input{sections/05_experimental_protocol}
\input{sections/06_results}
\input{sections/07_industrial_context}
\input{sections/08_discussion}
\input{sections/09_limitations}
\input{sections/10_conclusion}
\input{sections/declarations}
\bibliographystyle{elsarticle-harv}
\bibliography{references}
\end{document}
```

The drafting sentence is not allowed in the final manuscript; Task 7 replaces the entire abstract after results exist.

- [ ] **Step 3: Define the selected Trust Teal visual grammar**

Create `eswa/styles/trust-teal.tex`:

```tex
\definecolor{TrustTeal}{HTML}{16796F}
\definecolor{TrustCharcoal}{HTML}{243746}
\definecolor{TrustAmber}{HTML}{C06B19}
\definecolor{TrustPaleTeal}{HTML}{E1F2EF}
\definecolor{TrustPaleAmber}{HTML}{FFF0DC}
\tikzset{
  evidence/.style={draw=TrustTeal,fill=TrustPaleTeal,rounded corners,thick,align=center},
  candidate/.style={draw=TrustTeal,fill=TrustPaleTeal,rounded corners,thick,align=center},
  decision/.style={draw=TrustAmber,fill=TrustPaleAmber,rounded corners,thick,align=center},
  fact/.style={draw=TrustCharcoal,fill=white,rounded corners,very thick,align=center},
  permitted/.style={->,>=stealth,thick,draw=TrustTeal},
  authoritative/.style={->,>=stealth,very thick,draw=TrustAmber},
  prohibited/.style={dashed,thick,draw=TrustCharcoal}
}
```

- [ ] **Step 4: Add compile-safe section stubs**

Each section file must contain its final numbered `\section{}` heading and one scope sentence, not an empty file. For example, `03_formal_model.tex` begins:

```tex
\section{Problem Definition and Formal Trust Model}
\label{sec:formal-model}
This section defines the authoritative-data threat model, permitted transitions, and the scope of the machine-to-fact isolation invariant.
```

- [ ] **Step 5: Add the build configuration**

Create `eswa/.latexmkrc`:

```perl
$pdf_mode = 1;
$interaction = 'nonstopmode';
$out_dir = 'out';
```

Create an empty `eswa/references.bib` ending with a newline so the scaffold has every declared input file.

- [ ] **Step 6: Compile twice and commit**

Run two `pdflatex` passes into `eswa/out`. Expected: a readable PDF with no missing input files.

```powershell
git add eswa
git commit -m "paper: scaffold anonymous ESWA manuscript"
```

### Task 2: Build and verify the journal bibliography

**Files:**
- Create: `eswa/references.bib`
- Create: `eswa/reviews/citation-ledger.md`
- Modify: `eswa/sections/01_introduction.tex`
- Modify: `eswa/sections/02_related_work.tex`
- Create: `eswa/reviews/code-paper-alignment.md`

- [ ] **Step 1: Convert the 13 verified LNCS references to BibTeX**

Use DOI-bearing publisher metadata wherever available. Preserve the corrected RAG identifier, MILP author list, and formal LayoutLMv3/Donut publication records. The citation ledger must record citation key, DOI or stable URL, verified title, publication venue, and the exact manuscript claim supported.

- [ ] **Step 2: Discover recent directly relevant literature**

Search 2022--2026 primary publisher pages and papers for: trustworthy document intelligence, human oversight in information extraction, selective classification and calibration, data provenance and immutable evidence, LLM-assisted information extraction, and industrial document processing. Include recent ESWA papers only when they directly support positioning; do not add citations merely to imitate the journal.

- [ ] **Step 3: Verify every new entry**

For each candidate reference, confirm title, authors, year, venue, volume/article number, and DOI against Crossref or the publisher page. Exclude unverifiable entries. Target a focused bibliography of approximately 35--50 references rather than an inflated list.

- [ ] **Step 4: Write the introduction and related-work evidence map**

The introduction must follow this sequence: consequential workflow problem; limits of accuracy-only automation; specific gap in authoritative-data control; research question; solution and boundaries; contribution hierarchy. Related work must compare capabilities and gaps neutrally and end by locating candidate--fact separation relative to selective prediction and provenance.

- [ ] **Step 5: Establish the code--paper alignment gate**

Create `code-paper-alignment.md` with one row per architecture, implementation, test-count, framework, recognition, offline, and deployment claim. Record the supporting code path or experiment artifact and a `SUPPORTED`, `PARTIAL`, or `REMOVE` verdict. The public baseline currently requires explicit resolution of FastAPI, React, PWA, ArUco detection, and “478 tests”; none may appear in ESWA unless the experiment branch implements and verifies it.

- [ ] **Step 6: Audit and commit**

Run a citation-key audit to ensure every `\cite` key exists and every bibliography entry is used. Expected: zero missing and zero unused entries.

```powershell
git add eswa/references.bib eswa/reviews/citation-ledger.md eswa/reviews/code-paper-alignment.md eswa/sections/01_introduction.tex eswa/sections/02_related_work.tex
git commit -m "paper: position Auto-Decte in verified ESWA literature"
```

### Task 3: Formalize the trust model without overclaiming

**Files:**
- Modify: `eswa/sections/03_formal_model.tex`
- Create: `eswa/figures/vector/trust-model.tex`
- Create: `eswa/figures/vector/state-transitions.tex`

- [ ] **Step 1: Define entities and transition relations**

Introduce evidence `E`, candidates `C`, human decisions `H`, facts `F`, and machine modules `M`. Define permitted relations `M -> C`, `E -> C`, `C -> H`, and `(F_t,H_t) -> F_{t+1}`. State the scoped invariant:

```tex
\begin{equation}
\forall m\in M,\qquad m\not\rightarrow F,
\label{eq:machine-fact-invariant}
\end{equation}
```

Immediately qualify that this is an application-architecture invariant over exposed service paths, not protection against a database administrator or compromised operating system.

- [ ] **Step 2: State testable propositions**

Add propositions for incorrect machine candidates, stale review replay, duplicate evidence, AI-disabled operation, and fact lineage. Each proposition must name the corresponding fault-injection artifact and avoid claiming a universal formal proof.

- [ ] **Step 3: Draw two native TikZ diagrams**

`trust-model.tex` shows machine modules terminating at candidates/references, a charcoal human trust boundary, and an amber authoritative transition. `state-transitions.tex` distinguishes candidate states from versioned fact states and labels prohibited direct paths. Use shape, label, and line style in addition to color.

- [ ] **Step 4: Check prose against implementation interfaces**

Map each permitted write to `RecognizeForms.record_candidate`, `AIReviewForms.run`, retrieval read methods, and `ReviewForms.confirm`. Narrow any statement not enforced by these paths.

- [ ] **Step 5: Compile, inspect, and commit**

Render both diagrams at final column width and verify legibility in grayscale. Commit:

```powershell
git add eswa/sections/03_formal_model.tex eswa/figures/vector
git commit -m "paper: formalize candidate-fact separation invariant"
```

### Task 4: Expand methodology and create the author-controlled system figure

**Files:**
- Modify: `eswa/sections/04_methodology.tex`
- Create: `eswa/figures/vector/system-pipeline.tex`
- Create: `eswa/figures/vector/data-lineage.tex`

- [ ] **Step 1: Write the method in reproducible order**

Cover QR template identification, perspective correction, field cropping, digit normalization, score and margin, OMR rejection band, candidate persistence, human decision, versioning, retrieval references, optional LLM suggestions, and offline recovery. Report exact parameters only when confirmed in code or frozen experiment config.

Describe the actual verified software stack from `code-paper-alignment.md`. Do not carry the LNCS FastAPI/React/PWA or ArUco wording forward merely because it appears in the preserved manuscript.

- [ ] **Step 2: Define selective recognition mathematically**

Use smallest and second-smallest template distances `d_1(x)` and `d_2(x)`, margin `s(x)=d_2(x)-d_1(x)`, and threshold `tau`. Define accepted prediction and abstention as separate outputs; do not call confidence a calibrated probability unless calibration is actually measured.

- [ ] **Step 3: Draw the pipeline and lineage diagrams**

Create diagrams from TikZ primitives only. `system-pipeline.tex` follows evidence capture through review and versioned fact export. `data-lineage.tex` shows the identifiers connecting source image, crop, recognition attempt, human decision, fact version, and export. Do not reuse or trace the ChatGPT-generated images.

- [ ] **Step 4: Verify visual consistency and commit**

All diagrams use Trust Teal styles, no gradients, no shadows, consistent arrowheads, and readable labels. Commit:

```powershell
git add eswa/sections/04_methodology.tex eswa/figures/vector
git commit -m "paper: expand reproducible ESWA methodology"
```

### Task 5: Write the experimental protocol before viewing final results

**Files:**
- Modify: `eswa/sections/05_experimental_protocol.tex`
- Modify: `eswa/supplementary.tex`
- Create: `eswa/tables/generated/experiment-grid.tex`

- [ ] **Step 1: Describe the frozen synthetic benchmark**

Report labels, fonts, seeds, perturbation names and severities, sample generation, train/test separation for HOG+SVM, and the reason production records are excluded. State that synthetic performance cannot be extrapolated to plant forms.

- [ ] **Step 2: Define every metric before reporting values**

Define accuracy, coverage, selective risk, erroneous automatic-pass rate, routing rate, fault containment, audit completeness, latency summaries, and bootstrap 95% intervals. State denominators explicitly.

- [ ] **Step 3: Describe baselines and availability rules**

Explain always-predict, HOG+SVM, and Tesseract versions and configuration. If Tesseract is unavailable, say it was excluded before results are analyzed; never reconstruct its value from the LNCS prose.

- [ ] **Step 4: Describe fault injection and validity controls**

List machine-originated faults, stale human replay, duplicate evidence, and operational resilience cases. Clarify that direct database/OS compromise is outside the invariant's scope.

- [ ] **Step 5: Commit the protocol before importing final metrics**

```powershell
git add eswa/sections/05_experimental_protocol.tex eswa/supplementary.tex eswa/tables/generated/experiment-grid.tex
git commit -m "paper: preregister ESWA experimental protocol"
```

### Task 6: Import verified results and write the Results section

**Files:**
- Create: `eswa/artifacts/`
- Create: `eswa/figures/generated/`
- Create: `eswa/tables/generated/`
- Modify: `eswa/sections/06_results.tex`
- Create: `eswa/reviews/claim-artifact-ledger.md`

- [ ] **Step 1: Verify the experiment manifest and hashes**

Reject any copied artifact whose SHA-256 does not match `eswa/artifacts/manifest.json`. Record the experiment commit and dirty state in the claim-artifact ledger.

- [ ] **Step 2: Import generated plots and tables without manual number editing**

Include coverage--risk, robustness, fault outcomes, and latency plots from `figures/generated`. Include threshold, baseline, ablation, fault, and resilience tables from `tables/generated`.

- [ ] **Step 3: Write results in research-question order**

For each finding, state the result, uncertainty interval, comparison, and interpretation. Distinguish “zero observed failures in N tests” from “zero risk.” Report adverse or null findings and baseline exclusions transparently.

- [ ] **Step 4: Build the claim-artifact ledger**

For every number in abstract, results, discussion, or conclusion, record manuscript location, artifact path, JSON field or table cell, experiment commit, and verification status. The ledger must contain no unsupported quantitative claim.

- [ ] **Step 5: Compile and commit**

```powershell
git add eswa/artifacts eswa/figures/generated eswa/tables/generated eswa/sections/06_results.tex eswa/reviews/claim-artifact-ledger.md
git commit -m "paper: report manifest-grounded ESWA results"
```

### Task 7: Complete interpretation, limitations, abstract, and conclusion

**Files:**
- Modify: `eswa/sections/07_industrial_context.tex`
- Modify: `eswa/sections/08_discussion.tex`
- Modify: `eswa/sections/09_limitations.tex`
- Modify: `eswa/sections/10_conclusion.tex`
- Modify: `eswa/main_anonymous.tex`

- [ ] **Step 1: Write industrial context without unverifiable performance claims**

Describe the workflow needs that motivated evidence immutability, offline capture, human authority, and traceability. Do not identify the enterprise in the anonymous manuscript and do not claim measured time, cost, wage-error, or productivity effects.

- [ ] **Step 2: Write the discussion around what the experiments establish**

Interpret the trust boundary separately from recognition quality. Compare selective-risk behavior with prior selective-prediction work, explain the engineering/scientific contribution boundary, and discuss when the architecture is useful.

- [ ] **Step 3: Write explicit threats to validity**

Cover synthetic-to-real distribution shift, limited recognition scope, application-path rather than adversarial-security guarantee, baseline coverage, single-machine latency, and absent human-review-efficiency study.

- [ ] **Step 4: Rewrite the abstract from verified artifacts**

Use at most 250 words. Include purpose, formal trust mechanism, experiment design, principal measured results with intervals or sample counts, and bounded conclusion. Remove the drafting sentence and use no citations.

- [ ] **Step 5: Write a bounded conclusion and commit**

The conclusion must not introduce new numbers or claims and must name the real-data and human-study limitations.

```powershell
git add eswa/main_anonymous.tex eswa/sections/07_industrial_context.tex eswa/sections/08_discussion.tex eswa/sections/09_limitations.tex eswa/sections/10_conclusion.tex
git commit -m "paper: complete bounded ESWA interpretation"
```

### Task 8: Create declarations and submission-side files

**Files:**
- Modify: `eswa/sections/declarations.tex`
- Modify: `eswa/title_page.tex`
- Create: `eswa/highlights.txt`
- Create: `eswa/cover_letter.md`
- Create: `eswa/figure_captions.txt`
- Create: `eswa/submission_checklist.md`

- [ ] **Step 1: Add the data-availability statement**

State that raw production forms cannot be shared or used for public evaluation because they contain employee identity, payroll, and production information and lack authorization for research redistribution. State that synthetic generators, seeds, code, raw benchmark outputs, and manifests are available.

- [ ] **Step 2: Add the generative-AI declaration**

Use the journal-required section title and this factually complete content, adjusted only to the submission system's current wording:

```tex
\section*{Declaration of generative AI and AI-assisted technologies in the manuscript preparation process}
During the preparation of this work, the authors used DeepSeek Harness and OpenAI Codex to support drafting, content organization, and language editing. The authors reviewed and edited all AI-assisted material, independently verified the sources and experimental evidence, and take full responsibility for the content of the article.
```

- [ ] **Step 3: Add funding and competing-interest statements without guessing**

Until definitive author information is supplied, state in the drafting package that no specific grant or competing interest has been reported to the manuscript preparer. Before submission, replace this administrative drafting status only with author-confirmed information; flag it as a submission blocker in the checklist rather than inventing a declaration.

- [ ] **Step 4: Write compliant highlights**

Create three to five bullets, each no more than 85 characters including spaces. Verify character counts with a script and focus on measured novelty, not generic claims.

- [ ] **Step 5: Write cover letter, captions, and title-page separation**

The cover letter must explain ESWA scope fit, originality, non-concurrent submission, data restrictions, open experiment artifacts, and bounded claims. The title page remains a separate file and contains anonymous drafting metadata until the user provides definitive authors, affiliations, corresponding-author contact, acknowledgements, funding, and interests.

- [ ] **Step 6: Commit**

```powershell
git add eswa/sections/declarations.tex eswa/title_page.tex eswa/highlights.txt eswa/cover_letter.md eswa/figure_captions.txt eswa/submission_checklist.md
git commit -m "paper: add ESWA submission declarations and files"
```

### Task 9: Compile, visually inspect, audit, score, and estimate publication prospects

**Files:**
- Generate: `eswa/main_anonymous.pdf`
- Generate: `eswa/supplementary.pdf`
- Create: `eswa/reviews/pre-submission-report.md`
- Create: `eswa/reviews/eswa-readiness-assessment.md`

- [ ] **Step 1: Run a clean multi-pass build**

Run `latexmk -pdf -interaction=nonstopmode -halt-on-error main_anonymous.tex`, or a documented `pdflatex`/BibTeX fallback if MiKTeX blocks latexmk. Expected: no unresolved citations or references and a readable PDF.

- [ ] **Step 2: Run structural compliance checks**

Verify abstract word count is at most 250, keywords number one to seven, highlights number three to five and each at most 85 characters, all sections are numbered except declarations, every figure/table is cited, and the anonymous file contains no author/institution/funding identifiers.

- [ ] **Step 3: Run citation and claim audits**

Require zero missing/unused citation keys. Cross-check every quantitative manuscript claim against `claim-artifact-ledger.md` and the artifact hashes. Require zero unsupported numbers.

- [ ] **Step 4: Perform page-by-page visual QA**

Render every PDF page to images. Check clipping, font size, float placement, caption readability, table width, vector-figure sharpness, color consistency, grayscale interpretability, and blank or sparse pages. Correct source and rerun the full build after any visual change.

- [ ] **Step 5: Run the 35-point academic quality gate**

Score originality, argumentation, literature coverage, methodological rigor, clarity, academic impact, and technical accuracy from 1 to 5 with concrete evidence. A score below 28/35 blocks a “ready to submit” recommendation and triggers targeted revision.

- [ ] **Step 6: Estimate ESWA publication prospects**

Create `eswa-readiness-assessment.md` containing:

- scope-fit verdict based on ESWA's official aims;
- likely desk-rejection risks;
- likely reviewer objections;
- evidence strengths and external-validity limits;
- a clearly labeled subjective probability interval for reaching peer review and for eventual acceptance;
- separate estimates for the current synthetic-only package and a future package with a real double-entered validation set;
- the assumptions behind every estimate and a warning that it is not an official acceptance rate.

Do not choose the probability before completing the manuscript and audits.

- [ ] **Step 7: Commit final verified deliverables**

```powershell
git add eswa/main_anonymous.tex eswa/main_anonymous.pdf eswa/supplementary.tex eswa/supplementary.pdf eswa/reviews
git commit -m "paper: finalize and assess ESWA submission package"
```

- [ ] **Step 8: Integrate to the source directory**

Merge the isolated paper branch only after all checks pass. Confirm the final user-facing files are under `D:\Claude_Design\auto-decte-paper\eswa`, the preserved LNCS files are byte-identical to the preservation commit, and the temporary worktree can be removed after integration.
