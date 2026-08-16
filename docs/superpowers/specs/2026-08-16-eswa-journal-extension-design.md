# Auto-Decte ESWA Journal Extension Design

Date: 2026-08-16  
Target journal: *Expert Systems with Applications* (ESWA)  
Paper type: Methods and industrial intelligent-system application

## 1. Objective

Create an ESWA-ready journal extension of Auto-Decte without modifying or replacing the existing LNCS manuscript. The journal paper will present candidate--fact separation as an enforceable trust invariant, selective abstention as its complementary decision mechanism, and a reproducible evaluation based on synthetic document generation, controlled perturbations, fault injection, ablation, and statistical uncertainty.

The paper will not claim measured real-world accuracy, productivity gains, payroll-error reduction, or reviewer-efficiency improvements. Real production records cannot be used for reproducible evaluation because they contain employee identity, payroll, and production information governed by enterprise data-protection constraints.

## 2. Fixed Constraints

- Preserve `lncs/`, including `main.tex`, `main-polished.pdf`, and all existing LNCS artifacts.
- Create the journal manuscript under `eswa/` as an independent Elsevier LaTeX project.
- Perform experimental development in a separate clone at `D:\Claude_Design\auto-decte-eswa` on branch `codex/eswa-experiments`; do not alter the public repository's `main` branch directly.
- Use only measured outputs produced by executable scripts. Do not invent results, sample sizes, confidence intervals, or deployment effects.
- Treat the industrial deployment as application context and design motivation, not quantitative effectiveness evidence.
- Do not include the three ChatGPT-generated engineering illustrations in the ESWA submission. Replace them with author-controlled TikZ or SVG diagrams derived from the implemented architecture.
- Include a transparent generative-AI declaration describing the use of DeepSeek Harness and Codex for drafting, organization, and language editing under author review.

## 3. Research Positioning

### 3.1 Central research question

How can OCR, large-language-model assistance, and retrieval support high-risk document processing while an enforceable system architecture prevents unreviewed machine outputs from entering the authoritative fact layer?

### 3.2 Main claim

Auto-Decte enforces a candidate--fact separation invariant: every machine module terminates at an append-only candidate or read-only reference interface, while authoritative fact transitions require an attributable human decision. This architectural claim is distinct from recognition accuracy and does not imply that humans catch every incorrect candidate.

### 3.3 Contribution hierarchy

1. A formal trust model covering evidence, candidates, human decisions, facts, permitted transitions, and prohibited machine-to-fact transitions.
2. A selective-recognition mechanism that exposes the coverage--risk and human-routing trade-off through explicit abstention.
3. Reproducible verification through adversarial fault injection, synthetic perturbation benchmarks, ablations, baselines, and confidence intervals.
4. An offline-capable industrial implementation demonstrating how the model can be instantiated under data-governance constraints.

### 3.4 Scope boundaries

The evaluation covers structured printed forms, single-cell digits, OMR fields, QR template identification, fiducial alignment, candidate persistence, review transitions, retrieval references, and optional LLM suggestions. General handwriting, free-form Chinese OCR, signatures, multi-user scalability, field-effectiveness claims, and human-efficiency outcomes are outside the paper's validated scope.

## 4. Formal Model

Define four planes: evidence `E`, candidates `C`, human decisions `H`, and versioned facts `F`. Define machine modules `M` as perception, LLM assistance, and retrieval. The permitted transition system must encode:

- machine writes to candidates or references only;
- evidence is immutable and content-addressed;
- candidates are append-only and linked to evidence;
- retrieval output is read-only;
- a fact transition is produced only by an attributable human decision;
- each fact version can be traced to its prior version, decision, candidate, and evidence.

The primary invariant is `for all m in M, m cannot transition F directly`. Supporting propositions will cover preservation under incorrect suggestions, replayed requests, duplicate evidence, disabled AI, and failed network submission. Executable fault-injection tests will operationalize these propositions; the paper will distinguish test evidence from a universal proof of all possible implementations.

## 5. Experimental Design

### 5.1 E1: Trust-boundary fault injection

Inject incorrect OCR candidates, incorrect LLM suggestions, irrelevant retrieval results, duplicate requests, stale-version replays, and attempted direct fact writes. Measure prohibited-write success count, unchanged-fact rate, audit completeness, lineage completeness, and deterministic rejection behavior.

### 5.2 E2: Synthetic document benchmark

Generate structured forms with controlled labels across digits, supported fonts, OMR states, template variants, and seeded randomization. Apply graded blur, Gaussian noise, brightness changes, perspective distortion, rotation, compression, and occlusion. Retain clean source labels and configuration metadata so every sample is reproducible.

Report results by perturbation type and severity rather than relying only on an aggregate mean. Explicitly characterize the synthetic-to-production validity gap.

### 5.3 E3: Selective prediction

Sweep the abstention threshold and report coverage, accepted accuracy, selective risk, erroneous automatic-pass rate, and human-routing rate. Use repeated seeded generation and bootstrap 95% confidence intervals. Select any operating point using a declared criterion rather than post-hoc preference.

### 5.4 E4: Baselines and ablations

Compare the supported recognizer with always-predict behavior, Tesseract single-character recognition, and HOG plus linear SVM where dependencies permit reproducible execution. Evaluate the contribution of abstention, QR identification, ArUco correction, and candidate isolation. Candidate isolation will be evaluated through bypass attempts in a test harness, not by shipping an unsafe production mode.

### 5.5 E5: Operational resilience and performance

Test AI-disabled operation, offline submission recovery, duplicate evidence import, record-version traceability, export back-tracing, and batch latency. Report hardware, software versions, warm-up policy, repetition count, and distribution summaries.

