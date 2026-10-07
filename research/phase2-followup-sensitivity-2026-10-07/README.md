# Exploratory completed-A sensitivity

This is an explicitly **post-hoc sensitivity analysis**, assembled after the separately frozen deployment-A follow-up completed. It does not overwrite the original 512-arm primary results or relabel the sensitivity as prospectively specified.

The analysis routes each original pair identifier to exactly one source: the final terminal follow-up attempt for the 117 A pairs selected by pre-response quota failure; the original attempt for A's other 11 pairs; and the original attempt for all 128 B pairs. Failures in the selected attempts remain. `outputs/pair-source-map.json` identifies every source. Raw input files are never copied over or edited.

The adapter passes these read-only input routes to the unchanged original `export_tables` and paired estimator. Because both deployments are available for each of the original 128 task clusters, the original scenario-stratified paired task bootstrap can be computed mechanically (10,000 draws, seed 20261007). Its interval is conditional on the retrospectively assembled sources and cannot remove selection or collection-period differences.

The derived collection status is `DERIVED_COMPLETE_POSTHOC_VIEW`, so the frozen exporter reports `formal_inference_allowed: false`. This flag prevents confusing the derived view with the completed original collection. The same flag does not prohibit descriptive/exploratory sensitivity reporting under the explicit scope above.

## Reproduce offline

Extract both the original complete replication archive and completed follow-up archive into a separate workspace. Include the independent A-only analysis package next to this directory. With the original pinned dependencies installed, run from the repository root:

```text
python research/phase2-followup-sensitivity-2026-10-07/sensitivity.py --output fresh-sensitivity
```

The output directory must not already exist. No model calls are made. Test the routing safeguards from this directory with `python -m unittest test_sensitivity -q`.

## Verified result

The derived A view completes 123/128 context and 125/128 bound arms; original B completes 117/128 and 119/128. Across the derived paired view, this is 240/256 versus 244/256 and a +1.5625 percentage-point completion difference with percentile interval [-1.171875, 4.296875]. The original primary effect remains +0.78125 percentage points with its original interval; neither is replaced. The two original unknown-integrity N arms remain unknown.

The manuscript reports this sensitivity in the supplement, alongside original results and the separately reported supplementary cohort.
