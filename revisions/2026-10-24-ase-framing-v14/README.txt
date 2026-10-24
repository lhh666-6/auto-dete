ASE framing revision v14 - 24 October 2026

The Review-Execution Gap in Agentic Software: Approval Scope and Recovery

Build all PDFs with Python 3 and a pdfLaTeX/BibTeX installation:
    python build.py
Build the 29-page manuscript only:
    python build.py --main-only
Auxiliary files are written under out/ in each source directory.
The sn-jnl class, bibliography style and all cited entries are supplied.

This framing revision applies the author's English revision to the abstract, introduction,
related work, Table 2, the Section 6.3 worked example, the opening of Section 7.1 and the
conclusion. It orders the contributions as C1 comparison model, C2 validation of
review-to-execution obligations and C3 the empirical recovery account, places Figure 1 below
the introduction opening, and removes one defensive sentence from Section 7.1. It keeps the v13
layout revision, the v12 reference revision (Cordon and ACG removed, six arXiv preprints), the
v11 AI-assisted preparation statement, the v10 introduction revision and the v9 future-work
subsection, together with all observations, mathematical definitions, figure data, bibliography
and statistical results. Online Resource 1 (31 pages) now documents two archived examples in
S12.6; Online Resource 2 (25 pages) adds the 16-cell accounting clause in A17. The seven
reproduction archives are unchanged. No new model call or experiment was made.

Recovery and scientific-statistics readback: see REPRODUCE-RECOVERY.md.
The three qa/recovery_*.py scripts and qa/scientific_statistics.py use only the
standard library and the two pinned archives listed there. qa/feedback_strata.py
uses the supplied pairs.csv. Run with --output to preserve the distributed tables.

Figure-generation code, measured source data, original glyph assets and author
specifications are in scripts/figures/. requirements-figures.txt records the
dependencies; rebuilding figures is optional and is not needed to compile the PDF.
The supplied figure PDFs are the ones typeset in the manuscript; do not overwrite them merely to compile.

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
