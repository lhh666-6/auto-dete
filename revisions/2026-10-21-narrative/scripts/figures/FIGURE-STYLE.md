# Approved figure style and grayscale encoding

Figures 1–4 now share this style. All are placed at their final 150 mm width using a centered box; Figures 2–4 are no longer reduced to the narrower text width. Regular labels are 7.5 pt and larger headings/emphasis are 8.5 pt.

## Typography and object grammar

- Arial throughout; ordinary labels 7.5 pt.
- Bold 8.5 pt is reserved for the three business-value transitions and the rejection in Figure 1, not for every heading.
- Equal candidate records use the same generated image at 34 × 12.45 mm including the ID tab, with equal live field spacing and label geometry.
- A changed candidate ID uses a charcoal tab with white text.
- Authorization is an uncolored hang-tag referring to the reviewed record. No purple or other color is assigned to human authorization.
- The initial authoritative state uses a capsule with value 90. Each alternative execution has its own diamond check and either an arrow to a separate committed-transition capsule or a stop bar with the rejection label. Candidate cards are row labels, not a flow through both policies.
- Two equal context endpoints remain separate objects. A comparison bracket links them visually; it is not a merge or an execution edge.
- Figure 1 uses 150 × 76 mm at final size. Do not downscale to a single-column width.
- Candidate, grant and state objects now embed actual generated PNG glyphs from `assets/fig1-gpt-symbols/`. Text, numbers, gates, arrows, bracket and rejection stop remain editable vector elements. This is a hybrid image/vector figure, not an all-vector drawing. The asset directory records the generation prompt and provenance; the manuscript discloses the use.

## Color and monochrome readability

- Context heading and gate outline: muted ochre `#8C6847`.
- Instance heading and gate outline: slate blue `#4F6B7A`.
- Other labels and geometry: neutral charcoal `#333333` on white.
- The two accent colors have similar luminance. They are NOT an adequate standalone encoding for lanes, lines, or points.
- Retain the accents for column/lane headings and their check symbols. Every policy lane and every policy-specific point in future figures must also be directly labelled context or instance. Distinct marker shapes may provide an additional cue: circle for context, square for instance.
- Reuse and fresh authorization use filled and open squares respectively, with a full-word local legend. The previous R/F letters are removed to avoid confusion with the R task family. Fill is a recovery-route encoding, not a policy encoding. Cost summaries use diamonds and observed-range segments, not these square route symbols.
- Figure 3 now directly labels both policy lanes; the former dashed/solid policy encoding and its caption description have been replaced together. Shape, text, identical layout and a localized + ID label preserve the difference without color. The dashed vertical separator marks the experimental exposure/measurement boundary, not a policy.
- Very pale bands (`#F6F3F0` and `#F1F3F4`) group Figure 1's policy columns; both become neutral `#F4F4F4` in the monochrome companion. Their role is grouping, not a stronger/weaker or pass/fail encoding. All labels, paths and outcomes remain explicit without color.

## Terminology

Use **context binding**, **instance binding**, and **shared checks** for the two policies and their common requirements. Preserve literal code labels such as `context` / `bound` when identifying archived arms. Examples use plain IDs c1, c2, and a1; formal variables and subscripts retain their mathematical meanings.

## Updated figure responsibilities

- Figure 2 uses pale conditional sets and candidate/grant objects for two alternative recovery routes. New authorization is not a fifth binding level; both routes lead to a new check.
- Figure 3 keeps checkpoint persistence distinct from the fork into isolated arms. The harness changes the submitted identity; the actual agent continuation begins after feedback. A rejected request does not commit, but its lane continues to the agent and independent audit.
- Figure 4 retains all 32 pairs and separate cohorts. Range segments are observed minima/maxima, never confidence intervals. The new recovery-cost table separates calls through recovery, subsequent calls, and complete paired suffixes.
- The existing generated sheet is reused for candidate/grant objects in Figures 2 and 3. It has not been regenerated; the AI preparation statement names these additional uses.

2026-10-21 alignment correction: Figure 3 uses proposal $x_c$ with an Arial mathematical subscript. Figure 4 is 150 x 125 mm, with fixed task columns 01–16 across cohorts; dashes are non-membership in the displayed delivered-pair cohort, not failures.
