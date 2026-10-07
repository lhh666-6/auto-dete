# AI disclosure correction

Date: 2026-10-07. Baseline: published review-closure commit `c66bab68f4e143c738e47e3c5d976add756c7ddc`, saved locally under `qa/before-ai-disclosure/`.

The author stated that Claude was not used and requested a balanced, concise disclosure. Only the paragraph under **AI-assisted preparation** changes in the manuscript source. It now reads:

> DeepSeek and OpenAI tools, including Codex, were used to assist with code development, analysis checks, literature organization, figure preparation, and manuscript drafting and revision. The authors retain full responsibility for the research design, interpretation of the results, and the accuracy and integrity of the final manuscript.

The wording identifies the tools, the assistance categories and author responsibility without retaining a detailed history of manuscript reconstruction or an earlier diagram prototype. The final figures continue to have explicit plotting scripts; no figure, result or scientific claim changes in this pass. The statement does not assert that assistance was limited to copyediting or that every generated output has already been independently reviewed.

## Editorial basis

The [KAIS submission guidelines](https://link.springer.com/journal/10115/submission-guidelines) were checked for their LLM-use and accountability guidance. Relevant declarations were also inspected in [Text2AMR2FRED](https://link.springer.com/article/10.1007/s10115-025-02631-y), [SAR](https://link.springer.com/article/10.1007/s10115-025-02485-4), and [the prompting paper](https://link.springer.com/article/10.1007/s10115-024-02326-w). These examples did not provide a directly comparable AI-assisted-preparation template. The 51-word wording is an editorial synthesis of the actual assistance and author responsibility; it is not a claim that KAIS imposes a 50-word rule or that the inspected articles establish a uniform disclosure convention. Journal approval or final compliance is not certified by this text edit.

## Verification

- Every source character outside the AI-assisted-preparation paragraph remains unchanged.
- The supplement source and PDF remain byte-identical to the baseline.
- All 154 packaged evidence, baseline and figure files remain byte-identical, including the regenerated evidence-verification receipt.
- All 29 evidence checks pass. The article retains 12 pages, three main figures, three tables and 20 references; the supplement retains 29 pages.
- Existing MiKTeX compiles the main article in three successful passes. No undefined citation/reference warnings, overfull boxes or missing characters are present. The built-in compiler remains unavailable because it cannot locate its standard directories.
- Main pages 1–10 have exactly identical extracted text and 72-dpi pixel renders to the baseline. Only pages 11–12 change; both were rendered at 144 dpi and visually inspected. The declaration is complete, and all 20 bibliography entries remain present without clipped text or overlaps.
- `QA-RECEIPT.json`, `FINAL-POLISH-VERIFICATION.md` and `FINAL-POLISH-PDF-QA.md` record the current source/PDF hashes and distinguish this authorized declaration exception from the preceding preservation audit.

No additional model calls, data collection, rescoring changes or experiments were introduced. The editable archive is regenerated with this note and verified by CRC and member SHA-256 checks.
