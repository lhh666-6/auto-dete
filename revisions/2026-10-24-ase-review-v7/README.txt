ASE review revision v7 — 24 October 2026

Build all PDFs with Python 3 and a pdfLaTeX/BibTeX installation:
    python build.py
Build the 28-page manuscript only:
    python build.py --main-only
Auxiliary files are written under out/ in each source directory.
The sn-jnl class, bibliography style and all cited entries are supplied.

This revision completes the final-review reproducibility fixes: it restores two
promised analysis scripts, clarifies the relation to Guarded Commits and the scope
of concrete admission, and distinguishes historical and supplementary bootstrap
readbacks. Existing observations, mathematical definitions, figures and experimental
archives' original members are preserved. No new model calls were made.

Recovery and scientific-statistics readback: see REPRODUCE-RECOVERY.md.
The three qa/recovery_*.py scripts and qa/scientific_statistics.py use only the
standard library and the two pinned archives listed there. qa/feedback_strata.py
uses the supplied pairs.csv. Run with --output to preserve the distributed tables.

Figure-generation code, measured source data, original glyph assets and author
specifications are in scripts/figures/. requirements-figures.txt records the
dependencies; rebuilding figures is optional and is not needed to compile the PDF.
The supplied figure PDFs are unchanged; do not overwrite them merely to compile.

Each of the following separate study archives includes a portable standard-library
entry point, verify_offline.py, full raw per-cell records and REPRODUCE-V4.md.
Read START-HERE.md first; it distinguishes the current route from historical notes:
  Correction-consumption-reproduction.zip          504 cells / 444 matches
  Agno-entrypoint-reproduction.zip                 54 cells /  42 matches
  Reviewed-instance-substitution-reproduction.zip  16 cells /  12 matches
These are distinct constructed collections, not independent pooled samples.
Run the verifier after extraction. The historical collectors require separately
configured SDK environments; offline readback does not imply portable recollection.
Original freezes, scores and mismatches are preserved.

Other supplied archives retain their existing experiment-specific guides:
X1-X2-reproduction.zip, Native-contract-reproduction.zip,
Feedback-sensitivity-reproduction.zip and Dynamic-recovery-reproduction.zip.
SOURCE-MANIFEST.json inventories this source package. EXTERNAL-INPUTS.json links
the sibling reproduction archives by hash and retains historical evidence references.
The external historical datasets are not embedded in this manuscript-source ZIP.
