# Auto-Decte: An LLM- and RAG-Assisted Human-in-the-Loop Document Intelligence System for Industrial Paper Forms

> Draft v0.3 — 2026-08-14 (LLM/RAG/human-in-the-loop repositioning). Benchmarked numbers are measured on the deployed system.
> Target venue: AI-application EI/CCF-C conference (IJCNN 2027 primary; autumn-deadline AI/information-systems EI venues as backup).

## Abstract

Deploying large language models (LLMs) in high-stakes enterprise workflows is constrained less by model capability than by trust: suggestions must never silently become facts, every decision must be traceable to evidence, and the system must keep working when the model is unavailable. This paper presents Auto-Decte, a document intelligence system for industrial paper forms that operationalizes these constraints through a human-in-the-loop architecture. A fiducial-guided perception front end (QR/ArUco template recognition, perspective correction, per-cell digit and OMR recognition with an explicit ambiguity band) converts photographed paper forms into structured candidate values. An LLM suggestion adapter (DeepSeek, structured output) and a local vector similarity-retrieval module (RAG-style, read-only) assist reviewers, while a React review workbench makes the human the only source of truth: machine outputs are stored as append-only candidates, and only human confirmations or corrections become versioned, auditable records. A PWA front end with an offline outbox extends submission to in-plant mobile devices. The system is evaluated on end-to-end acceptance (389 public-snapshot tests, including the AI-off path and suggestion-isolation invariants), front-end recognition benchmarks (digit 93.9% overall, 100% on the printed font family; OMR 100% correct outside the ambiguity band; QR 100%; ArUco correction ≤0.34 px), a baseline comparison against a learned HOG+SVM recognizer (comparable accuracy, but only the template matcher routes ambiguity to humans), end-to-end whole-form cell accuracy of 97.5% clean, and per-image latency (≈2.2 s, QR search dominant).

## 1. Introduction

Foundation-model-assisted document processing is attractive for the long tail of paper-based workflows in small and medium plants, but its adoption in payroll-adjacent settings is blocked by a trust problem: an LLM that transcribes a digit wrong changes a worker's wage, and a retrieval system that injects a similar-looking historical record into a decision can silently corrupt it. Fully automatic pipelines are therefore unacceptable where errors carry financial consequences, yet purely manual digitization does not scale.

Auto-Decte addresses this with a human-in-the-loop architecture built on three principles: (i) **machine outputs are candidates, never facts** — the LLM adapter and every recognition stage emit candidates that a human must confirm or correct; (ii) **the document is engineered** — templates are generated with QR codes and ArUco fiducials so that perception is reliable rather than learned; (iii) **everything is auditable** — evidence is content-addressed, records are append-only versions, and every exported cell is back-traceable. The system is deployed as a working baseline at a bamboo-processing plant.

Contributions:

1. A human-in-the-loop document intelligence architecture for industrial paper forms, integrating a fiducial perception front end, an LLM suggestion adapter, and local similarity retrieval under a single "candidates-only, human-confirmed" trust boundary.
2. Trustworthy LLM/RAG integration mechanisms: suggestions are stored separately and can never mutate confirmed values; retrieval results are strictly read-only; the core pipeline runs and remains correct with the AI layer fully disabled (guarded by acceptance tests).
3. An engineered, interpretable perception front end — synthetic-font template matching for digit cells and a fill-ratio OMR recognizer — whose explicit ambiguity band routes borderline cells to humans instead of guessing.
4. An offline-capable mobile submission path (PWA + IndexedDB outbox + idempotency keys) that feeds the same review queue as scanned forms.
5. A deployment-motivated case study with end-to-end acceptance evidence and honest reporting of what remains unmeasured.

## 2. Related Work

**Document OCR and layout analysis.** General document AI stacks (PP-OCRv3 [arXiv:2206.03001], LayoutLMv3 [arXiv:2204.08387], Donut [arXiv:2111.15664]) target free-form documents with learned detection and recognition. Auto-Decte deliberately keeps learned layout models out of the critical path: system-generated templates make layout known exactly, so perception reduces to fiducial-guided cropping plus per-cell template matching; learned OCR remains a future extension for handwriting and Chinese text.

**LLM assistance and retrieval.** Retrieval-augmented generation and generative information-extraction surveys [arXiv:2312.17617, arXiv:2409.14924] and Local-First Software principles [Onward! 2019, DOI 10.1145/3359591.3359737] motivate two components: a read-only DeepSeek structured-output suggestion adapter and a local vector similarity index. The distinction from generic RAG is architectural: in Auto-Decte the model and the retriever are denied write access to facts by construction, and their outputs are versioned separately from records.

**Human-in-the-loop digitization.** HITL principles for high-stakes data (Budd et al., Med. Image Anal. 2021, DOI 10.1016/j.media.2021.102062; drilling-report digitization, EAGE 2025) motivate the review workbench: machine outputs are append-only candidates, and every confirmed or corrected value is a versioned human decision with a before/after audit pair.

