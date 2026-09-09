# R21 Figure Structural Redesign

**Date:** 2026-09-04

**Target:** Journal of Systems and Software, 183 mm double-column figures

**Status:** Design approved in conversation; implementation awaits author review of this written specification

## 1. Goal and invariant

Redesign the four main-paper figures so that they form one visual argument for the revised novelty:

\[
\text{persisted AI candidate}
\rightarrow
\text{candidate-bound human authorization}
\rightarrow
\text{explicit authorized value}
\rightarrow
\text{atomic complete successor}
\rightarrow
\text{total field-source attribution}.
\]

The redesign may change layout, hierarchy, visual encoding, annotations, and captions. It must not change an experimental value, denominator, confidence interval, formal outcome, test count, or inference boundary. The frozen evidence bundles remain immutable.

## 2. Shared visual system

- Canvas: 183 mm double-column width; height chosen per figure and kept below the journal limit.
- Typography: Arial/Helvetica/Liberation Sans; 8 pt base, 7 pt ticks, no text below 5 pt at final size.
- Semantic colors:
  - blue `#2166AC`: AI candidate, reference, or baseline;
  - purple `#762A83`: human authorization and explicit authorized value;
  - orange `#F1A340`: trusted admission transaction or secondary comparison;
  - green `#1B7837`: committed authoritative successor and verified trace;
  - red `#B2182B`: rejection, failed predicate, or inference ceiling only;
  - grey/black: neutral context and text.
- Critical distinctions also use shape, line style, labels, or spatial separation; color is never the sole encoding.
- Submission assets: editable SVG, vector PDF master, and 300 dpi PNG preview.
- All figures are generated deterministically from textual contracts or frozen machine-readable inputs. The internal AI ideation raster remains excluded from submission inputs.

## 3. Figure contracts

### Figure 1 — Correction-aware admission boundary

**Core conclusion:** An AI proposal becomes authoritative only through candidate-bound human authorization and a complete trusted admission transaction; Correction retains \(x_c\) while committing a distinct \(x_a\).

**Archetype:** schematic-led process diagram.

**Reading order:**

1. Persisted candidate certificate: identity, record/field context, evidence, \(x_c\), expected pre-version.
2. Human decision:
   - Accept: \(x_a=x_c\);
   - Correction: \(x_a\neq x_c\), candidate retained;
   - Reject: no admission attempt.
3. Trusted admission predicate: candidate/context, dual-value attribution, freshness, batch completeness, total source relation, and principal policy.
4. One record-version compare-and-swap.
5. Either atomic commit of the complete successor, source map, authorization, transitions, and audit event, or rejection with authoritative-state stutter.
6. Reverse trace from each authoritative field to the exact authorization, candidate certificate, and evidence.

The Correction branch is the hero element. Machine-side components must remain visibly unable to write authoritative facts. A footer retains the boundary that authorization records responsibility, not factual truth.

### Figure 2 — Contribution-to-evidence map

**Core conclusion:** Distinct evidence layers support distinct parts of C2--C4, and each layer has an explicit inference ceiling.

**Archetype:** schematic-led evidence map.

**Structure:** contribution bands above five evidence cards:

| Contribution | Evidence card | Frozen facts | Permitted inference | Ceiling |
|---|---|---|---|---|
| C2 | Bounded relational model | 66/66 declared outcomes in S1/S2 | witnesses and no bounded counterexample for encoded assertions | not an unbounded proof |
| C3 | Projection adapter | 9 intended SAT; 20 mapping mutants UNSAT | selected persisted executions bind to exact formal instances | not total refinement |
| C3 | Independent concrete catalogue | 35/35 declared cases; 354 Python tests | declared legal, rejected, tamper, rollback, and conformance cases | finite declared catalogue |
| C3 | Frozen performance evidence | 2,000 admission pairs; 7,200 trace observations | cost on the frozen Windows/Python/SQLite grid | not asymptotic or platform-general |
| C4 | Repeated live-agent evidence | 1,260 planned; 320/335 benign completion; 0/899 unauthorized mutation; 93 runtime failures reported separately | descriptive behavioral variation with scenario-bounded authority invariance | not provider ranking or global security proof |

The current linear arrows are removed because they suggest that one evidence type derives from another. Grouping and braces instead show which contribution each independent layer supports.

### Figure 3 — Cost characterization

**Core conclusion:** Admission latency, incremental admission cost, reverse-trace cost, and lineage storage are different cost dimensions and must be interpreted separately.

**Archetype:** asymmetric mixed-modality; four non-redundant panels.

- **(a) Absolute admission latency:** full and lower p50 across all ten total/changed-field cells.
- **(b) Paired incremental latency:** paired mean delta with 95% CI on a zero-centered axis; retain and directly mark both negative cells.
- **(c) Reverse-trace latency:** all 36 p50 cells in the existing 4-by-9 matrix, with direct millisecond labels and log-color encoding. This is the hero panel.
- **(d) Storage scaling:** full, lower, and incremental main-database size for 1k, 10k, and 100k transitions on a labeled log axis.

