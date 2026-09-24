# Local LaTeX build

*manuscript.md* is the prose source for this DKE working draft. *build_latex.py* converts its paragraphs, formulas, tables, figure captions, links, and five verified citation links to *manuscript.tex* without rewriting the research text. The LaTeX file uses the locally installed Elsevier elsarticle class with the journal set to *Data & Knowledge Engineering*. The four vector PDF figures are read from the figures directory. Bibliographic metadata is in *references.bib*.

From this directory in PowerShell:

    python build_latex.py
    New-Item -ItemType Directory -Force -Path out | Out-Null
    pdflatex -interaction=nonstopmode -halt-on-error -output-directory=out manuscript.tex
    bibtex out/manuscript
    pdflatex -interaction=nonstopmode -halt-on-error -output-directory=out manuscript.tex
    pdflatex -interaction=nonstopmode -halt-on-error -output-directory=out manuscript.tex
    Copy-Item -LiteralPath out/manuscript.pdf -Destination manuscript.pdf -Force

The checked build used local MiKTeX 25.12 and elsarticle 3.5. It produced a 16-page PDF with four figures, two tables, and a five-entry reference list. The final log had no LaTeX errors, unresolved references, or box warnings. The five bibliographic entries were checked against publisher, university, author, arXiv, or W3C source pages. Author names and submission metadata remain to be supplied for a journal-ready version.

The .latexmkrc is included for installations with Perl. On this machine, latexmk could not start because its Perl script engine was absent, so the PDF was compiled directly by the installed pdflatex.
