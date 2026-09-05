# LaTeX Compilation and Visual QA Report

## Compilation status

| Field | Value |
|---|---|
| Status | Clean manual natbib chain |
| Source | `jss/main.tex` |
| Engine | pdfTeX 1.40.28 via MiKTeX 25.12 |
| Class | `elsarticle` 3.5 (2026-01-09) |
| Pages | 34 |
| Page size | 612 x 792 pt (US Letter) |
| PDF | `jss/main.pdf` |
| LaTeX/package warnings | 0 |
| Undefined citations | 0 |
| Undefined references | 0 |
| Multiply defined labels | 0 |
| Overfull boxes | 0 |
| Underfull boxes | 1 |

The installed `latexmk.exe` could not start because MiKTeX has no Perl runtime. The equivalent natbib chain defined by the skill—`pdflatex`, `bibtex`, and repeated `pdflatex` passes—completed cleanly. The same missing Perl runtime also made `latexindent` unavailable; this is an environment limitation, not evidence of a source-formatting failure.

## Fixes applied

1. Added `.latexmkrc` with `out/` build isolation and a cross-platform Perl-core PDF copy-back block.
2. Added `lmodern` because T1 Computer Modern bitmap fonts cannot support the enabled `microtype` font expansion.
3. Changed `\code{...}` from raw `\texttt` to `\nolinkurl`, so underscores are legal and long hashes/paths can break without changing their text.
4. Verified DOI `10.1145/1146238.1146251` against Crossref's ACM deposit and synchronized the registered page range 109--120 across the three same-source bibliography files; BibTeX then completed with zero warnings.
5. Replaced natural-width wide-text tables with width-constrained `tabularx` layouts and adjusted the generated numeric admission table using `\footnotesize` plus a local 5.5-pt column separation. No result value or table wording changed.
6. Added width-safety regression tests. Both new tests were observed failing before implementation; the full generator suite now passes 6/6.

The generated evidence digest SHA-256 remained `0d46e319b6c142a160a77cab8a99acef907e0729d60410f54277f12d216fa364` before and after the layout-only regeneration.

## Box report

| Type | Location | Detail | Score impact |
|---|---|---|---:|
| Underfull hbox | `tables/generated/validation_evidence.tex`, line 14 | `Rollback/concurrency` row, badness 10000; visually legible | -1 |

There are no overfull hboxes or vboxes in the final log.

## Source pathologies

All nine detector families passed with zero findings: no spacing-hack conflicts, manual vertical-rhythm surgery, semantic-unit line breaks, forced-float carpet bombing, shrink-to-fit objects, tiny-table hacks, absolute/overlap positioning, fixed-centimetre assumptions, or label-before-caption floats.

`chktex` returned 39 raw advisory findings across seven warning codes. They are dominated by known false positives for Elsevier's `\sep`, correct section-following labels, the deliberate variable name `v_{\mathrm{exp}}`, and explicit author-input placeholders. The LaTeX rubric nevertheless applies its external-tool deduction cap of -10. `latexindent` was skipped as unusable because the installed launcher cannot find Perl.

## Citation audit

| Check | Result |
|---|---:|
| TeX files scanned | 17 |
| Citation commands | 24 |
| Unique cited keys | 36 |
| Entries in active `filtered.bib` | 36 |
| Missing cited keys | 0 |
| Unused active keys | 0 |
| Duplicate active keys | 0 |

The broader 40-entry verified source pool retains four intentionally noncompiled records. Full bibliography findings are in `reviews/bib-validate/2026-08-25-1347-latex.md`.

## Visual inspection

All 34 pages were rendered at 96 dpi and inspected through four full-document contact sheets. The title/abstract, section hierarchy, equations, tables, three figure placeholders, declarations, artifact appendix, references, page numbers, and transitions are present and legible. High-resolution inspection covered the formerly wide Tables 2, 3, 5, and A.8. No clipped text, overlap, blank page, black glyph block, or unreadable table remains.

The three expected placeholders remain pending the next workflow phase:

- admission workflow vector;
- formal--concrete evidence-chain vector;
- fixed-grid cost characterization.

## Quality score

| Metric | Value |
|---|---:|
| **Score** | **88 / 100** |
| **Verdict** | **Revise** |

### Deductions

| # | Issue | Tier | Deduction | Category |
|---|---|---|---:|---|
| 1 | 39 raw `chktex` advisories (cap applied) | Minor pattern | -10 | External tool findings |
| 2 | One visually benign underfull hbox | Minor | -1 | Box report |
| 3 | Three compile/fix iterations were needed before the first clean TeX pass | Minor | -1 | Compile-fix loop |
| | **Total deductions** | | **-12** | |

The `Revise` verdict is expected at this stage because figures and author-only metadata are still deliberately incomplete. It is not a claim of submission readiness.