**Fiducial-based localization and OMR.** ArUco [DOI 10.1016/j.imavis.2018.05.004] and MILP dictionary markers [DOI 10.1016/j.patcog.2015.09.023] provide geometric anchoring; existing OMR systems (e.g., SurveyNet, J. Imaging 12(4):175, DOI 10.3390/jimaging12040175) evaluate bulk mark recognition. Auto-Decte's distinguishing feature is the first-class ambiguity band: cells in the intermediate fill band are emitted with zero confidence and force review rather than a thresholded guess.

**Positioning.** Four decisions distinguish Auto-Decte from prior systems: (i) machine outputs — from recognition and from the LLM alike — are candidates, never facts; (ii) an explicit ambiguity band routes borderline cells to humans; (iii) full traceability — SHA-256 evidence, versioned records, audit events, back-traceable exports; (iv) offline mobile submission integrated with the same review queue.

## 3. System Overview

Auto-Decte is a single-machine deployment: FastAPI (Python 3.11) backend, SQLite via SQLAlchemy 2.0 with Alembic migrations, React 18 + Vite front end, OpenCV for image operations, a DeepSeek client for structured-output suggestions, and a local vector index for similarity retrieval. Fig. 1 (figures/architecture.png) shows the pipeline stages.

The domain model separates immutable evidence, versioned form records (`RecordVersion`), append-only recognition attempts, isolated AI suggestions, read-only retrieval references, audit events, and export batches. Roles (operator, reviewer, finance, admin, auditor) gate every mutation.

## 4. Template Design and Perception Front End

Templates are designed and published inside the system (template center with versioning and draft canvas). Each published template renders a PDF/PNG with a QR code (template identity + version) and ArUco markers at known positions. Recognition is fiducial-first: a multi-region QR search classifies the form, four ArUco corner markers (IDs 10–13) map it to the canonical canvas, perspective correction aligns it, and per-field cells are cropped from the template definition. This makes identification and geometry deterministic and auditable.

## 5. Field-Level Recognition with Confidence and Ambiguity

**Digit cells.** Each cell is normalized to 48×64, binarized with Otsu thresholding, and matched against ten rendered synthetic-font templates (0–9) by normalized mean absolute difference. The recognizer reports the best digit, a distance-based confidence, and an `AMBIGUOUS` flag when the margin to the second-best template falls below 0.02. Blank cells (ink ratio < 1%) are reported as blank rather than as a digit.

**Checkbox (OMR) cells.** Fill ratio in the cell interior is computed after Otsu binarization; ratios ≤ 0.15 map to unchecked, ≥ 0.35 to checked, and the (0.15, 0.35) band maps to `AMBIGUOUS` with zero confidence. The ambiguity band is the key design choice: it routes exactly the cells that recognition cannot decide to the human, instead of silently guessing.

## 6. LLM Assistance and Similarity Retrieval

Two optional AI components support the reviewer, both constrained to be unable to write facts:

- **LLM suggestions (DeepSeek).** A structured-output client requests field suggestions for a form under review. Suggestions are stored separately from records, carry their evidence reference, and can never mutate confirmed values. The adapter is disabled by default; the core pipeline is fully functional without any external model (an acceptance-tested AI-off path).
- **Similarity retrieval (local vector index).** Historical records are indexed locally; the review page shows similar past forms as reference. Retrieval results are strictly read-only — they do not participate in statistics or fact modification (guarded by acceptance tests).

The trust boundary is architectural: the model and the retriever produce candidates and references; only the reviewer produces facts.

## 7. Data Integrity, Versioning, and Export

Evidence images are content-addressed with SHA-256; duplicates are detected and never silently overwritten. Every human correction appends a `RecordVersion` with before/after audit rows. XLSX export produces four worksheets (formal data, exceptions & review, summary, export notes) and every exported cell is back-traceable to form, version, evidence image, and event log.

## 8. Offline Mobile Submission

A PWA front end supports in-plant phone use: mobile credentials are salted with scrypt; sessions use HttpOnly SameSite cookies with CSRF double-submit; drafts live in an IndexedDB outbox keyed by owner/device with idempotency keys; retries back off on network errors and stop on 4xx conflicts; mobile submissions flow into the same NEEDS_REVIEW path as scanned forms.

## 9. Evaluation

Methodology: end-to-end functional acceptance via the automated test suite; controlled benchmarks on the perception front end using the system's canonical template conventions and synthetic perturbations (blur, rotation, brightness, Gaussian noise, perspective tilt) plus fill-ratio sweeps for OMR; per-stage latency on A4@150 dpi images (desktop hardware, CPU timing).

**Functional acceptance and trustworthy-AI invariants.** On the public snapshot of the integration branch, 389 tests pass. Beyond core digitization (import, SHA-256 dedup, QR classification, digit/OMR candidates, rule validation, human confirmation, export, reverse traceability), the suite enforces the AI trust boundaries: the AI-off path completes the workflow end-to-end; LLM suggestions are stored separately from confirmed values; similarity-retrieval results are read-only references. 159 additional tests require enterprise database fixtures excluded from the public repository by data policy.

