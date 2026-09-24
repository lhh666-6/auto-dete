# Figure quality and source checks

The four main-text figures were exported as PDF, SVG, and 300 dpi PNG. The PNG previews were inspected for clipping and overlap, and each PDF has one page. Figure captions identify the AI assistance and rendering version. These figures are ordinary manuscript figures, not a graphical abstract.

## Figure 1 — Same value, different history

- **Question answered:** Can identical final values conceal a different reviewed-candidate identity? Yes; the two constructed paths end at quantity 101 while their candidate links differ.
- **Semantic check:** The field-source pointer targets a transition (`t1` or `t2`), which traces to the candidate. The figure does not make the candidate the direct field source. The substituted path represents the context-only control; candidate-bound admission rejects that path.
- **Data basis:** Conceptual construction drawn from the declared equal-valued candidate-substitution case. It is not a plot of experimental frequencies. Statistics report: not applicable.
- **Export check:** 183 mm design width; PDF, SVG, and 300 dpi PNG produced. PDF has one page with embedded TrueType fonts and extractable text. PNG was inspected visually for clipping, legibility, and label overlap.
- **Reuse boundary:** The explanatory values 90, 100, and 101 are the manuscript's constructed example. The figure does not imply a measured attack rate or field prevalence.

## Figure 2 — Correction-aware admission relation

- **Question answered:** How does an exact persisted candidate become a complete, attributable successor when a reviewer corrects its proposed value?
- **Semantic check:** Candidate $c_1$ proposes 100 and authorization $a_1$ explicitly permits 101. Quantity gets the new source transition $t_1$; unchanged fields retain prior source transitions. The pre-state is checked before one atomic commit.
- **Data basis:** Conceptual illustration of the specified relation; no experiment frequencies are plotted.
- **Export check:** Vector PDF and SVG plus PNG preview; labels and arrows were visually inspected.

## Figure 3 — Candidate-binding comparison

- **Question answered:** Which measured behaviors separate the context-only event journal from the exact journal and transactional reference?
- **Data basis:** All three rows of `../data/e1-comparison.csv`, copied byte-for-byte from Git commit `2645e5e18c900ea91c9c980e44195dc71e410432` with hash in `../data/SOURCE-MANIFEST.json`.
- **Numeric check:** Every mechanism has 165 scored cases and 45 legal admissions. Context-only has 15 instance-policy violations and 60 ambiguous field-level candidate answers; both exactly bound mechanisms have zero of each. Counts represent constructed executions and answers, not population rates.
- **Reproduction:** Run `python build_fig3.py` from this directory; source-row and denominator checks are built into the script. No source rows are omitted.
- **Export check:** PDF, SVG, and PNG produced and the PNG inspected visually.

## Figure 4 — Trace access cost

- **Question answered:** Under the same verifier and returned object, how do bulk retrieval and point lookups compare across the measured trace grid?
- **Data basis:** All 72 rows (36 paired cells) of `../data/e3-trace-summary.csv`, copied byte-for-byte from the same deposited Git commit and listed in the source manifest.
- **Numeric check:** Each arm has 200 measured traces in every cell; all 36 point-lookup medians exceed their paired bulk medians. The labelled 128-field, 100-version, 1,000-record cell has medians 170.24 and 509.09 ms. The plot uses medians from the deposited summary, not generated or interpolated observations.
- **Reproduction:** Run `python build_fig4.py` from this directory; grid, pair, denominator, and labelled-value checks are built into the script.
- **Export check:** PDF, SVG, and PNG produced and the PNG inspected visually.
