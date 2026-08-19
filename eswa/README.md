# ESWA submission package

- `main_anonymous.tex`: author-redacted manuscript source; keep identifying author metadata in the separate title page during anonymized review
- `title_page.tex`: separate finalized author/title metadata, funding, competing-interest statement, and CRediT roles
- `supplementary.tex`: reproducibility and detailed-results supplement
- `highlights.txt`, `cover_letter.md`, `figure_captions.txt`: submission files
- `figures/vector`: editable author-controlled TikZ diagrams
- `figures/generated`, `tables/generated`, `artifacts`: hash-verified experiment outputs
- `reviews`: citation, claim, code/paper, and readiness audits

Build from this directory with `latexmk main_anonymous.tex` and `latexmk supplementary.tex`. The local `.latexmkrc` writes intermediate files to `out/` and copies final PDFs beside their sources.
