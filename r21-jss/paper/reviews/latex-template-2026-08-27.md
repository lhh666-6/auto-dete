# LaTeX template compliance — R18

**Project:** JSS R18 manuscript  
**Path:** `revisions/2026-08-26-jss-r18/paper`  
**Date:** 2026-08-27  
**Mode:** report-only

## Result

Template comparison is **blocked informationally** because the configured working-paper
template could not be located on this host. No preamble or bibliography-system change was
applied. The manuscript uses the JSS `elsarticle` class with natbib-compatible
`elsarticle-harv`, which is a legitimate venue-specific setup and must not be replaced by a
generic `article` or `biblatex` configuration.

## Checks

| Block | Status | Finding |
|---|---|---|
| Template source | Not available | Neither `templates/latex-wp/your-template.sty` plus bibliography companion nor legacy `settings.tex` was found under the configured user/task-management paths. |
| Document class | Keep | `elsarticle[preprint,12pt,authoryear]` matches the stated JSS target. |
| Bibliography | Keep | `elsarticle-harv` with `\bibliography{filtered}` is venue-compatible; no system migration was attempted. |
| Packages and commands | Keep pending template | `booktabs`, `enumitem`, `graphicx`, `microtype`, `tabularx`, `xcolor`, `hyperref`, and `cleveref` support the current manuscript and figures. |
| Build configuration | Pass | `.latexmkrc` uses `out/`, `pdflatex`, and copies the final PDF beside `main.tex`. |
| Auxiliary checks | Pass | `main.tex` has no stale `settings` input and the bibliography command is internally consistent. |

## Recommendation

Keep the current venue-specific preamble. If the canonical working-paper template becomes
available, rerun the semantic comparison before submission; any conflict requires explicit
author confirmation. LaTeX compilation and warning inspection remain the next gate.

