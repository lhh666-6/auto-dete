# Auto-Decte: Trust-Constrained Human-in-the-Loop Document Intelligence for Industrial Paper Forms

> Draft v0.5 — 2026-08-15 (research framing per PAKDD-style review: trust-constrained framework + selective recognition as core contribution).
> All benchmark numbers are measured on the deployed system.

## Abstract

High-stakes document extraction --- such as digitizing paper payroll and production forms --- demands more than accuracy: a single mis-transcribed digit changes a worker's wage, so machine errors must never silently enter the factual record. We propose a trust-constrained human-in-the-loop framework for document intelligence, and instantiate it in Auto-Decte, a deployed system for industrial paper forms. The framework rests on two principles: (i) **candidates, never facts** --- every machine output (perception, LLM suggestion, or retrieval result) is an append-only candidate or a read-only reference, and only human confirmation or correction creates a versioned fact; and (ii) **abstention over guessing** --- recognition emits an explicit ambiguity band and abstains on borderline cells, routing them to review instead of risking silent errors. Perception is fiducial-guided (QR classification, ArUco perspective correction) rather than learned, making geometry deterministic; a DeepSeek adapter and a local retrieval index assist reviewers under the same trust boundary, and a PWA with an offline outbox extends submission to the plant floor. We evaluate recognition accuracy, a selective-prediction coverage-vs-risk curve, robustness under perturbation, retrieval precision, end-to-end whole-form accuracy (97.5% clean), and traceability/AI-off invariants (389 acceptance tests).

## 1. Introduction

Foundation-model-assisted document processing is attractive for the long tail of paper-based workflows in small and medium plants, but payroll-adjacent settings impose a stricter requirement than raw accuracy: trust. An LLM that transcribes one digit wrong changes a worker's wage; a retrieval system that injects a similar-looking historical record can silently corrupt a decision. Fully automatic pipelines are therefore unacceptable where errors carry financial consequences, yet purely manual digitization does not scale. This motivates our central research question:

> **How can machine learning and generative assistance extract information from high-risk paper documents while guaranteeing that machine errors never enter the factual data layer?**

We address this with a trust-constrained framework whose two principles are (i) *candidates, never facts*, and (ii) *abstention over guessing*. Concretely, we study three sub-problems: (RQ1) how to reduce perception uncertainty on structured paper forms (template-guided perception with an explicit ambiguity band); (RQ2) how to let LLM/RAG provide assistance without contaminating facts (candidate/reference isolation); and (RQ3) how to make human confirmation the sole path that writes facts while preserving traceability (append-only candidates, versioned decisions, evidence lineage).

Our contributions are:
1. A **trust-constrained document intelligence framework** that separates an evidence layer, a candidate plane, a human trust boundary, and a fact plane, and enforces the invariant that machine outputs never become facts.
2. **Selective recognition via abstention**: recognition emits a per-cell ambiguity band (template-matching margin for digits, fill-ratio band for OMR) and abstains on borderline cells; we report the resulting coverage-vs-selective-risk trade-off.
3. **Trustworthy LLM/RAG integration**: suggestions are stored separately and cannot mutate confirmed values, retrieval is strictly read-only, and the AI-off path keeps the pipeline correct.
4. An offline-capable mobile submission path feeding the same review queue as scanned forms, and a deployment case study with end-to-end acceptance and honest reporting of what remains unmeasured.

## 2. Problem Formulation and Design Principles

**High-risk document extraction.** A paper form is photographed and must be converted into structured, trustworthy records. Formally, a form image $x$ is mapped to a set of field values $y=\{y_j\}$. The key requirement is not only that $\hat y_j$ be accurate, but that any machine error be *detectable and non-persistent*: a wrong machine output must not survive into the stored record without human awareness.

**Candidate vs fact.** We distinguish three data planes. The *evidence plane* holds immutable, content-addressed inputs (SHA-256 images). The *candidate plane* holds everything a machine produces: recognition hypotheses, LLM suggestions, and retrieval references --- all append-only and forbidden from overwriting facts. The *fact plane* holds versioned values that exist only after a human confirms or corrects them. This separation is architectural, not advisory: the data model enforces it.

**Abstention over guessing.** A recognizer should predict only when its uncertainty is low; otherwise it should abstain and route the cell to review. We operationalize this with a per-cell confidence and an explicit ambiguity band, so that abstention is a first-class output rather than a threshold tuned after the fact.

## 3. Trust-Constrained Document Intelligence

