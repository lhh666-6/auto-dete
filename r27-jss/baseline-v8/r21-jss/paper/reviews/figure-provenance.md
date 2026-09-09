# Figure provenance

## Submission-policy rule

The current paper source uses the exact author-exported Canva PDF for Figure 1
so that the manuscript and the author's editable design `DAHUNAr-imw` are visually identical.
The matching SVG was converted locally from that PDF using `pdftocairo -svg`.
Because the current JSS guide may restrict
generative-AI or AI-assisted image creation or alteration, Figure 1 requires a
final venue-policy provenance decision before submission. Figures 2--4 remain
deterministically generated from approved text contracts and frozen JSON inputs.

| Figure | Submission construction | Editable master | Current status |
|---|---|---|---|
| Figure 1: correction-aware admission | exact PDF export of author-approved Canva design `DAHUNAr-imw`; matching SVG converted locally from that PDF | Canva design `DAHUNAr-imw`; current paper source `figures/canva/admission-workflow-canva.pdf`; delivery SVG `figures/canva/admission-workflow.svg` | rich text reverified 2026-09-04; exact PDF exported and SVG converted 2026-09-05; venue-policy provenance approval pending |
| Figure 2: authoritative-state admission framework and evidence chain | independent three-level vector construction from the C1--C4 contribution chain, frozen evidence definitions, evidence-lineage stages, and inference ceilings | `figures/vector/evidence-chain.svg` | generated, audited, included |
| Figure 3: fixed-grid cost characterization | deterministic rendering of all 10 admission, 36 reverse-trace, and 3 storage cells | `figures/generated/cost-characterization.svg` | generated, audited, included |
| Figure 4: behavior versus authority | deterministic rendering of staged descriptive endpoints and zero-event bounds | `figures/generated/behavior-vs-authority.svg` | generated, audited, included |

## Non-submission visual drafts

- The private ideation raster remains at
  `figures/concept-internal/admission-workflow-internal-concept-r18.png` with
  SHA-256
  `d8ac540bc02cdc12d093c52627e87048c3aac6825175d204e31cb468d9197f40`.
- The author manually corrected the Canva design's scientific notation,
  including `c_i`, `x_a ≠ x_c`, and the `D_*` tokens. Canva API content retrieval
  reverified these strings in design `DAHUNAr-imw` on 2026-09-04. The exact Canva PDF is
  now the Figure 1 manuscript source, with its converted SVG retained beside it. The prior deterministic SVG/PDF/PNG set is
  retained under `figures/vector/admission-workflow.*` as a rollback option.

## Independent submission construction

- Generator for Figures 2--4 and the Figure 1 rollback vector:
  `scripts/build_figures.py`.
- Generator SHA-256:
  `e175b0020a498602e8ef7dc97319226d93fddab8a40cf2e0a1a84c64c2344895`.
- Figure-test SHA-256:
  `2e7d377d7c7b3e68fa8773c66c005dd34ea917d5e850fde1248abcf720c53fba`.
- Cost input SHA-256:
  `705c4e647447d4aea8bf28f15f002d62ea80bee3f15aa4df4dc6ea79fb3fdd3b`.
- Agent-statistics input SHA-256:
  `7121a4dd042122dc6f22c17c9e30cd1036240155634ee416f4647fd4d648e14c`.
- Runtime: CPython 3.11.9, Matplotlib 3.10.8, NumPy 2.3.5.

Build command from `paper/`:

```powershell
python scripts/build_figures.py `
  --cost-input ../evidence/final-rerun-paper/paper_inputs/cost_summary.json `
  --agent-stats-input ../evidence/agent-authority-benchmark-v2/analysis/2026-09-05-recognition-semantic-audit/statistical_analysis_semantic.json `
  --output-root figures
