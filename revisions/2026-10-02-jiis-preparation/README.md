# Latest JIIS manuscript and submission sources

Updated 2 October 2026. Research content is frozen; this revision changes journal framing, format, disclosures, diagram spacing, and submission packaging. It introduces no new experiment or scientific result.

## Use these files for submission

- [Latest manuscript PDF — 25 pages](submission-files/Manuscript.pdf)
- [Complete manuscript LaTeX source](submission-files/Manuscript-LaTeX/), entry point [main.tex](submission-files/Manuscript-LaTeX/main.tex)
- [Online Resource 1 — 14 pages](submission-files/ESM_1.pdf)
- [Supplementary LaTeX source](submission-files/Online-Resource-LaTeX/), entry point [ESM_1.tex](submission-files/Online-Resource-LaTeX/ESM_1.tex)
- [Cover letter](submission-files/cover-letter.txt)
- [Title, abstract, and keywords](submission-files/submission-metadata.txt)
- [Upload instructions in Chinese](submission-files/README-上传说明.md)

The abstract is 207 words and has six keywords. Upload all files from `Manuscript-LaTeX`, not only `main.tex`; the source set is internally flat. The supplementary source is a separate compilation target. Check the submission platform's generated PDF before submitting. Do not upload this README, audit reports, or historical preparation snapshots as manuscript files.

## Audit and preservation records

- [Final limited submission audit](reviews/pre-submission-report/2026-10-02-final.md)
- [Mechanical verification results](final-audit.json)
- [Submission file SHA256 manifest](submission-files-manifest.json)
- [Final outputs SHA256 manifest](final-outputs-manifest.json)
- [Reference metadata/access audit](reviews/bib-validate/2026-10-02.md)
- [Diagram verification](figure-qa-report.md)
- [Transition and writing decisions](transition-plan.md)

The contract, conditional proposition, RQ wording, table results, and frozen raw data were preserved. The original 32-page DKE manuscript remains in [the preceding revision](../2026-09-26-dke-manuscript/). `format-baseline/` records the untouched 24-page Springer migration; **it is not the final manuscript**. `final-source/` retains the organized editorial sources; use the flattened submission sources above for upload. The audit reports are dated snapshots, and their statements about publication/upload status describe the audit time.

## Compile locally

With a working TeX installation, run these commands inside `submission-files/Manuscript-LaTeX/`:

```text
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Compile `ESM_1.tex` separately inside `submission-files/Online-Resource-LaTeX/` with two `pdflatex` passes. Journal style files, bibliography, and vector figures are included. `main.bbl` is also supplied. No hosted AI call or experiment is required to compile either paper.

Experimental reproduction remains documented in the paper's pinned artifact links and [the repository reproduction entry point](../../reproduction/dke/). This editorial revision does not create a new dataset or rerun the experiments.
