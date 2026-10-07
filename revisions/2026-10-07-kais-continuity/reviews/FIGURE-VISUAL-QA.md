# Final figure QA

Date: 2026-10-07. Status: **PASS for all four standalone figures.** Artwork frozen for parent manuscript compilation.

## Visual inspection

Every complete final 400 dpi PNG was inspected, and every PDF was independently rendered at 200 dpi and inspected. A separate reviewer also inspected the full PNGs and publication-width PDF renders at 172 mm / 96 dpi. No remaining clipping, overlap, missing glyph, ambiguous connector or insufficient-padding defect was found.

- **Figure 1:** four distinct pastel role panels, original agent/reviewer/review-certificate/gear/database icons, consistent inset detail cards, original proposal 100 and authorization 101, alternate c1/c2 execution rows, and the logical non-implication symbol are clear. This is a motivating construction, not a reported observation.
- **Figure 2:** all five stage headings and evidence-unit insets fit. The final wrapping keeps the problem, contract, formal/transactional, controlled/historical and prospective stages readable. The controlled unit explicitly says 165 cases per mechanism. The footer states the evidence progression without pooling units.
- **Figure 3:** the checkpoint uses a deterministic-host gear and review certificate, not a human. The two isolated gate formulas differ only by I_eq. Actual feedback, the next agent action, the return loop, the observed path and independent (U,I) scoring are visually connected. Planned-ledger retention remains explicit.
- **Figure 4:** only the observed 16 B reuse paths and one A reauthorization path are drawn. The circular reuse icon was simplified after review. Ribbon widths are proportional to 16:1; the terminal label is 17/17 with (U,I)=(1,1). The separate N panel distinguishes transition counts from the 32-arm outcome partition. Both unknown-integrity observations have known U=0. No hypothetical repair taxonomy is portrayed as observed.

## Technical checks

All four PDFs are one-page, **172 × 80 mm**, with no embedded raster images. Their drawings and text remain vector content. All fonts are embedded, subsetted TrueType with Unicode mappings. Text is searchable.

All four SVGs contain editable text and vector shapes, and zero image nodes. The PNG exports are **2708 × 1259 pixels at 400 dpi**.

Ordinary text base sizes are at least **7.5 pt** at the intended 172 mm publication width. Only conventional mathematical subscripts are smaller (lowest PDF span about 5.95 pt in Figure 3); they are parts of base-size mathematical expressions, not body labels. No overall downscaling is required.

Technical audit details: `reviews/figure-review/technical-audit.json`.

Final asset SHA-256 hashes: `reviews/figure-review/final-asset-hashes.json`.

## Source checks

`make_revision_figures.py` ran successfully against the COMPLETE frozen export before final generation. Its assertions check:

- 512 planned policy arms.
- 72 matching bounded formal command outcomes.
- 165 planned and scored cases per controlled mechanism.
- The passing audit of 84 historical correction chains.
- Exactly 17 delivered, recoverable G-bound INSTANCE_MISMATCH episodes, all recovered with U=True and I=1.
- Exactly 16 B commit/reuse-reviewed episodes and one A request_authorization/reauthorization episode.
- Exactly 17 policy-admissible G-context executed substitutions.
- No N substitution and exact N transition counts A=3, B=30 per policy.
- G planned/checkpoint denominators (16 per configuration/policy; one A and sixteen B checkpoints).
- N-B planned/completed/integrity-covered/unknown partition (32/28/31/1 per policy).
- Known U=0 in both N integrity-unknown arms.

Source hashes and figure-generation facts: `figures/revised-figure-source-audit.json`.

The existing frozen reference directory was not modified. This figure task did not edit the manuscript or supplement sources. Final inclusion, caption placement and page flow are checked separately after the parent compiles the paper.
