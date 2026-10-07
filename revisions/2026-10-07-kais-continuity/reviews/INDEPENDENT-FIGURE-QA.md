# Independent figure visual QA

**Verdict: PASS for all four final diagrams, including manuscript inclusion.** No unresolved visual or semantic figure issues were detected in the reviewed versions.

## Review scope and version

- Design reference: the supplied four-panel image, `image(20261007-023746).png`.
- Reviewed all four `figures/revised-figure*.png` exports at full native resolution, and independently rendered all four vector PDFs at their 172 mm print width (96 dpi screen-equivalent inspection).
- Reviewed the final 13-page `main.pdf`, SHA-256 `88c1eb754e77605d79053d40445cc8a01cb6f2fc55a08e14d05584cc1f4fe1f1`: Figures 1 and 2 on page 2, Figure 3 on page 7, and Figure 4 on page 9. Inspected actual page pixels and PDF text/object geometry, not source code alone.
- Exact PDF/SVG/PNG hashes and sizes are recorded in `reviews/INDEPENDENT-FIGURE-MANIFEST.json` (historical review-stage PDF; final PDF hashes are in `QA-RECEIPT.json`). This approval applies to those files; superseded plain-box exports were not approved.

## Visual findings

All four now use soft differentiated stage zones, original consistent line icons, layered cards, restrained color, deliberate connectors and clear academic hierarchy. Their visual richness is comparable to the supplied reference without copying its unsupported empirical flows. Text, icons, borders and connectors are sharp, aligned and unclipped. Padding and text density are acceptable at final print size.

The integrated figures are full text width, 172 mm, with no reduction from the source PDFs. Ordinary figure labels are at least 7.5 pt in the final manuscript. Mathematical subscripts are conventionally smaller (approximately 5.95–7.14 pt); equation base characters remain legible. All figure PDFs have embedded fonts and zero raster image objects. Captions are adjacent, legible and correctly numbered. No figure/caption/body overlaps were found on pages 2, 7 or 9.

## Semantic checks

1. Figure 1 correctly separates proposal 100, authorization 101, reviewed instance and executed candidate. Its explicit callout says equal proposal value and retained context do not establish equal identity; the original-grant policy difference is clear. The caption identifies this as a conceptual construction.
2. Figure 2 keeps bounded commands, controlled cases, archived chains and prospective arms as distinct evidence units.
3. Figure 3 uses a mechanism/certificate icon and “Host review”, avoiding an implied human participant. Context is G ∧ K_eq; Bound adds I_eq. The shared checkpoint, isolated continuations, actual feedback, next action, observed path and independent U/I oracle remain visible.
4. Figure 4 shows only the two observed G-bound paths: 16 B reuse and 1 A reauthorization, all ending (U,I)=(1,1). Ribbons encode the documented 16:1 counts, with no invented recovery/outcome connections. The N panel separates transition counts from 32-arm outcomes and explicitly retains U=0 with unknown I. These counts were independently cross-checked against the three online CSV tables.

## Fixes verified

- Corrected inclusion scaling from 0.98/0.94 text width to full text width.
- Replaced the ambiguous crossed-arrow reuse icon with a circular reuse symbol and clarified the B-path label.
- Verified the final Figure 2 wrapping, deterministic-host icon in Figure 3, and explicit unknown-integrity outcome in Figure 4.

**Unresolved issues: none within this figure-review scope.** This audit does not claim a full-page review of all manuscript or supplement pages.
