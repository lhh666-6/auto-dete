# Verification probes

Scripts used for the 2026-09-11 independent reproducibility verification
(see `../REPRODUCIBILITY-VERIFICATION-2026-09-11.md`). Read-only: neither script
writes anything except stdout.

## `verify_rq8_claims.py`

Recomputes the manuscript's RQ8 headline numbers directly from the frozen
normalized run records and prints PASS/FAIL against each reported value. On the
verified revision it reports **23/23 claims reproduced exactly**.

```bash
python -B verify_rq8_claims.py \
  latest/code/figure-work/evidence/agent-authority-benchmark-v2/\
manuscript-input/2026-09-03-three-config-10x/normalized/agent_authority_benchmark_runs.json
```

Two conventions matter when reading the script: the manuscript's `720` / `179`
challenge split is by scenario (`A2`–`A9` vs `A1` + `A10`), and the
`93 runtime failures` are records whose `terminal_class` is one of
`HARNESS_FAILURE`, `MODEL_API_FAILURE`, `TIMEOUT`, `INVALID_OUTPUT` — not
records with a non-null `error_class`, which gives a smaller count.

## `recompute_rq8.py`

Exploratory companion that dumps the composition of the frozen record set
(counts by configuration, scenario, variant, repetition, `terminal_class`, and
the authority-endpoint cross-tabulation). Useful for checking a claim that
`verify_rq8_claims.py` does not already cover.

```bash
python -B recompute_rq8.py <path-to-agent_authority_benchmark_runs.json>
```

Neither script makes a network call or a hosted-model call.
