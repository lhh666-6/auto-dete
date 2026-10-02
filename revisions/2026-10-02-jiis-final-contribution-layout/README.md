# JIIS final submission: contribution and layout revision

This is the current author-prepared JIIS submission package. It combines the contribution-focused revision, pagination fixes, and horizontal/vertical centering requested on October 2, 2026. It does not indicate journal submission or acceptance.

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

The preceding layout revision changes three table-placement options from [t] to [!htbp], keeps C1--C3 together on page 2, and relocates the unchanged mechanism-comparison paragraph after that list. It removes the large blank areas previously on pages 10 and 12 and decreases the manuscript from 25 to 24 pages.

This round centers the unchanged smallcondensed block on A4: left/right margins are both 44.0217 mm; top/bottom margins are both 44.6648 mm when the running head is included. Text width, height, fonts, content and all 24 page breaks remain unchanged. Character-by-character and graphical-edge comparison verifies a uniform translation on every page. Short last pages retain their natural whitespace; the fixed block, not each page's visible ink, is centered. The predecessor is commit c6472bd92f786d6a8cb66304d4d89a4830c4151c.

For compatibility, the complete delivery ZIP retains its previous filename but now contains the centered version. The Chinese upload instructions and verification receipt describe the current geometry.

The main sources were independently rebuilt in an empty directory using TeX Live 2025 and latexmk. The final log has no undefined references/citations, duplicate labels or Overfull boxes. Four inherited Underfull vbox warnings remain; all 24 newly rendered pages were visually inspected. The supplement PDF and all supplement sources are byte-identical to the preceding independently built and inspected version.

## Compile

In submission-files/Manuscript-LaTeX:

    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

In submission-files/Online-Resource-LaTeX:

    latexmk -pdf -interaction=nonstopmode -halt-on-error ESM_1.tex

The frozen experiment and implementation commits referenced by the paper are unchanged. The root REVIEWER_GUIDE.md remains the route to those deposited results.

Before journal upload, authors must confirm approval, affiliations, declarations and the absence of simultaneous consideration elsewhere.
