# Final continuation policy design

## Decision

The R3 Final benchmark keeps its frozen source, coordinates, schedule, zero-retry rule, and append-only terminal evidence. Only the external continuation controller changes. A valid terminal is never rerun.

## Continue conditions

After a runner invocation creates exactly one new terminal and exits successfully, the controller records the terminal and continues regardless of `terminal_class`. This includes `HARNESS_FAILURE`, `TIMEOUT`, `TOOL_RUNTIME_FAILURE`, ordinary `MODEL_API_FAILURE`, `INVALID_OUTPUT`, `PASS_SAFE_BUT_UTILITY_FAILED`, and `PASS_UTILITY_SAFE`. These outcomes remain in their predeclared denominators.

## Hard-stop conditions

The controller stops immediately only when:

1. `unauthorized_authoritative_mutation` or `mechanism_authority_violation` is true;
2. the runner exits nonzero;
3. an invocation does not create exactly one new terminal;
4. the R3 freeze fails verification; or
5. a terminal provides explicit evidence of exhausted provider credit or quota.

Quota exhaustion is an operational pause, not a benchmark exclusion. The five-hour heartbeat checks the same output root and verified R3 freeze, waits while quota is unavailable, and resumes with at most one new invocation after quota recovery. It never reruns a terminal.

## Transition

The currently active controller remains untouched until it exits or reaches a safe between-invocation boundary. The next controller uses this policy from the latest immutable checkpoint. Existing control roots and all stopped terminals remain unchanged.

## Verification

Before launch, tests must demonstrate that ordinary failure classes continue, authority violations stop, structural runner failures stop, and quota exhaustion produces a resumable pause. Launch requires a passing R3 freeze verification, a unique latest checkpoint, and no competing benchmark process.
