# JSS LaTeX verification — RC4 final-rerun inputs

Date: 2026-08-26 (Asia/Shanghai)

- Source: `source/main.tex` from `paper-new-all`.
- Inputs: `paper-from-new-all/paper_inputs/`, the final RC4 correctness plus
  performance aggregation.
- Chain: `pdflatex → bibtex → pdflatex → pdflatex → pdflatex`.
- Result: PASS; 35 pages, PDF SHA-256
  `93e8cb07f754288671a40adffdd0226f47c00e02860c56adc7b8bd5d348fa28a`.
- Final log: 0 fatal errors, 0 undefined citations/references, 0 LaTeX/package
  warnings, 0 overfull boxes, and one benign Underfull table-row advisory in
  `tables/generated/validation_evidence.tex`.
- Placeholder scan: 0 TODO/FIXME/XXX/TBD/[INSERT/PLACEHOLDER/Lorem ipsum.
- Citation coverage: 36 cited keys, 36 active entries, 0 missing, 0 unused.
- PDF text contains 0 unresolved `??` markers.
- Regenerated timing claims: admission p50 16.573–185.532 ms; reverse-trace
  p50 5.327–7,857.313 ms; maximum p95 8,046.960 ms; storage bytes unchanged.
- The paper-input manifest and lineage hashes in `artifact_appendix.tex` match
  the final `paper-from-new-all` records.
- All three submitted figures remain independently constructed editable vectors;
  `ai_concept_consumed` is false and SVGs contain no raster image payload.

The local `latexmk`/`latexindent` launchers require an unavailable Perl runtime.
The explicit MiKTeX chain is the recorded fallback. The installed shared
`verify_outputs.py` helper is absent; RC4 manifests and the clean-build manifest
provide hash-and-existence verification.
