# Local LaTeX build

*manuscript.md* is the prose source for this DKE working draft. *build_latex.py* converts its paragraphs, formulas, tables, figure captions, and links to *manuscript.tex* without rewriting the research text. The LaTeX file uses the locally installed Elsevier elsarticle class with the journal set to *Data & Knowledge Engineering*. The four vector PDF figures are read from the figures directory.

From this directory in PowerShell:

    python build_latex.py
    New-Item -ItemType Directory -Force -Path out | Out-Null
    pdflatex -interaction=nonstopmode -halt-on-error -output-directory=out manuscript.tex
    pdflatex -interaction=nonstopmode -halt-on-error -output-directory=out manuscript.tex
    Copy-Item -LiteralPath out/manuscript.pdf -Destination manuscript.pdf -Force

The checked build used local MiKTeX 25.12 and elsarticle 3.5. It produced a 15-page PDF with all four figures and both tables. The final log had no LaTeX errors, unresolved references, or overfull boxes; it reported one underfull table-alignment box. Source references currently remain the clickable links in the working draft. Full journal bibliography preparation is a separate manuscript-editing step.

The .latexmkrc is included for installations with Perl. On this machine, latexmk could not start because its Perl script engine was absent, so the PDF was compiled directly by the installed pdflatex.