**3.1 Template-guided perception.** Instead of learning layout from data, templates are generated by the system with a QR code (identity + version) and ArUco corner markers (IDs 10--13). A multi-region QR search classifies the form; four ArUco markers map it to a canonical canvas via perspective correction; fields are then cropped from the known template definition. This makes identification and geometry deterministic and auditable, and it confines recognition to per-cell decisions.

**3.2 Selective recognition with an ambiguity band.** Digit cells are normalized to $48{\times}64$, binarized (Otsu), and matched against ten rendered synthetic-font templates by normalized mean absolute difference. The recognizer reports the top digit, a distance-based confidence, and --- when the margin to the second-best template is below a threshold $\tau$ --- abstains, flagging the cell AMBIGUOUS. Blank cells (ink ratio $<1\%$) are reported as blank. Checkbox (OMR) cells use an interior fill ratio: $\le 0.15$ unchecked, $\ge 0.35$ checked, and the $(0.15,0.35)$ band abstains with zero confidence. The abstraction is a decision rule $D(x)=\hat y$ if confidence $\ge\tau$, else ABSTAIN; Section 6 reports the coverage-vs-risk curve over $\tau$.

**3.3 Candidate isolation.** Recognition attempts, LLM suggestions, and retrieval references are stored as append-only candidates that reference their evidence and can never overwrite a confirmed value. The LLM adapter (DeepSeek, structured output) is disabled by default; the core pipeline runs end-to-end with the model off.

**3.4 Read-only retrieval.** A local, dependency-free similarity index (character-bigram + word cosine) surfaces similar historical forms as references. Retrieval results are strictly read-only and do not participate in statistics or fact modification.

**3.5 Human decision layer.** A React review workbench is the sole path from candidate to fact: operators confirm or correct every value under rule validation, each human action appends a versioned record with a before/after audit pair, and exports are back-traceable to form, version, evidence, and event log.

## 4. System Architecture

Auto-Decte implements the four planes as a single-machine deployment. The evidence layer stores SHA-256-addressed images; the candidate layer holds append-only recognition attempts, isolated suggestions, and read-only retrieval references; the trust boundary is the review workbench; the fact layer holds versioned records, audit events, and export batches, with role-based access (operator, reviewer, finance, admin, auditor). A PWA front end with an IndexedDB outbox (scrypt credentials, HttpOnly cookies, CSRF double-submit, idempotency keys) routes in-plant mobile submissions into the same review queue.

## 5. Implementation

The backend is FastAPI (Python 3.11) with SQLite via SQLAlchemy 2.0 and Alembic migrations; the front end is React 18 + Vite; image operations use OpenCV; suggestions use a DeepSeek client; retrieval is a local vector index. The codebase is covered by 389 passing tests on the public snapshot (159 additional tests require enterprise database fixtures excluded by data policy).

## 6. Experimental Evaluation

**Methodology.** Functional acceptance via the automated suite; controlled benchmarks on synthetic filled forms under perturbations (blur, rotation, brightness, Gaussian noise, perspective tilt); a learned baseline and a general-OCR baseline for comparison; retrieval precision on a synthetic corpus; and a selective-prediction sweep.

**Recognition accuracy.** Digit recognition is 93.9% overall across 28 font$\times$perturbation conditions: 100% on the printed template font under blur/rotation/noise/brightness, and 80--90% on unseen fonts with 10--20% of cells abstained --- i.e., degradation concentrates in the human-routed channel rather than silent errors. OMR is 100% correct outside the ambiguity band and 100% abstained inside it.

**Selective recognition (abstention).** Sweeping the margin threshold $\tau$ yields the coverage-vs-risk curve in Table~\ref{tab:selective}. At the operating point $\tau{=}0.02$ the system covers 93.7% of cells at 94.7% accepted accuracy (5.3% selective risk); tightening $\tau$ to $0.05$ raises accepted accuracy to 100% (zero silent errors) while covering 61.4% and routing the rest to review. This quantifies the intended trade-off: abstention buys zero-silent-error extraction at a coverage cost.

\begin{table}[t]
\centering
\caption{Selective recognition: coverage vs selective risk over the abstention threshold $\tau$.}
\label{tab:selective}
\begin{tabular}{lcccc}
\toprule
$\tau$ & Coverage & Accepted acc. & Selective risk & Routing rate \\
\midrule
0.000 (always guess) & 1.000 & 0.938 & 0.062 & 0.000 \\
0.020 (operating) & 0.937 & 0.947 & 0.053 & 0.063 \\
0.050 & 0.614 & 1.000 & 0.000 & 0.386 \\
0.080 & 0.411 & 1.000 & 0.000 & 0.589 \\
\bottomrule
\end{tabular}
\end{table}

