> Historical baseline audit for the 44-page version at `cd5bded0`. Current compression and visual checks: [compression-quality-check.md](compression-quality-check.md).

# Final quality check — 2026-09-26

- Main manuscript: 44 pages; supplementary material: 12 pages, Elsevier preprint layout.
- Both PDFs built successfully with the included scripts/Build.ps1 using TeX Live 2025.
- Final logs contain no overfull boxes, unresolved citations/references, or LaTeX/package warnings.
- Source dependency check resolves all labels and all 17 cited bibliography entries; no duplicate labels.
- All 56 pages were rendered. Contact-sheet inspection covered every page; dense tables, equations, and reference pages were checked at enlarged size. A misaligned row in Eq. (18) and a wide Eq. (19) were corrected and re-rendered. No remaining clipping, overlap, or accidental blank page was observed.
- Automated PDF extraction found no words outside the configured page safety boundary. This complements, rather than replaces, visual inspection.
- The E1/E2 result counts and complete current admission/trace grids were cross-checked against recorded data. The independent audit confirms 165 matched comparison pairs, 60 browser cases, 372 rejected attempts, and 22,400 timed observations. These are distinct units, not additive independent trials.
- Recent-neighbor and foundational citations were checked against primary sources, with links and scope in positioning-notes.md. The revision makes no claim to an exhaustive literature search.
- Formal/core, evaluation, and synthesis sections received cross-agent review. Two metadata/interpretation issues were corrected: the historical model-label mapping and the explanation of the old cross-layer JSON equality mismatch.
- Historical experiments were not rerun as part of manuscript preparation. Current experiment records are the fixed September 23 package; new model calls: none.
- This is a complete local manuscript revision for author review. It does not certify coauthor approval or a completed journal submission.

Final PDF identities and build checks are in final-build-check.json; the source/package manifest excludes build intermediates under out/ and itself.

## Author update — 2026-09-27

Added Chen Qile after Xuan Wentao, with the shared Hunan University affiliation confirmed by the user. CRediT roles are Investigation and Validation, based on the supplied description of post-rejection experimental validation. Updated both title author lists and PDF metadata. Rebuilt both PDFs successfully; main remains 44 pages and supplement 12 pages. Visually inspected all six pages whose extracted text changed (main 1/41/42; supplement 1/2/3). No clipping, overlap, or compilation warnings were found. Package hashes were refreshed.
