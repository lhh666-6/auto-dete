# Submission coherence revision — 2026-09-06

Current version: r21-jss-2026-09-06-v6. Current manuscript: paper/main-r21-submission-coherent-2026-09-06.pdf (59 pages).

## Revision scope

- C1–C2 carry the core contract and conditional information requirements; C3–C4 supply implementation, cost, and integration evidence. No new novelty or superiority result is claimed.
- Related work explains the consequences of omitted relations within our model and distinguishes those consequences from empirically demonstrated defects in other systems.
- Highlights, cover letter, availability statements, and reviewer entry points are synchronized. All five highlights are at most 85 characters.
- The narrative-A figures and manuscript organization are included. Figure 1 remains the approved Canva asset.
- The observation witness correction derives effects and commit counts from connected states and checks local source resolution/consistency. Its relationship to full P6 checks remains explicit.
- Frozen experiment records are preserved. Against v5, 18,481 retained evidence files outside the revised witness report and revision manifest have matching SHA-256 digests.

## Verification performed

- 21 acknowledgment-audit and observation-witness tests passed.
- 13 table/figure generation tests passed.
- Six manifest regression tests passed, including two new checks reproduced as failures before the fix. Frozen manuscript-input verification passed.
- A clean manuscript-only directory compiled from source with no prior auxiliary files: 59 pages; extracted text matches the delivered PDF; zero LaTeX warnings, overfull boxes, and underfull boxes.
- 53 cited keys resolve; the bibliography was not expanded.
- The old package contained stale LaTeX auxiliary files; six generated files are removed from this version and ignored for future builds. Revision selection now excludes unshipped installation metadata and runner caches. Experimental receipts are retained; the cache exclusion is covered by regression tests.

PDF SHA-256: 99a78ff88873bb6bedaddcb2c9dbe28c4cf8013ab827720cc2e6a022ee8b5e1d

## Boundaries and outstanding author inputs

Hosted-model, performance, and Alloy experiments were not rerun. The 354 historical Python tests remain a frozen prior result, not a claim about this revision's test count. Independent human acknowledgment annotation remains uncompleted and is disclosed. Submission date, originality/no-concurrent-submission confirmation, final author approval and any required postal details remain author/portal inputs. No submission to the journal has been performed.

The package and revision manifests are regenerated for this version. Earlier tag versions retain the prior source and evidence snapshots.
