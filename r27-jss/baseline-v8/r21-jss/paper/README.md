# Current manuscript: submission-coherence revision (2026-09-06)

The current PDF is `main-r21-submission-coherent-2026-09-06.pdf`. Earlier named PDFs are historical snapshots. The latest package is pinned at https://github.com/lhh666-6/auto-dete/tree/r21-jss-2026-09-06-v6/r21-jss.

C1–C2 state the core contract and conditional information requirements; C3–C4 provide realization and evaluation evidence. Highlights, cover letter, availability statements, and the author-input checklist are synchronized. The formal witness correction is included; experimental observations and Figure 1 are unchanged.

# JSS manuscript

This is the evidence-locked Journal of Systems and Software manuscript for the
certificate-bound admission study, packaged in the isolated R21 revision overlay.

## Evidence boundary

Baseline quantitative and pass/fail statements are derived from exactly ten
JSON files under the final RC4 performance/correctness aggregation:

`../evidence/final-rerun-paper/paper_inputs/`

Generate the tables and digest from the `paper/` directory:

```powershell
python scripts/build_evidence_tables.py `
  --input-root ../evidence/final-rerun-paper/paper_inputs `
  --output-root tables/generated
python -m unittest discover -s scripts -p "test_build_evidence_tables.py" -v
```

The generator rejects a missing or extra paper input, checks locked
denominators and environment bindings, hashes every input, and retains all
unfavorable measured cells.

R18 and R19 do not change that baseline input set. They add, respectively,
`../evidence/paper-inputs/ai_origin_lifecycle_summary.json` and
`../evidence/paper-inputs/dsh_plugin_integration_summary.json`, each with a
separate receipt/manifest and claim-ledger entries.

R21 performance extensions add the feature-equivalent materialization summary
and optimized reverse-trace summary under `../evidence/paper-inputs/`. The
repeated live-agent Final is staged separately under
`../evidence/agent-authority-benchmark-v2/manuscript-input/2026-09-03-three-config-10x/`.
Its `MANUSCRIPT_INPUT_STATUS.json` records
`READY_FOR_MANUSCRIPT_INTEGRATION`; the bundle contains all 1,260 normalized
runs, statistical analysis, generated tables and figure, and a manifest tied
to the verified Final root. The post-hoc semantic acknowledgment audit is
retained separately under
`../evidence/agent-authority-benchmark-v2/analysis/2026-09-05-recognition-semantic-audit/`;
it preserves every audited assistant output, the original lexical label, the
semantic label, the coding rule, confusion matrices, and a derived statistics
file used by the manuscript figure and behavior table.

Generate the independently constructed submission figures from `paper/`:

```powershell
python scripts/build_figures.py `
  --cost-input ../evidence/final-rerun-paper/paper_inputs/cost_summary.json `
  --agent-stats-input ../evidence/agent-authority-benchmark-v2/analysis/2026-09-05-recognition-semantic-audit/statistical_analysis_semantic.json `
  --output-root figures
python -m unittest discover -s scripts -p "test_*.py" -v
```

The figure generator does not read the internal AI concept. It exports a
contract-equivalent fallback for Figure 1 and the submitted Figures 2--4 as
editable SVG, vector PDF, and 300 dpi PNG previews, then writes a hash manifest
for both frozen quantitative inputs and every output. The current Figure 1 is
the author-approved Canva design `DAHUNAr-imw`, included from the exact Canva
PDF export at `figures/canva/admission-workflow-canva.pdf`. The matching
`figures/canva/admission-workflow.svg` was converted locally from that PDF.
Both preserve the author-approved layout; Canva rasterized some decorative
layers, so these are hybrid rather than pure-vector exports.

## Build

The manuscript is compiled from the locked baseline, isolated lifecycle,
harness and performance inputs, and the separately verified repeated-agent
Final staging bundle. Where a working Perl
runtime is available, the typical local build is:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Run it from this directory. On the current Windows/MiKTeX host, `latexmk`
cannot start because Perl is absent; the equivalent `pdflatex → bibtex →
pdflatex → pdflatex` chain (repeat until cross-references stabilize) is recorded in the R21 verification summary and
pre-submission report.

The recorded Windows build uses MiKTeX/pdfTeX with `elsarticle`, `natbib`,
`cleveref`, `microtype`, `booktabs`, `tabularx`, `multirow`, `xcolor`, `xurl`,
and Latin Modern fonts. BibTeX uses `elsarticle-harv.bst`. Figure regeneration
uses CPython 3.11 with the NumPy and Matplotlib versions locked by
`../source/implementation/uv.lock`; run it through that frozen environment.
Poppler `pdfinfo`/`pdftoppm` is used only for page-count and visual-QA checks,
not to construct the manuscript.

## Figure policy

The AI-generated ideation raster is intentionally excluded from this reviewer
package because it is not a submission figure. Figures 2--4 are independently
built from verified textual specifications and frozen data. Figure 1 uses the
exact author-approved Canva PDF export; its locally converted SVG is retained
alongside it. The independently constructed pure-vector version under
`figures/vector/` remains a fallback, not the same Canva file.

## Submission-administration status

The manuscript retains the recorded author and declarations. `AUTHOR_INPUT_NEEDED.md` distinguishes author/portal confirmations from optional independent annotation. `COVER_LETTER.md` deliberately retains the submission-date and originality/approval fields for the author to complete. These fields must not be filled using inferred metadata.
