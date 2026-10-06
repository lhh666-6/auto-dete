# Phase 2 design package

Status: **DRAFT — not frozen, not executed**. Created 2026-10-06.

- [Phase2-protocol-DRAFT.md](Phase2-protocol-DRAFT.md): full A–N design, definitions, scenarios, online fork/feedback procedure, denominators, analysis and venue assessment.
- [protocol-manifest-DRAFT.json](protocol-manifest-DRAFT.json): 32 unique prospective case parameter sets, scenario/domain balance, planned budgets and unresolved freeze fields. These are planned inputs, not results.
- [tool-definitions-DRAFT.json](tool-definitions-DRAFT.json): seven shared tool schemas. No live tools or runner have been implemented by this design task.
- [trajectory-event.schema.json](trajectory-event.schema.json): Draft 2020-12 logging schema; cross-event invariants will require an independent scorer.
- [design-verification.json](design-verification.json): structural validation and file hashes; zero experimental model calls and zero runs.

Recommended: 32 tasks × 2 configurations × 2 policies = 128 policy arms / 64 pairs. Engineering pilot: 16 additional arms, held out. Prefix calls are prospectively generated and shared inside each pair; both suffixes are online model continuations.

Do not treat this package as an approved protocol, frozen pre-registration, an implemented experiment or an experimental result. Author review and design freeze precede implementation/pilot; main acquisition freeze follows engineering checks. Historical protocols and phase-one artifacts are not modified.
