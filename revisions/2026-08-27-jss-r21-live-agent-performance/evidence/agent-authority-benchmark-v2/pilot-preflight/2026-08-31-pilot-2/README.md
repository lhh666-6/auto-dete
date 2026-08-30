# Pilot-2 preflight lock

This directory binds the repaired, quota-aware Pilot-2 inputs before the first provider call. The
actual output root is deliberately absent until execution begins:

`evidence/agent-authority-benchmark-v2/pilot/2026-08-31-pilot-2`

The first command must omit `--resume`; every later command must use `--resume`. Every command uses
`--max-new-invocations 1` and the frozen zero-retry policy. A successful incomplete command creates
one new terminal run plus one checkpoint and no normalized or qualification artifacts.

No Final work is authorized from this preflight lock. Final still requires completed Pilot-2
qualification, both provider families, a passing pre-result resource gate, and a separately
verified Final freeze.