### 5.6 Evidence flow

Each experiment writes machine-readable JSON or CSV, a run manifest containing commit hash and random seeds, and script-generated figures/tables. Manuscript numbers must be generated from or checked against these artifacts. No result will be manually introduced without a matching artifact.

## 6. Manuscript Structure

The anonymous manuscript will target approximately 7,000--9,000 words and use numbered sections:

1. Introduction
2. Related work
3. Problem definition and formal trust model
4. Auto-Decte methodology
5. Experimental protocol
6. Results
7. Industrial context and data-governance constraints
8. Discussion
9. Limitations and threats to validity
10. Conclusion

Supplementary material will contain full generation parameters, perturbation grids, fault-injection cases, extended results, and reproducibility instructions.

## 7. Submission Artifact Layout

The new `eswa/` project will contain:

- `main_anonymous.tex`: double-anonymized manuscript;
- `title_page.tex`: author and affiliation page kept separate from the manuscript;
- `references.bib`: verified bibliography;
- `highlights.txt`: three to five bullets, each no more than 85 characters;
- `cover_letter.md`: ESWA-specific cover letter;
- `data_availability.tex`: production-data restriction and synthetic-artifact availability;
- `supplementary.tex`: reproducibility and extended experiments;
- `figures/`: non-generative vector diagrams and script-generated plots;
- `tables/`: generated LaTeX tables;
- `artifacts/`: run manifests and summarized result files used by the paper.

The title page will remain separate and will be completed only from definitive author-provided metadata. This does not block the anonymous manuscript or experiments.

## 8. Figures and AI Disclosure

The three ChatGPT-generated diagrams remain part of the preserved LNCS project but will not be submitted to ESWA. Their factual content may inform newly drawn architecture diagrams, but the replacement graphics will be constructed from explicit nodes, edges, labels, and implemented data flows using TikZ or SVG tooling.

The selected visual system is **Trust Teal**:

- teal `#16796F` for evidence and permitted candidate data flows;
- charcoal `#243746` for trust boundaries, structural labels, and primary text;
- amber `#C06B19` for human decisions, warnings, and authoritative transitions;
- pale teal `#E1F2EF` and pale amber `#FFF0DC` for restrained fills;
- white or near-white backgrounds, without gradients, decorative shadows, or pictorial embellishment.

Figures will use consistent node shapes, arrowheads, line weights, label hierarchy, and panel lettering. Color will never be the sole encoding: curves also differ by line style or marker, states use labels or patterns, and all graphics must remain interpretable in grayscale. Tables will use booktabs-style horizontal rules, aligned decimal columns, restrained emphasis, and no vertical grid. Figure text will remain legible at final single- or double-column size.

The manuscript will include the required section titled `Declaration of generative AI and AI-assisted technologies in the manuscript preparation process`. It will state that DeepSeek Harness and Codex were used for drafting, organization, and language editing; the authors reviewed and edited the content and take responsibility for the article. AI tools will not be credited as authors and will not generate experimental observations.

The authors' review responsibility covers the accuracy, completeness, impartiality, and originality of AI-assisted material; verification of every source and reference; substantive editing so that the paper reflects the authors' own analysis and interpretation; and protection of confidential data, intellectual property, and other rights. The declaration will follow the wording required by the submission system at the time of submission.

Elsevier's general AI policy and the journal-specific ESWA guide must be read together. Where their wording differs in specificity, the stricter journal-specific requirement governs the submission. Accordingly, the project will not rely on attribution alone for the existing generated engineering illustrations; it will replace them with non-generative, author-controlled diagrams.

## 9. Data Availability and Ethics Language

The data statement will explain that raw production forms cannot be shared because they contain employee identity, payroll, and production information and were not authorized for research redistribution. It will also state that the reported quantitative evaluation uses openly releasable synthetic documents generated by published scripts and seeds.

This constraint will be presented as a threat to external validity. It will not be used to imply unmeasured production accuracy or operational benefits.

## 10. Failure Handling

- If a baseline cannot run reproducibly, report the dependency or compatibility failure and exclude it rather than estimating a result.
- If a current paper number cannot be regenerated, remove or qualify the claim until supporting evidence exists.
- If synthetic results show a weakness, retain the result and revise the scope or operating criterion rather than tuning it away without disclosure.
- If a fault-injection test reaches the fact layer without an attributable human decision, treat it as a blocking defect and fix the implementation before writing the corresponding claim.
- If the Elsevier template or local TeX environment fails, preserve the source and use a documented alternative compile path while retaining ESWA submission structure.

## 11. Verification and Quality Gates

Completion requires:

- all experiment scripts execute from documented commands;
- every reported number maps to a generated artifact;
- citation keys and bibliography entries match, with core claims checked against primary sources;
- the anonymous manuscript contains no author, institution, funding, or identifying deployment details;
- abstract length is at most 250 words and keywords number from one to seven;
- highlights contain three to five bullets of at most 85 characters each;
- AI disclosure, competing-interest text, funding statement, and data-availability statement are present in the correct submission files;
- the LaTeX project compiles without unresolved references or citations;
- the final PDF receives page-by-page visual inspection;
- a final quality-gate review separates confirmed strengths from remaining threats to validity.

## 12. Success Criteria

The project succeeds when it produces an independently compilable ESWA submission package and a reproducible experiment package while leaving the LNCS version unchanged. The resulting paper must make only claims supported by generated artifacts, describe confidentiality constraints transparently, and provide a substantially stronger scientific evaluation than the preserved conference manuscript.
