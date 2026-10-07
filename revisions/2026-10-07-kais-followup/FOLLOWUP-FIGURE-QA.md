# Supplementary evaluation figure: source and visual QA

Date: 2026-10-07. Verdict: **READY**.

## Deliverables

- `figures/followup-behavior-comparison.pdf`: vector master, exactly 172 × 74 mm.
- `figures/followup-behavior-comparison.svg`: editable labels and vector shapes.
- `figures/followup-behavior-comparison.png`: 600 dpi, 4062 × 1748 pixels.
- `figures/followup-behavior-comparison-pdf-render.png`: independent PDF render used for inspection.
- `figures/followup-figure-source-audit.json`: exact cohort counts, paired observations, source SHA-256 hashes, and scope definitions.
- `make_followup_figure.py`: deterministic source-driven generator. It writes only the new `followup-*` figure products. The four original diagrams remain unchanged.

## Scientific purpose and design

The figure shows that the original B and supplementary A cohorts both reached accountable completion following delivered G-bound feedback, while their observed recovery-path compositions differed. It makes no inferential claim that either deployment prefers a strategy.

Two aligned rows preserve the collection-cohort distinction. Direct labels provide the G exposure denominator, recovery counts, and joint utility/integrity outcome. Within-row bar segment widths encode path fractions. Separate cost annotations provide the mean paired tool-call difference and median paired elapsed-time difference, each with its paired denominator. The supplied manuscript's 172 mm width, 7–9 pt typography and existing pastel vector style are retained.

The design omits an overall cross-model rate. Original deployment A remains in the manuscript's original analysis and is not silently included in the supplementary A row. The main manuscript's cohort table describes full execution coverage; this figure is deliberately restricted to the standardized G handoff behavior.

## Source reconciliation

| Quantity | Original B | Supplementary A |
|---|---:|---:|
| Whole-cohort planned task pairs | 128 | 117 |
| Planned G pairs | 16 | 15 |
| G checkpoint pairs | 16 | 15 |
| Delivered recoverable G-bound mismatch episodes | 16 | 15 |
| Reuse reviewed candidate | 16/16 | 8/15 |
| Reauthorize handoff candidate | 0/16 | 7/15 |
| Bound joint U=1, I=1 | 16/16 | 15/15 |
| Context substitutions, I=0 | 16 | 15 |
| Context task completion | 14/16 | 15/15 |
| Mean paired extra suffix agent calls | +1.000 | +1.600 |
| Median paired extra suffix time | +14.539 s | +14.532 s |
| Paired cost denominator | 16 | 15 |

The original source is `evidence/online/`. The supplementary source is the independently rescored complete export packaged under `evidence/followup/`, copied from `research/phase2-followup-analysis-2026-10-07/outputs/` at the repository root. `analysis-summary.json` must have `collection_status = COMPLETE` before the generator renders. Its G planned/checkpoint/delivered counts must match the figure's CSV-derived counts. All source paths in the final audit are package-relative.

Source mapping:

- `table1-outcomes.csv`: planned G denominators, checkpoint counts, context and bound task completion; cohort planned totals checked independently.
- `table2-continuity.csv`: G-context executed substitutions with `policy_admissible = True`.
- `table3-recovery.csv`: G-bound rows with delivered, recoverable `INSTANCE_MISMATCH` feedback; strategy, U, I, and recovery outcome. Every episode corresponds to a distinct pair.
- `paired-effects.csv`: within-pair `delta_suffix_agent_tool_calls` and `delta_suffix_elapsed_ms`, restricted to every actually exposed G pair, without excluding failed context outcomes.

The original B invariant checks require 16 reuse paths, mean/median +1 call, and median +14.539 s. No simulated observations, interpolation, outcome-based subsampling, or cross-cohort pooling is used. All 31 actually delivered episodes appear in their respective cohort rows; the figure never reports a pooled denominator of 31.

## Statistical documentation

The recovery unit is a delivered G-bound mismatch episode, one per exposed task pair. These are descriptive post-treatment exposure summaries. There are no significance tests, interval bars, or multiple-comparison adjustments in the figure. Broader completion estimates and their intervals belong to the manuscript results table.

The cost direction is bound minus context. Calls are **mean paired differences**; time is the **median of paired differences**, converted from milliseconds to seconds and displayed to two decimals. Time is observed suffix time, not the unsuccessful-run capped time-to-success endpoint. Cost includes the complete suffix; it is not a weighted average of the number of actions after each rejection. The difference matters because supplementary A's +1.60 paired calls need not equal the average of one-action reuse and two-action reauthorization paths.

The original B paired suffix-call differences are 0 in two pairs, 1 in twelve pairs, and 2 in two pairs (mean and median both 1). A claim of exactly one extra full-suffix call in every B pair would be inaccurate. The original B recovery path itself uses one post-rejection commit in every delivered episode; that is a different measurement boundary. This distinction was sent to the manuscript editor during QA.

## QA results

| Check | Result |
|---|---|
| Collection completion and source-count reconciliation | PASS |
| Separate original B and supplementary A denominators | PASS |
| Every exposed G pair represented in cost summaries | PASS |
| Recovery fractions sum to one within each row | PASS |
| All labels lie inside the figure canvas | PASS |
| PDF page geometry | PASS: 171.999999 × 74.000000 mm |
| Vector master | PASS: 15 vector paths, zero embedded raster images |
| PDF fonts | PASS: three embedded DejaVu font subsets; minimum 7 pt |
| Editable SVG | PASS: 27 text elements, zero image elements |
| High-resolution preview | PASS: 4062 × 1748 px; 599.9988 dpi metadata |
| Required labels searchable in PDF | PASS: both cohorts, 8/15, 7/15, 15/15, 16/16 and both time values |
| Rendered visual inspection | PASS: no clipped labels, overlapping text, occluded values or illegible numbers |
| Original four-figure preservation | PASS: generator does not write any original figure path |

The full PNG and an independent 144 dpi PDF render were both inspected. At the final print dimensions, the labels, explicit statistic names, denominator annotations and path shares remain readable. Thin pastel bars have dark outlines and direct count labels so the categories do not depend on hue alone.

The skill's generic eight-stage simulated Sankey asset is incompatible with these observed two-cohort records. This figure therefore inherits the existing manuscript's vector-diagram parameters; no asset simulation is used. The provided 172 mm manuscript width, existing font family and fixed page dimensions intentionally override generic CNS figure dimensions and tight-bounding-box defaults.

## Reproduction

From this revision directory, using the bundled complete supplementary export:

```text
python make_followup_figure.py
```

The explicit equivalent command is:

```text
python make_followup_figure.py --followup-dir evidence/followup
```

## Suggested caption

Recovery paths and execution cost in the original deployment-B cohort and the separately collected supplementary deployment-A cohort. Bound feedback was delivered in 16/16 and 15/15 G pairs, respectively. B reused the reviewed candidate in all 16 episodes; supplementary A reused it in eight and reauthorized the handoff candidate in seven. Every delivered bound episode reached (U,I)=(1,1). Bars show within-cohort path shares. Costs are the mean paired change in suffix agent tool calls and median paired change in observed suffix time (bound minus context), with 16 B and 15 A pairs. Context admitted 16 and 15 substitutions with I=0; its task completion was 14/16 and 15/15, respectively. The cohorts are reported separately.
