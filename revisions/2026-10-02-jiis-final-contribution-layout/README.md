# JIIS final submission: contribution and layout revision

This is the current author-prepared JIIS submission package. It combines the contribution-focused revision with the pagination fixes requested on October 2, 2026. It does not indicate journal submission or acceptance.

## Read or upload

- [Main manuscript: 24 pages](submission-files/Manuscript.pdf)
- [Online Resource 1: 14 pages](submission-files/ESM_1.pdf)
- [Main LaTeX source ZIP](submission-files/Manuscript-LaTeX.zip)
- [Supplement LaTeX source ZIP](submission-files/Online-Resource-LaTeX.zip)
- [Complete delivery ZIP](JIIS-final-submission-layout-2026-10-02.zip)
- [Upload instructions in Chinese](submission-files/README-上传说明.md)
- [Cover letter](submission-files/cover-letter.txt)
- [Submission metadata](submission-files/submission-metadata.txt)
- [Contribution and layout revision notes](submission-files/修改说明-zh.md)
- [Machine verification receipt](submission-files/verification.json)

The source ZIPs are flat and contain all required local class, style, figure and bibliography files. The editable folders are also retained under submission-files/Manuscript-LaTeX and submission-files/Online-Resource-LaTeX. Do not upload the outer delivery ZIP as the main LaTeX source archive.

## Scope and evidence

The source baseline is commit e65f760d0f486bbf70114207d969f66e4219abeb, revisions/2026-10-02-jiis-preparation/submission-files. Its original PDF is byte-identical to the PDF supplied by the author. The original preparation folder is not overwritten.

The contribution revision strengthens candidate-bound authorization, the distinction between proposal, authorized value and exact reviewed instance, equal-valued substitution as a policy separator, cross-representation realization, and the E2 presentation boundary. It preserves the formal scope, experimental numbers and limitations.

The layout revision changes three table-placement options from [t] to [!htbp], keeps C1--C3 together on page 2, and relocates the unchanged mechanism-comparison paragraph after that list. It removes the large blank areas previously on pages 10 and 12. The main manuscript decreases from 25 to 24 pages without changing template geometry, text width, text height, font sizes, figures or data. The default smallcondensed block remains left/top positioned on A4.

Both source sets were independently rebuilt in empty directories using TeX Live 2025 and latexmk. The final logs have no undefined references/citations, duplicate labels or Overfull boxes. Four Underfull vbox warnings remain in the main template; all 38 final pages were rendered and visually inspected. The supplementary source is unchanged.

## Compile

In submission-files/Manuscript-LaTeX:

    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

In submission-files/Online-Resource-LaTeX:

    latexmk -pdf -interaction=nonstopmode -halt-on-error ESM_1.tex

The frozen experiment and implementation commits referenced by the paper are unchanged. The root REVIEWER_GUIDE.md remains the route to those deposited results.

Before journal upload, authors must confirm approval, affiliations, declarations and the absence of simultaneous consideration elsewhere.
