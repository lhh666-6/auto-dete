# ESWA submission package

- `main_anonymous.tex`: author-redacted technical review source; add verified author metadata for ESWA's single-anonymized submission
- `title_page.tex`: separate author/title metadata with explicit placeholders
- `supplementary.tex`: reproducibility and detailed-results supplement
- `highlights.txt`, `cover_letter.md`, `figure_captions.txt`: submission files
- `figures/vector`: editable author-controlled TikZ diagrams
- `figures/generated`, `tables/generated`, `artifacts`: hash-verified experiment outputs
- `reviews`: citation, claim, code/paper, and readiness audits

Build from this directory with `latexmk main_anonymous.tex` and `latexmk supplementary.tex`. The local `.latexmkrc` writes intermediate files to `out/` and copies final PDFs beside their sources.
