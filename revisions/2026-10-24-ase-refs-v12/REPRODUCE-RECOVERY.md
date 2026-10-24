# Offline recovery readback

This entry point recomputes the manuscript's recovery-call decomposition from existing records and checks the example in Online Resource 1, S12.6. It does not rerun an agent or revise any outcome. Python 3.11+ and its standard library suffice; no API key or installed research package is required.

## Required files

Keep `qa/recovery_costs.py`, `qa/recovery_example.py` and `scripts/figures/figure-data.json` in their source-package layout. Supply exactly two frozen ZIP files under a directory of your choice, called `INPUT_ROOT` below. The ZIPs are read directly; do not extract them for this entry point.

| Archive | Download | Required path relative to INPUT_ROOT |
|---|---|---|
| Original collection | [Pinned original ZIP](https://github.com/lhh666-6/auto-dete/blob/475e66f549613aaaaa62c2ec81ffdee483636c54/cloud-handoff/replication-package.zip) | `revisions/2026-10-07-kais-continuity/replication-package.zip` |
| Complete supplementary A | [Pinned supplementary ZIP](https://github.com/lhh666-6/auto-dete/blob/f5fe7231c5e808ba1629132d222f448bff471204/research/phase2-results-snapshots/2026-10-07-complete/quota-recovery-complete.zip) | `research/phase2-results-snapshots/2026-10-07-complete/quota-recovery-complete.zip` |

Download the raw ZIP from each GitHub file page. The original download is published under `cloud-handoff/`; place those same bytes at the local `revisions/...` path above. This explicit remapping matches the source ledger. The checksums are:

```text
Original:       1bc17338d18f198811e0e58eca9b64bded29f9b01cd61558862455e7e0d469d8
Supplementary:  536f8b7d784d1af118145affd90c3d613b67ad44d9c5b3607b463bcebeacbec1
```

Both hashes are checked automatically before recovery analysis. Only these archives are validated as external inputs: the collection-status and X2 entries in the broader figure-data source list are not dependencies of this recovery readback. The JSON's own hash is recorded in the derived audit. Acquiring the archives requires network access; the commands below are offline.

## Commands

From the extracted manuscript-source directory, replace `INPUT_ROOT` with that directory's actual path:

```text
python qa/recovery_costs.py --repository-root INPUT_ROOT --output recovery-readback
python qa/recovery_example.py --repository-root INPUT_ROOT --output recovery-readback
```

`--output` defaults to `tables/`; specifying a separate directory preserves the distributed tables. The scripts verify saved events and states and write only derived files to the chosen output directory.

Expected checks and results:

- 32 G episodes, 64 recovery-commit before/after state hashes, 24 reuse and eight fresh-authorization routes, all 32 direct through their selected route.
- Original A: one pair, mean suffix call difference 2.00, median time difference 23.671 seconds.
- Original B: 16 pairs, mean call difference 1.00, median time difference 14.539 seconds.
- Supplementary A: 15 pairs, mean call difference 1.60, median time difference 14.532 seconds.
- Example `FORMAL-G-002-B`: one recovery commit, one later receipt query, zero context-side agent calls; the receipt query leaves the state unchanged.

Compare `recovery-decomposition.tex` and `recovery-cost-episodes.csv` with the distributed `tables/` files; compare the scientific fields in `recovery-cost-source.json`. Its source-check list now contains only the two required archives. `recovery-example-source.json` records exact archive-member hashes and example checks.

These numbers condition on delivered feedback in the existing collections. Original A, original B and supplementary A remain separately labelled. Human review and queue waiting were not measured. This entry point does not validate all experiments; use each experiment's archived guide for its own analysis. The supplied `X1-X2-reproduction.zip` has its own independent offline verification route.

## Revision availability audit

Run `python qa/recovery_availability.py --repository-root INPUT_ROOT --output recovery-availability` with the same two ZIP dependencies. Expected: 32 episodes, 13 availability predicates per episode, all true; 24 reuse and eight fresh-authorization routes. The derived CSV aligns all 16 task definitions but preserves A collection labels. This is post-hoc saved-state reconstruction, not new model collection or counterfactual execution.

## Scientific statistics and feedback strata (Online Resource 2, A12–A13)

These two entry points are included in the v7 source package. They use Python 3.11+
and its standard library, with no additional dependency, API key or model call.
Run from the extracted manuscript-source directory and write to a new directory:

```text
python qa/scientific_statistics.py --repository-root INPUT_ROOT --output scientific-readback
python qa/feedback_strata.py --pairs tables/feedback-sensitivity/pairs.csv --output scientific-readback/feedback-strata.json
```

The first command reads the same two pinned ZIPs directly and the supplied tables.
It writes `scientific-statistics.json`, `integrated-recovery-pairs.csv`,
`integrated-n-arms.csv`, `integrated-n-exposed-pairs.csv` and
`integrated-feedback-secondary.csv`. Expected checks include:

- Completion: 128 task clusters, 256 planned policy pairs; original B contrast
  0.015625 with interval [-0.0390625, 0.0703125]. The pooled contrast and every
  bootstrap draw are exactly half the B contrast; this is no independent precision gain.
- Recovery: 32 pairs; supplementary A comprises 15 pairs, mean call difference
  1.60, exploratory 95% interval [0.8666666667, 2.3333333333] (printed as
  [0.87, 2.33] in A12), 10,000 paired resamples, seed 20261023.
- N exposure: 64 cohort/configuration pairs presented and responded to, with
  collection and policy labels retained. These are separate from the 32 G pairs.
- Checkpoints: 128 hash-verified reached events versus 127 retained summary flags;
  neither count asserts that both suffixes started or completed.

Compare the four CSVs with the identically named distributed `tables/` files and
the JSON's scientific fields with the results listed above and in A12–A13.
Runtime and script provenance fields may differ across environments; input hashes
must not differ.
Completion intervals retain the archived seed 20261007; the G intervals are
explicitly exploratory. The historical supplementary call interval [0.93, 2.33]
in Online Resource 1 uses seed 20261007; A12 uses seed 20261023 with the same
ordered pairs, 10,000 draws and percentile estimator. Seed-swap readback reproduces
both intervals, identifying Monte Carlo variation rather than a change to the data
or estimator. Keep the two analyses labelled and do not substitute the historical
value for A12.

The second command needs only the supplied pairs CSV. Compare its JSON contents
with `tables/feedback-sensitivity/strata.json`: four task definitions are reused
across three permission states, giving 12 model pairs. The labels-minus-facts
total-call differences are +2 (valid), +1 (revoked), -3 (unavailable), and 0 overall.
These are descriptive groupings, not an interaction test or 12 independent tasks.
