# Budget runner implementation notes

The study runs only inside this directory. No production API request was made during implementation. Offline provider fixtures write real request/response artifacts and execute the original host, action loop, audit, and scorer.

## Interfaces and artifacts

Use the absolute Python 3.11 interpreter with `-B`:

```powershell
& 'C:\Users\lenovo\AppData\Local\Programs\Python\Python311\python.exe' -B 'D:\Claude_Design\auto-decte-paper\research\kais-budget-sensitivity-2026-10-14\run.py' prepare
```

The commands are `prepare`, `preflight`, `freeze`, `verify`, `live`, `status`, and `pause`. `live --resume` continues a previously paused run. A global stop cannot be bypassed by the resume flag. The root coordinator performs final preflight, freeze, and live launch.

`allocation.json` contains 24 task blocks and 96 flat `cells` in collection order. Each cell has `task_id`/`task_instance_id`, `scenario`, `condition`, `policy`, `budget`, `max_tokens`, `sequence_index`, `position`, `block_order`, `path`, `prefix_path`, and `source_prefix`. Sampling completes in scenario order E/G/L/N/R/V before sequence allocation; each scenario uses every Williams sequence once. Task blocks are then shuffled using the same seeded RNG.

The immutable prefix is copied in full to `live/<task>/<low|high>/prefix`. Its dates, old deployment metadata, event hashes, and protocol identity remain unchanged. Suffixes reside under the sibling `context` and `bound` directories. Primary scores are original `score.json` outputs. Supplemental `terminal.json` stores the cell, terminal/preserved-incomplete status, error, global-stop decision, and a manifest of all arm artifacts. It permits validation and skipping without repeating calls.

`provider-raw/<step>-<attempt>/` retains `prompt.txt`, `request-body.json`, the exact `request-body.raw.json` bytes passed by the original transport, `request-metadata.json`, original `response.json` bytes, duplicate `response-body.bin`, and `response-metadata.json` with stop reason, returned model, usage, and raw SHA256. No request headers or decrypted credential are written. Errors preserve the original diagnostic bytes and a code-only classification. Mock tests use a sentinel secret and verify it appears in no output file.

## Isolation and preserved semantics

`vendor/src/phase2/` copies `__init__.py`, `kernel.py`, `providers.py`, `runner.py`, `oracle.py`, and `trajectories.py`. The three original frozen-design files are copied beneath `vendor/frozen-design/`, preserving the kernel's ROOT calculation.

Only two lines of the vendored runner differ from the source: suffix wall time uses config `suffix_seconds` (21600) and each request uses `request_timeout_seconds` (1800). Defaults retain the source runner's behavior. `validate_run` and the entire `score_run` tail are byte-for-byte identical as decoded source text; every other vendored Python file is byte-identical. The 20 suffix response iterations, 24-tool guard, 2/8-second transient retries, and one format repair across the full inherited conversation remain the source implementation.

The thin initializer reproduces the original N/G/E/V events, with R semantics supplied by the unchanged kernel. During initialization only, `kernel.utc` is fixed to the checkpoint's latest grant issuance. The log's separate UTC function remains real. All online host actions restore the real clock. `config.id` remains B, keeping budget labels out of visible decision IDs. `inputs/initial-input-equivalence.json` records all 96 first-message hashes and verifies same-policy request bodies differ only in max_tokens. New arms verify their first messages against this frozen record before calling a provider.

New events use the SHA256 of this study's PROTOCOL.md. Current configs have expected model identity only; old availability probe timestamps and actual returned identifiers are removed. The actual current model is recorded from each response. The original encrypted credential_file reference remains in the config; the credential is read only by the original live transport.

## Recovery, stopping, and freezing

Collection holds one OS file lock. Completed arms verify their full artifact manifest and recomputed score before being skipped. A termination event without score can be scored without a model request. The existing safe boundary retains a cached response; an additional recovery shim closes the narrower gap where raw response bytes or a response event were persisted before the boundary update. The shim only reconstructs response/feedback bookkeeping and never executes a tool. Any intervening semantic event remains fail-closed in the original loop.

An initialized arm with no boundary is preserved without rerunning initialization or G handoff. If interruption preceded the very first event, the unchanged scorer cannot score it; supplemental terminal metadata therefore records U/I as unknown and creates no fabricated score.json. Semantic interruption, auditing failure, malformed provider envelope, HTTP 400/401/402/403/404, model identity drift, credentials unavailable, and quota/balance/model-unavailable diagnostics trigger a global stop. Budget and invalid-output outcomes remain valid terminal records and collection proceeds.

`pause` stops at the next request boundary. An in-flight HTTP request may finish first; its bytes are retained. Keyboard interruption also retains the current boundary. `live --resume` clears the explicit pause marker, validates the frozen inputs, and continues. A pause consumes elapsed wall-clock time, consistently with the original runner's resume accounting.

`prepare` is offline. `preflight` runs both runner and analysis test suites, records output, then snapshots all required code/protocol/config/allocation/input/vendor/prefix and protection manifest hashes. `freeze` refuses stale or failed preflight. `live` verifies the master freeze before collection, each cell, and each real provider request. The copied prefixes are included in that freeze. Source prefix/core hashes are checked at collection start and end; the root coordinator independently checks the broader original-file protection manifest. PLAN.md and output artifacts are explicitly excluded from the freeze. No freeze was created by the implementation subagent.

## Test evidence

`test-run-red*.log` and `test-run-green*.log` preserve observed red/green cycles. The final runner suite has 20 offline tests covering balanced/reproducible allocation, all 96 initial inputs, exact wire budgets, retained provider bytes, secret exclusion, six scenario semantics, unchanged scorer/core, inherited repair, 20-response limits, three transport attempts and waits, source initialization interruption, raw-response recovery, semantic interruption, termination without score, no repeated terminal requests, pause/resume/global stop, process locking, and freeze tampering.

The independent analysis suite also executes the real vendored scorer on a runner-generated G/bound fixture. Offline fixture outcomes are engineering checks and are not study observations.
