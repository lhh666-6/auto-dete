# AUTO-DECTE DSH plugin (R19)

This candidate-only plugin targets DeepSeek Harness `dsh-v0.1.1-rc.2` at commit
`b150a551b`. It registers exactly two model-callable tools:

- `auto_decte_propose`: append a parent-linked AI suggestion certificate and immutable JSON evidence.
- `auto_decte_verify`: read and independently hash-check a persisted certificate/evidence binding.

It intentionally exposes no confirmation or fact-write tool. A trusted host may separately invoke the
existing Python `ReviewForms.confirm` use case. Authentication and actor identity remain host
preconditions and are outside the experiment claims.

The bridge is a one-shot JSON process (`python -m app.integrations.dsh_bridge`). Each invocation has a
bounded timeout, bounded output, an explicit protocol version, and a fail-closed nonzero-exit path.
No API key or live model is needed for the deterministic ToolRuntime experiment.

## Reproduce the checks

The exact source identity and hashes are recorded in `SOURCE_PIN.json`. Install
the official workspace from the extracted pinned release with
`corepack pnpm install --frozen-lockfile`, then build its host libraries with
`corepack pnpm run build:lib:host`. The plugin and driver are type-checked from
the pinned workspace because they import its workspace packages.

The Python authority service is prepared independently with:

```powershell
uv sync --frozen --extra dev --extra research
```

Run the experiment into a fresh, non-existing output directory. Never overwrite
the retained run-1, run-2, run-3, final, or tamper-probe directories. Verify the
final evidence offline with:

```powershell
python experiment/verify_receipt.py verify <final-evidence-directory>
```

A successful final directory reports `verified: true`; the retained deliberate
one-byte probe reports `verified: false` and only `receipt.json` as changed.
