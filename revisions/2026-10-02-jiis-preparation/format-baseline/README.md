# JIIS complete-content format baseline

This is the complete frozen DKE manuscript migrated to official Springer SVJour3 `smallcondensed`, with no scientific-text edits. The compiled main.pdf has 24 pages including references. It is a reviewable format baseline, not the final submission package.

Open main.pdf to review. Sections, tables, figures, the abstract, and bibliography data are unchanged. See ../format-migration-report.md for preservation checks and remaining layout notes.

Build from this directory using a working TeX installation:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The included .latexmkrc places auxiliary files in out/ and copies the successful PDF beside main.tex. The official class and bibliography style are included. The supplement remains the unchanged DKE baseline in the parent directory; no Springer supplement migration has occurred yet.

Do not submit this development directory as-is. The final submission will need the journal's source-file organization and declarations checks.
