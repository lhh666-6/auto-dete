# ASE manuscript source and submission files

Updated 21 October 2026. This is the compressed revision after multi-perspective review of **The Review–Execution Gap in Agentic Software: Specification, Design Space, and Empirical Characterization**.

## Current files

| File | Purpose |
|---|---|
| `main-submission.pdf` | Current manuscript PDF |
| `main.pdf` | Standard source-build destination; the older local preview is currently held open and is not the submission PDF |
| `Online-Resource-1.pdf` | Original evidence and collection ledgers, with corrected navigation and S12.6 archived recovery example |
| `Online-Resource-2.pdf` | Addendum A1–A11, including the clarified trusted-storage prerequisite and implementation/recovery matrix |
| `ASE-manuscript-sources.zip` | Sources for the manuscript and both supplements, figure assets, readback scripts and source manifest |
| `X1-X2-reproduction.zip` | Unchanged deterministic experiment sources and saved evidence; follow its own `REPRODUCE.md` |
| `cover-letter.md` | Cover letter matching the current contribution and cost boundaries |
| `SOURCE-MANIFEST.json` | Local source/PDF hashes and separately identified external evidence hashes |

The upload-ready directory is `submission-ase-2026-10-21/`. Upload `Manuscript-sources.zip` in the Manuscript field; it has one main.tex and only the main paper dependencies. Upload the two Online Resource PDFs and `X1-X2-reproduction.zip` separately as Supplementary material. `Manuscript.pdf` is the reference preview; `Cover-letter.txt` is for the cover-letter field if requested. Follow `UPLOAD-GUIDE.md`. No combined submission ZIP is provided. Historical preview PDFs with other suffixes are not current submission files.

## Revision scope

The manuscript retains its binding-choice and conditional recovery-measurement focus. The revision adds contrasting responsibility design examples, an obligation-level positioning table, explicit agent/human cost boundaries, and an archived recovery-and-confirmation example. Formal navigation is synchronized with OR2 A9; OR2 A10 separates validity and recovery channels from reversibility. These are explanations and readbacks of existing evidence, not new experiments or deployment results. Raw archives, scores, denominators and reported empirical values are unchanged. The subsequent review refinement places the immediate deterministic-authorization and available-candidate conditions next to the abstract recovery result, concentrates the diagnostic contribution beside Table 3, and names instance-rule conformance directly inside Figure 4.

The subsequent prose compression removes repeated framing and table replay while preserving all figures, tables, definitions, core formal arguments, empirical values and limitations. The final format pass adds the Table 1 callout, fits all four figures to the text width, and removes caption-ending punctuation. It changes no scientific claim, evidence or experiment. Earlier combined bundles are historical snapshots and should not be uploaded.

## Build all three documents

Requirements: Python 3 and a pdfLaTeX/BibTeX installation with the packages in the preambles. From the extracted source directory:

```text
python build.py
```

For only the main manuscript or only the supplements:

```text
python build.py --main-only
python build.py --supplements-only
```

Intermediate files remain in each project's `out/`. The complete source ZIP includes both supplement source trees and their figure assets; the three documents can be compiled without downloading experimental records. The current PDFs supplied separately are the reference outputs. PDF metadata can vary across builds.

## Offline recovery verification

See `REPRODUCE-RECOVERY.md` for the exact two archive downloads, required path mapping, checksums, Python-only commands and expected outputs. Supply the two ZIP files directly; a complete checkout, collection-status JSON and X2 raw files are unnecessary for this readback. Use `--output` to preserve the distributed tables. `qa/recovery_example.py` checks the exact events and state hashes cited in OR1 S12.6.

The 32 delivered pairs span 16 task definitions. The separate batch labels are retained: original A has one pair, original B sixteen, and supplementary A fifteen. The 24 reuse and eight fresh-authorization routes are observations under an immediate deterministic reviewer, not measurements of human approval cost.

## Figures and evidence

The included PDFs are sufficient for compilation. Optional regeneration uses `python scripts/figures/build_all_figures.py` and requires Matplotlib plus the assets included with these scripts. The source readback data are `scripts/figures/figure-data.json`; its broader source list belongs to the original extraction, whereas the recovery script validates only its two necessary archives. Figure 4 shows observed minima–maxima, not confidence intervals, and labels I as instance-rule conformance. Figure glyph provenance remains in the AI declaration and included assets.

`tables/recovery-cost-episodes.csv` and `tables/recovery-cost-source.json` document the recovery decomposition. `tables/recovery-example-source.json` records the anchored example. The experimental archives are external to the manuscript-source ZIP; their hashes are retained in the manifest and recovery guide. New hosted runs require provider access, but none of the offline checks here makes model calls.
