# Current figure design and provenance

The user requested the visual grammar of figures in the **Automated Software
Engineering journal**, without large solid-colour blocks. These are stylistic
references, not evidence for the manuscript's scientific claims or an ASE-wide
mandatory style. They are not added to the bibliography solely for appearance.

## Published figures visually inspected

1. Dakhama et al. (2025), *Enhancing search-based testing with LLMs for finding
   bugs in system simulators*, Figure 1.
   [Publisher figure](https://link.springer.com/article/10.1007/s10515-025-00531-7/figures/1).
   Its grouped pipeline distinguishes input artifacts, processing stages and
   output artifacts. We retain that structural separation, without copying its
   blue gradient fills or artwork.
2. Contreras et al. (2026), *Architecting open, accountable, and trustworthy
   AI-IDEs*, Figure 6.
   [Publisher figure](https://link.springer.com/article/10.1007/s10515-026-00608-x/figures/6).
   It uses activity nodes, decisions, artifact nodes, directed branches and
   numbered steps. We adapt those workflow conventions; the new drawings omit
   decorative icons, shadows and loop artwork.

Both figures were inspected as publisher-hosted images in the browser on
2026-10-21. No source image is embedded in the manuscript or source package.

## Applied style

Figure 1 now uses the card/tag comparison in `FIGURE-STYLE.md`, with actual
generated object glyphs embedded from `assets/fig1-gpt-symbols/`. The author
explicitly requested this replacement after inspecting the pure-vector version.
The generated asset sheet and prompt are archived; labels, numbers and flow
geometry are drawn separately and remain editable. The AI-assisted preparation
subsection discloses these symbols. Figure 1 is now a hybrid asset.
It is included at an explicit 150 mm width (centered on the text block) so its
7.5/8.5-point Arial labels retain their physical sizes. The three candidate
cards share identical geometry; only the changed ID tab is reversed out.
Only results are bold. Muted ochre/slate identify policy headings and gate
outlines, with very pale column bands for grouping. Each of the four paths is
independent; three reach separate state-transition capsules and one stops at
a rejection bar. An initial-state capsule occupies the upper-right area.
The style notes below describe the retained Figures 2–4; their eventual
redesign must preserve direct labels and non-color encodings.

- Figures 2–4: 150-mm vector masters; the manuscript's 31-pica text width scales them to
  about 130.75 mm. Base 8-point text becomes approximately 7 points, and the
  minimum 7-point labels become approximately 6.1 points.
- White node interiors, thin charcoal/warm-grey outlines, orthogonal routing,
  document/record and activity shapes; a small ivory band identifies record
  headers. The user later explicitly replaced the earlier blue/purple/green
  palette with black/white/grey and restrained ivory.
- Dashed and solid paths, explicit labels and letters preserve distinctions in
  grayscale. Colour alone never determines a result.
- No decorative icons, shading, shadows, gradient encoding, overall figure
  titles or invented minimum-cost reference lines.
- Matplotlib baseline inherited from the project's retained figure-generation
  code and academic-figure-skill. Generic scientific plot templates do not fit
  these approval workflows: this is cross-type parameter inheritance, not a
  claim of a native template run.

## Reproduction

`python scripts/figures/build_all_figures.py` validates the saved readback and
produces every active figure as PDF, SVG and 300-dpi PNG. Figure 1's PDF/SVG
embed the saved symbol pixels at their native resolution. Rebuilding uses no network,
model calls or experiment reruns. `figure-data.json` contains all 32 delivered
G pairs, the 15 undelivered original-A slots, all 72 X2 routes, source member
names and hashes. The original and supplementary cohorts remain separate.

In the full research repository, the readback can be independently regenerated
with `reviews/ase-figure-story-2026-10-21/extract_figure_data.py`.
The adjacent data-map report explains each field and exclusion. Conceptual
values 100 and 101 in Figure 1 are an explicit constructed example, not sampled
observations. The nesting in Figure 2 denotes conditional weak inclusion, not
empirical set sizes.

The package's `SOURCE-MANIFEST.json` is the current-file hash authority;
`figures/source-hashes.json` records historical upstream assets and is retained
for the older figure lineage.