**Baseline comparison.** A learned HOG + linear-SVM recognizer reaches 100% on the printed font and 79.7--80.3% on unseen fonts --- comparable to the template matcher --- but has no abstention mechanism, so its errors are silent. Against general OCR (Tesseract, single-character mode), the template matcher wins on the deployment-relevant printed-template regime (100% vs 84--87%), whereas Tesseract generalizes better to unseen fonts (94--95% vs 86--90%), which is outside the printed-form scope; in all cases only the template matcher emits an ambiguity channel.

**Template detection and geometry.** QR recovery succeeds on 100% of 90 perturbed renders; ArUco correction succeeds on 100% of clean/blur/noise/brightness/tilt images with $\le 0.34$\,px alignment error, dropping to 50%/20% at $3^\circ$/$5^\circ$ rotation --- the known weak axis of fiducial recovery.

**End-to-end whole-form.** Synthetic filled forms (10 digit cells + 10 OMR boxes) processed through the full pipeline yield cell-level accuracy 97.5% clean and 96.5--98.0% under blur/noise/brightness/tilt, with 4.5--8.5% of digit cells abstained; under $3^\circ$ rotation, correction success drops to 60%. Per-image latency is QR search 2{,}180\,ms, quality 20\,ms, correction 35\,ms.

**Retrieval precision.** On a corpus of 200 records across five templates (relevance = same template key), mean precision is 1.00@1, 0.99@3, 0.975@5, 0.95@10, confirming the retrieval surfaces the intended same-template references.

**Trust boundary (fault injection).** To verify the invariant that machine errors never become facts, we adversarially inject a wrong LLM suggestion (suggested value $\neq$ the confirmed value) into a form with a confirmed record. The confirmed fact is unchanged, the wrong suggestion is stored separately as a candidate, and no record version ever carries the machine value; a subsequent human correction remains the authoritative fact. The acceptance suite additionally enforces the AI-off path (workflow completes with the model disabled), read-only retrieval, and back-traceable exports.

**LLM/RAG assistance.** Trust is treated as the primary acceptance criterion, so the AI layer is designed for correctness before efficiency. The efficiency of the assistant --- reviewer time, error-catch rate, suggestion acceptance --- is the natural next evaluation step in a planned field pilot (Section 8); it is not claimed here.

## 7. Industrial Case Study

Auto-Decte is deployed as a working baseline at a bamboo-processing plant, replacing hand-kept paper payroll and production records. Deployment establishes that the system runs in a real industrial setting; the quantitative experiments of Section 6 are, by contrast, conducted on controlled, reproducible benchmarks, because real production data is excluded from the public repository by policy. We therefore do not claim a measured industrial deployment effect: deployment motivates the design (traceability, offline submission, human authority over payroll values) and provides the substrate for a future field pilot.

## 8. Limitations and Future Work

General handwritten / Chinese-text / signature OCR is not implemented (only single-cell printed digits and OMR); deployment is single-machine without a completed multi-user capacity test; the evaluation lacks a 30--50-form golden set with double entry and real plant images, so accuracy claims are limited to controlled benchmarks; and the LLM assistant has no measured end-to-end efficiency gain. Future work: general OCR integration, independent task workers, a quantitative human-review-efficiency study (recognition-only vs +retrieval vs +LLM), and a field pilot measuring financial-processing time reduction.

## 9. Conclusion

Auto-Decte instantiates a trust-constrained human-in-the-loop framework in which machine perception, LLM suggestions, and retrieval produce candidates and references, while humans remain the only source of facts, with full traceability from photograph to exported cell. The selective-recognition mechanism trades coverage for zero-silent-error extraction, and the AI layer assists without ever writing facts. The system is deployed as a working baseline and provides the substrate for a quantitative field study.

## Appendix: benchmark scripts and artifacts

- Repo: `lhh666-6/auto-decte`; acceptance report `docs/acceptance-report.md`.
- Benchmarks under `benchmarks/`: digit/OMR, template detection, HOG+SVM baseline, general-OCR comparison, end-to-end forms, retrieval precision, selective-recognition sweep, each with `results_*.json` and `report_*.md`.
