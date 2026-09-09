# Academic figure QA — R21 final

**Date:** 2026-09-04  
**Scope:** core admission workflow and existing manuscript figures  
**Verdict:** Figures 2--4 are pure-vector ready. Figure 1 now uses the exact
Canva PDF export and has a matching locally converted SVG; final venue-policy
provenance approval remains author-controlled. Canva rasterized some decorative
layers, so the exact export is hybrid rather than pure vector.

## Figure contract

The core figure must separate the untrusted candidate side, the only transaction holding the
fact-admission capability, and authoritative state. It must show persisted evidence/candidate,
exact binding checks, expected-version CAS, one atomic successor, complete source-map evolution,
whole-batch rejection/stutter, and reverse lineage. Color must be redundant with labels, borders,
and arrows. The submitted artifact must be editable vector artwork constructed independently
from verified semantics.

## Asset Confirmation Table

| Candidate asset | Native type | Match to contract | Decision |
|---|---|---|---|
| `figures/concept-internal/admission-workflow-internal-concept-r18.png` | AI raster | Ideation only; contains the required trust-boundary and accept/correction concepts | Exclude from submission and generator inputs |
| `figures/canva/admission-workflow-canva.pdf` | Exact Canva PDF export of author-approved design `DAHUNAr-imw` | Exact layout; embedded fonts plus Canva-rasterized decorative layers | Current LaTeX source |
| `figures/canva/admission-workflow.svg` | SVG converted from the exact Canva PDF export | Visual match verified at 2603 × 1208; 199 paths and 37 embedded image layers | Delivery SVG; hybrid vector/raster |
| `figures/canva/admission-workflow.png` | Earlier author-approved Canva rendering | Exact visual match after removing six pixels of interface chrome | Retain as historical raster fallback |
| `figures/vector/admission-workflow.svg` | Editable SVG | Deterministic semantic match; no raster payload | Retain as rollback master |
| `figures/vector/admission-workflow.pdf` | Vector PDF | LaTeX-compatible export of the rollback SVG | Retain as submission-policy fallback |
| `figures/vector/admission-workflow.png` | 300-dpi preview | Preview of the rollback vector | Do not use as the current LaTeX source |
| Existing evidence-chain and cost figures | SVG/PDF/PNG sets | Different figure contracts | Retain unchanged |

## QA gates

| Gate | Result | Evidence |
|---|---|---|
| AP — asset/provenance | PASS | AI concept has explicit internal-only banner/watermark and is not consumed by `scripts/build_figures.py`; manifest records `ai_concept_consumed=false`. |
| CL — content/layout | PASS | Original-resolution preview has readable hierarchy, no clipping/overlap, explicit capability boundary, and label/arrow redundancy. |
| VI — vector integrity | WARN | The exact Canva PDF embeds fonts and vector objects but also 37 raster/smask image layers; the converted SVG contains 199 paths and 37 embedded image elements. The independent fallback remains the pure-vector option. |
| VV — visual/venue verification | PASS | The exact Canva export has no clipping, overlap, or color-only critical distinction; the converted SVG render matches the approved layout. |

## Regression evidence

- Fourteen figure/evidence/runtime generator tests pass.
- `pdfimages -list` reports zero image objects in the core PDF.
- `pdffonts` reports embedded Unicode CID TrueType Arial/Arial Bold.
- Current independently reconstructed fallback hashes:
  - SVG: `42a417db2a338b2fd7055e4a7fe553403eec36f234061cf1220fd29fc5013b12`
  - PDF: `e7c152153ac5813610b6174de989dc8a790f38c729d6bc3fb15d8a56a564f3b6`
  - PNG preview: `1bf03fd87c9b10edad196f8ce703b93ec1ae9af6d80d03300160cc9b4de68eb7`

The AI concept was generated first for ideation and remains excluded. The current manuscript
uses the exact author-exported Canva PDF rather than claiming that the independently reconstructed
fallback is the same file. The matching SVG was produced locally with `pdftocairo -svg` and
visually verified. If a venue requires zero embedded raster objects, use the independently
constructed pure-vector fallback rather than mischaracterizing the Canva export.
