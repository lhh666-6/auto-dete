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
