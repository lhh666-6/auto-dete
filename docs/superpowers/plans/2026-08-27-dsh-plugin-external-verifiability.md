# R19 DSH Plugin Integration Implementation Plan

**Design:** `docs/superpowers/specs/2026-08-27-dsh-plugin-external-verifiability-design.md`  
**Workspace:** `revisions/2026-08-27-jss-r19-dsh/`  
**Constraint:** Preserve R17/G10 and R18; all new executions are non-overwriting.

1. Record R18-to-R19 baseline counts, hashes, and source/evidence verification state.
2. Acquire and hash the immutable DSH `dsh-v0.1.1-rc.2` source at `b150a551b`.
3. RED: add tests for an AI-suggestion candidate use case with parent lineage, immutable JSON
   evidence, candidate-only persistence, and rollback.
4. GREEN/refactor: implement the minimal use case, evidence type, candidate-only repository method,
   and facade without adding a fact-write capability.
5. RED/GREEN: implement a versioned one-shot Python JSON bridge with model-visible `propose` and
   `verify`, plus host-only setup/confirm/export operations.
6. RED/GREEN: implement the TypeScript Cordis plugin with exactly two tools, strict subprocess
   handling, stable errors, package metadata, and no confirmation surface.
7. Build the plugin and run unit/package tests against the frozen DSH dependency graph.
8. Build a real pinned Loader/ToolRuntime driver and execute D1--D10 into a fresh run directory.
9. Validate equal negative-case database digests, clean offline verification, exact one-byte
   mutation detection, source/config/lock hashes, receipt, and non-self-referential manifest.
10. Normalize one R19 paper input and update the claim--evidence ledger.
11. Verify and add the DSH convergence preprint and official pinned architecture source; update
    related work, protocol, results, discussion, appendix, and artifact documentation only if all
    D1--D10 pass.
12. Rebuild LaTeX, close citations, run code-paper/artifact-coherence/reproducibility and
    pre-submission gates, fix all scientific/technical Critical/Major issues, then assemble a new
    non-overwriting R19 release candidate.