```

The generator records that no production asset is semantically compatible
with its deterministic Figure 1 rollback or Figure 2. Figure 3 inherits only
general line/heatmap parameters, and Figure 4 inherits only marker/spacing
parameters. Its manifest does not cover the Canva-synchronized Figure 1 source.

## Output hashes

| File | SHA-256 |
|---|---|
| `figures/canva/admission-workflow-canva.pdf` | `3176588d384cda5eda805ea444240c7d478cb628f8318d5265afc335efee97a7` |
| `figures/canva/admission-workflow.svg` | `383c20ff2f7ac4333963426c22a596335c3665c444991ec7eb2fc7b6a2ecacfb` |
| `figures/canva/admission-workflow.png` | `982148439228f840080e424381b357f14cb6c2d1a4391ba3f801eeac0d6e1659` |
| `figures/vector/admission-workflow.svg` | `42a417db2a338b2fd7055e4a7fe553403eec36f234061cf1220fd29fc5013b12` |
| `figures/vector/admission-workflow.pdf` | `e7c152153ac5813610b6174de989dc8a790f38c729d6bc3fb15d8a56a564f3b6` |
| `figures/vector/admission-workflow.png` | `1bf03fd87c9b10edad196f8ce703b93ec1ae9af6d80d03300160cc9b4de68eb7` |
| `figures/vector/evidence-chain.svg` | `3b3cd45ca74d1058450f25d4e7ec0e6198141cfbfab05922608fe4887fc0fe59` |
| `figures/vector/evidence-chain.pdf` | `a21878bc1581a2cd2d3bf60113c97bcee5b7511bdd2d848e9e862168736171c4` |
| `figures/vector/evidence-chain.png` | `67f0f7a2a849d21bbb42db88842ab834b95a26b24a4355af9819f93c52e9de30` |
| `figures/generated/cost-characterization.svg` | `febdb953b4954d1ac4ac5666ffcef0f9b276c0d7b4c0679fc2f4bcba57b00d2c` |
| `figures/generated/cost-characterization.pdf` | `88fe77dacaee7a4c23d3df6d586ab91399c0039b7bdd84c4912515438be3de2c` |
| `figures/generated/cost-characterization.png` | `ed7b1338a98fa6f653a32d9c62bb13bb23cce6122b440a45abd699e848e08b96` |
| `figures/generated/behavior-vs-authority.svg` | `0668b33395440e38f34ce993a3086120472cf8b52bc5e75c4637ed642552e9a9` |
| `figures/generated/behavior-vs-authority.pdf` | `dcbfaf1884b654bfd1051839f107a51ea4e0df02bba65863251a4343b8f6b649` |
| `figures/generated/behavior-vs-authority.png` | `ca553bba97164dbb9a1a3e1f204ccfd38f83ecd5117279ec151eb5cc33873cc5` |

The build manifest is `figures/figure-build-manifest.json`, SHA-256
`0e6a9376fe69db4d732830a7de09d0e2a542d1fa6d00bad3807b4b3649c6394f`.

## QA record

- Fourteen paper-generator tests pass: six evidence-table tests, four figure
  tests, and four runtime-table tests. Figure tests enforce both frozen input contracts, exact 10/36/3 and
  1,260/93/320-of-335 totals, the 0-of-720 fixed-challenge and 0-of-179
  capability-unavailable decomposition, the semantically audited 117-of-174
  context and 150-of-151 stale acknowledgment counts, the four-figure semantic structure,
  the deterministic Figure 1 fallback hash, vector PDF output, editable SVG text,
  and absence of SVG raster images in the independently constructed figures.
- Every SVG contains title/description accessibility elements, ARIA linkage,
  editable text, and zero `<image>` elements.
- `pdfimages -list` reports zero raster objects in the four independently
  generated PDFs. The exact Canva Figure 1 PDF is separately documented as a
  hybrid export with 37 image/smask objects.
- `pdffonts` reports embedded Unicode CID TrueType Arial and Arial Bold in all
  four PDFs.
- Original-resolution and manuscript-page previews were inspected after the
  layout cycles. The final workflow has one unobstructed left-to-right success
  channel and two vertical failure channels. The authoritative-state admission
  framework separates its C1--C4 chain, evidence cards, and evidence-lineage /
  inference layer; both figures avoid arrow/text intersections and dark
  rectangle borders.
- Figure 3 separates absolute medians from paired mean differences; Figure 4
  separates behavioral proportions from zero-event upper bounds and reports
  runtime failures outside both panels.
