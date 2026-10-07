# Final polish: figure semantic and export QA

Date: 2026-10-07. Verdict: **READY**.

## Scope and actual changes

Only `make_revision_figures.py`, its existing `figures/revised-*` products, and this report were edited or regenerated. No TeX source, data table, follow-up comparison figure or other review report was edited.

**Concept diagram (`revised-figure1-concept`).** Removed the four step numbers and all serial arrows between the role cards. A single review region now groups the authorized correction and reviewed instance under “Review binds value and instance.” The lower band states that review of c₁ authorizes 101 while retaining proposal 100, identifies c₂ as value/context-equivalent but identity-distinct, and states the original-grant policy difference plus the possibility of new authorization for c₂. The visual therefore describes related roles without implying that authorization happens before selection of the reviewed instance.

**Online-design diagram (`revised-figure3-online-loop`).** Added the requested “Executed independently in each arm” label immediately above the feedback/action loop. The two-line label is 7.5 pt; feedback and action cards were shifted slightly to keep the label, connectors and loop distinct. The compact loop denotes the procedure instantiated separately in each isolated policy arm.

The evidence-chain and original-recovery drawing functions (figures 2 and 4) were unchanged. All four original filenames remain available for the manuscript/supplement relocation. The same palette, vector icon system, 172 mm width and 80 mm height are retained.

## Data and provenance verification

The generator completed `validate_sources()` successfully. No empirical values changed:

- Original planned arms: 512.
- B G-bound reuse episodes: 16; original A reauthorization episodes: 1; all 17 have U=1 and I=1.
- Original G ribbon ratio: 16:1.
- N exact-instance transitions per policy: A=3 and B=30.
- N integrity-unknown arms: two, both with unsuccessful utility.
- Formal results: 72 expected-result matches.
- Controlled results: 165 planned/scored cases in each of three mechanisms.
- Historical chain audit: 84 chains.

The online CSV/aggregate, formal-result and controlled-result source hashes remain the same after normalizing path separators. The parent refreshed `evidence/final-number-verification.json` for the finalized prose and 20-reference verification; the new figure audit correctly records its SHA-256 as `c85cc424c45568cffa7beeb7afc5161f463ca5de067874ad142d18e83bce0ac8`. The changed audit hash does not change diagram observations.

## Visual and technical QA

Both edited full-resolution PNGs were opened and visually inspected after regeneration. No clipped or overlapping labels, card collisions, or obscured arrows were found. The review-region grouping is clear, and the arm-independence label is visually adjacent to the repeated loop.

All four PDF masters were checked programmatically:

| Check | Result |
|---|---|
| PDF geometry | PASS: each one-page export is 172 × 80 mm |
| Vector content | PASS: zero embedded raster images in every PDF |
| Font embedding | PASS: all PDF font subsets embedded |
| Editable SVG | PASS: text preserved; zero SVG image elements |
| Figure 1 SVG text elements | 20 |
| Figure 3 SVG text elements | 24 |
| Ordinary label font floor | 7.5 pt |
| Math subscripts | Conventional smaller mathematical glyphs; 6.02/7.14 pt in Figure 1 and 5.95 pt in Figure 3 |
| Canvas bounds | PASS: no extracted words outside any page boundary |
| Export preview | 400 dpi, 2708 × 1259 px |
| Figure 1 semantic labels | PASS: review binding, authorized 101, retained 100, and new authorization text present |
| Figure 3 independence label | PASS: both lines are searchable PDF text |

The current local runtime regenerated all outputs. Earlier PNG files have different byte hashes from these current exports; no claim of byte identity with the pre-polish package is made for figures 2 and 4. Their drawing code and source counts were not changed.

## Deterministic rebuild check

PDF `CreationDate` and `ModDate` and SVG `Date` metadata are disabled. Two successive rebuilds produced identical SHA-256 hashes for all twelve PDF/SVG/PNG outputs, the generator and the source audit. Future citation-verification refreshes may change the source-audit hash, but will not create time-only changes in the figure exports.

Reproduce with:

```text
python make_revision_figures.py
```

## Release SHA-256

| File | SHA-256 |
|---|---|
| `make_revision_figures.py` | `24b40b0a697ad10a4023a03892f50b3c2e8c0bb1897aa7e22e7b8398c7c5f41c` |
| `figures/revised-figure-source-audit.json` | `f609695f2bcaaa59a657b681b043dcdc755035e30cefcd12e215faeeb5a41eb4` |
| `figures/revised-figure1-concept.pdf` | `a11721a73bb6f6e8aa9cf79260c4790a1fdf7cbc9c9729ce903a82c5aff7e7f0` |
| `figures/revised-figure1-concept.png` | `d189987946b62c839d6f84163b386bb87ac2fb1f27bb9f77eabb78aa9654ba2c` |
| `figures/revised-figure1-concept.svg` | `ee2a02c94f1ca8306231429e6182dd6fe2f0946b3faeae29ba44bfe952c2f008` |
| `figures/revised-figure2-evidence-chain.pdf` | `682cfe4b0f55dfacf017e59fe2cd2c2782a9849cf1a84732662506d307187300` |
| `figures/revised-figure2-evidence-chain.png` | `67cd95ac8410baef1f6fbff121ff21d863b747aebcef5f9c87c13f244b9d60c5` |
| `figures/revised-figure2-evidence-chain.svg` | `c36d8b7c8c7bb2616ff52c5732e61d773f943353f545b0c0212421b8f2725dd1` |
| `figures/revised-figure3-online-loop.pdf` | `c1c862acece9181c9ef05f1f98e461f44cd68efb6cae3234c1d3dd4053a634ef` |
| `figures/revised-figure3-online-loop.png` | `3ecadf95ec25ebce5e626a10f22399f785090d706dc1a0de2c88f80383ad5a5b` |
| `figures/revised-figure3-online-loop.svg` | `2b5ba26ded95cd684fb20a9057374099e267f3399a1712ca0795ddc314dcabed` |
| `figures/revised-figure4-recovery-paths.pdf` | `fc2af2859675d88269433a254bdf9078a01843896718f4544f433bcaf4bcf14a` |
| `figures/revised-figure4-recovery-paths.png` | `7497cadaafe834e296648b75ecef9b2160d7819213f761d853109304ff23e93a` |
| `figures/revised-figure4-recovery-paths.svg` | `4f19eb0199e84b3c47860df98e7b6600b4dfc2ba69942c9ac2d8e557b91fecf6` |

No remaining figure correction is required by this review.