**Perception front end.** (i) Digit recognition: 93.9% overall across 28 font × perturbation conditions; 100% on the system's printed font family under blur/rotation/noise/brightness; 80–90% on unseen fonts with 10–20% of cells flagged ambiguous — degradation concentrates in the human-routed ambiguity channel rather than silent errors. (ii) OMR: ratios ≤ 0.15 classified unchecked (100% correct), ≥ 0.50 classified checked (100% correct), and (0.15, 0.50) emitted ambiguous (100% routed to review). (iii) Template detection & geometry: QR recovery 100% on 90 perturbed renders; ArUco correction 100% under blur/noise/brightness/tilt with ≤ 0.34 px alignment error, dropping to 50%/20% at 3°/5° rotation (the known weak axis of fiducial recovery, mitigated by multi-region QR search). (iv) Latency: QR search 2,180 ms, quality assessment 20 ms, perspective correction 35 ms per image.

**Baseline comparison.** A learned HOG + linear-SVM recognizer trained on the printed font is compared against the template matcher under the same 28 conditions. On the printed font family both reach 100%; on unseen fonts the two are comparable (SVM 79.7–80.3% vs template 75.4–79.7% confirmed, with the template matcher additionally flagging 10–15% of cells as ambiguous). The differentiator is not raw accuracy but the failure mode: the SVM has no ambiguity mechanism, so its errors are silent, whereas the template matcher routes borderline cells to the reviewer — the property that matters for payroll-adjacent records.

**Comparison with general OCR.** Against a general OCR engine (Tesseract, single-character mode) on the same digit test set, the template matcher wins on the deployment-relevant regime — the system's own printed template font — with 100% vs 84–87% accuracy, because the templates match the exact printed glyphs. On unseen fonts Tesseract generalizes better (94–95% vs 86–90%), which is outside the printed-form scope and motivates future integration of a general OCR for handwriting. In all cases only the template matcher emits an ambiguity channel, so its uncertain cells are routed to review rather than silently misread.

**Similarity retrieval.** The read-only retrieval module (character-bigram + word cosine over form records) is evaluated on a synthetic corpus of 200 records across five templates, with relevance defined as sharing the template key (the reviewer's notion of a "similar past form"). Mean precision is 1.00@1, 0.99@3, 0.975@5, and 0.95@10, confirming that the module surfaces the intended same-template references without injecting them into records.

**End-to-end whole-form evaluation.** Synthetic filled forms (10 digit cells with random printed fonts + 10 OMR boxes) pass the full pipeline (QR classification → ArUco perspective correction → field cropping → per-cell recognition). Cell-level accuracy is 97.5% clean, 96.5–98.0% under blur/noise/brightness/tilt, with 4.5–8.5% of digit cells routed to human review (not silently wrong); OMR accuracy is 94–100%. Under 3° rotation the form-correction success drops to 60% and accuracy to 57.5%/60.0%, consistent with the fiducial recovery's known rotation sensitivity.

**LLM/RAG assistance.** Auto-Decte treats trust as the primary acceptance criterion for model-assisted document workflows, and accordingly designs the AI layer for correctness before efficiency. The deployed release enforces three guarantees, each covered by the acceptance suite: (i) the workflow remains correct end-to-end with the model disabled (AI-off path); (ii) every suggestion is stored separately from confirmed values and can never mutate a fact; and (iii) retrieval results are strictly read-only references. The retrieval module is also validated quantitatively, surfacing same-template references at 1.00 precision@1 and 0.95 precision@10. On this trust foundation, measuring the assistant's downstream efficiency — reviewer time, error-catch rate, and suggestion acceptance — is the natural next evaluation step in the planned field pilot.

## 10. Limitations and Future Work

Honest scope limits: general handwritten digit-string / Chinese text / signature OCR is not implemented (only single-cell template digits and OMR); deployment is single-machine without a completed multi-user capacity test or field pilot; the evaluation lacks a 30–50-form golden set with double entry and real plant images, so accuracy claims are limited to controlled benchmarks; and the LLM suggestion module has functional correctness but no measured end-to-end efficiency gain. Future work: general OCR integration, independent task workers, external storage, a quantitative LLM-assistance study (reviewer time, error-catch rate, suggestion acceptance rate), and a field pilot measuring financial-processing time reduction.

## 11. Conclusion

Auto-Decte demonstrates a trust-first integration of an LLM adapter and similarity retrieval into an industrial document workflow: recognition and the model produce candidates and references, while humans remain the only source of facts, with full traceability from photograph to exported cell. The system is deployed as a working baseline at a bamboo-processing plant and provides the substrate for a future quantitative field study.

## Appendix: benchmark scripts and artifacts

- Repo: `lhh666-6/auto-decte` (branch `modular-architecture`); acceptance report `docs/acceptance-report.md`.
- Benchmark harness under `benchmarks/` (digit/OMR/template/latency) with `benchmarks/report.md`, `report_template.md`, `results.json`, `results_template.json`.
