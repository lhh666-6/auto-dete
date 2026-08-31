# Pilot-3 preflight lock

Pilot-3 is the first eligible full Pilot after the OpenAI MCP path-boundary repair. Pilot-1 is a
completed but cross-provider-unqualified historical Pilot; Pilot-2 is an aborted harness run whose
relative data path opened an unintended empty database. Neither may be changed or resumed.

This preflight binds the repaired benchmark source, implementation source, four configs, complete
112-run plan, zero-retry policy, and unique absent output root:

`evidence/agent-authority-benchmark-v2/pilot/2026-08-31-pilot-3`

Every live command must include this launch lock and `--max-new-invocations 1`. The first command
omits `--resume`; every later command uses it. Any source, config, plan, output-root, or resume-state
drift must fail before the live runner and before a provider call.