Splitting the current panel (a) removes the misleading shared axis for absolute p50 values and paired differences. All 10/36/3 frozen cells and 9,200 timing observations remain represented.

### Figure 4 — Behavioral variation, authority invariance

**Core conclusion:** Agent-mediated behavior varies across the three configurations, while the trusted admission mechanism produced no observed unauthorized authoritative mutation in the declared challenge set.

**Archetype:** asymmetric quantitative composite.

- **(a) Behavioral variation:** horizontal grouped dot plot for benign completion, context recognition, recovery, and stale recognition. D1, G1, and G2 use distinct colors and marker shapes; exact count/evaluable-\(N\) labels remain visible. The panel is descriptive and does not rank providers.
- **(b) Authority invariance:** lollipop/interval display of the one-sided 95% zero-event upper bounds for D1, G1, G2, and pooled data on an approximately 0--1.1% scale. Direct labels state the observed counts (0/299, 0/300, 0/300, and 0/899).

Runtime failures (76/420, 4/420, and 13/420) remain separate from endpoint denominators and are stated in the caption rather than encoded as successful behavior.

## 4. Data and generation architecture

The paper-local generator becomes the only submission-figure build entry point:

```text
frozen cost_summary.json -------------------+
                                             +--> paper/scripts/build_figures.py
frozen statistical_analysis.json -----------+        |
                                                      +--> four SVG/PDF/PNG sets
                                                      +--> figure-build-manifest.json
```

Implementation rules:

- Extend `paper/scripts/build_figures.py`; do not edit the frozen Final bundle or its reporting output.
- Add an `--agent-stats-input` argument pointing to the staged `statistical_analysis.json`.
- Validate exact schema, configuration IDs, denominators, counts, runtime failures, and zero-event bounds before rendering Figure 4.
- Preserve the Academic Figure Skill asset-confirmation header and verbatim typography, palette, and export baselines.
- Record both source hashes and every output hash in a versioned figure-build manifest.
- Keep `ai_concept_consumed: false`.
- Extend `paper/scripts/test_build_figures.py` to enforce all four output triplets, editable SVG text, absence of SVG raster payloads, PDF signatures, frozen cost-grid invariants, and frozen live-agent values.

## 5. Manuscript synchronization

Update only text that must change to describe the redesigned visual encoding:

- `paper/sections/03-problem-contract.tex`: Figure 1 caption.
- `paper/sections/08-results.tex`: Figures 2--4 captions and nearby references where the old panel structure is named.
- `paper/reviews/figure-provenance.md`: construction, input hashes, commands, output hashes, and QA status for all four figures.
- `paper/reviews/claim-evidence-ledger.md`: Figure 4 source trace if the existing row no longer describes the paper-local rendering path.
- `paper/README.md`: deterministic rebuild command with both inputs.

No result prose may be changed merely to fit a visual. If a proposed graphic cannot represent a claim faithfully, the graphic changes.

## 6. QA and acceptance criteria

The redesign is accepted only if all of the following pass:

- [ ] Figure 1 visibly distinguishes \(x_c\) from \(x_a\) and shows Accept, Correction, and Reject.
- [ ] Figure 1 shows complete commit versus authoritative-state stutter without implying that authorization establishes truth.
- [ ] Figure 2 contains all five evidence layers, including repeated live-agent evidence, with distinct inference ceilings.
- [ ] Figure 3 separates absolute latency from paired deltas and includes every 10/36/3 frozen cell.
- [ ] Figure 4 makes behavioral variation visible and uses the correct zero-event upper-bound scale.
- [ ] All manuscript-visible counts, denominators, intervals, and runtime failures match frozen JSON inputs exactly.
- [ ] All four SVGs contain editable text and no embedded raster image; all PDFs are vector-only where applicable.
- [ ] Fonts are embedded; no text falls below 5 pt at final size.
- [ ] Original-size, manuscript-size, grayscale, and color-accessibility inspections pass.
- [ ] No clipping, label collision, legend occlusion, or unexplained statistical encoding remains.
- [ ] Figure tests pass and repeated builds are deterministic at the data/semantic level.
- [ ] The full LaTeX manuscript compiles with no errors, undefined references/citations, or overfull boxes.
- [ ] A dated Academic Figure Skill QA report records AP-0--AP-7, CL-1--CL-7, VI-1--VI-7, and VV-1--VV-5 outcomes.

## 7. Out of scope

- Changing experimental data, statistical definitions, or formal outcomes.
- Re-running the live-agent benchmark or performance experiment.
- Editing frozen evidence or manuscript-input bundles.
- Redesigning LaTeX tables in this pass.
- Adding decorative icons, screenshots, or generated raster artwork to submission figures.
