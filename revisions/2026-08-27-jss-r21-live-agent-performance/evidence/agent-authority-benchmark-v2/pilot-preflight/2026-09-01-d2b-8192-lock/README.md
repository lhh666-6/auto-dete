# D2b 8,192-token qualification preflight

This create-only preflight binds the approved post-Pilot amendment to commit `7807b8e`, one D2b
configuration, the exact 28-cell plan, zero automatic retries, and the unique absent output root
`evidence/agent-authority-benchmark-v2/pilot-amendments/2026-09-01-d2b-8192`.

Original D2 and Pilot-3 remain immutable. D2b requests the same `deepseek-v4-pro` model with an
explicit 8,192-token output cap. The first command may create the root once; every later command must
use the locked resume command and advance at most one absent coordinate.

The preflight also binds the approved amendment design and the completed Pilot-3 manifest. Its
verification performs zero provider calls and must report 28 planned executions.
