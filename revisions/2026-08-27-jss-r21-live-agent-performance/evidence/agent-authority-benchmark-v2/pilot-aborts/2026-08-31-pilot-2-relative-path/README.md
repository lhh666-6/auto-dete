# Pilot-2 abort disposition

Pilot-2 stopped after exactly one provider invocation. The run is not evidence of G1 utility:
although the expected initialized database existed, the OpenAI MCP child received a relative data
path and resolved it from the agent workspace, creating a second empty database under
`runs/evidence/...`. The proposal therefore failed with `unknown form`.

The Pilot-2 root is preserved unchanged and must not be resumed. Its run, checkpoint, frozen
configuration, raw trace, expected database, and unintended nested database are all covered by the
external Pilot-root manifest in this directory. No Pilot-2 observation may enter qualification,
resource gating, Final, or the manuscript.

The defect is reproduced by a regression test and fixed at the provider boundary in commit
`1e7b0ac`: every MCP workspace, source, implementation, interpreter, and data path is resolved to an
absolute path before Codex changes working directory. A new Pilot requires a new output root and
preflight lock.
