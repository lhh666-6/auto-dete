# R19 DSH Plugin External-Verifiability Integration Design

**Date:** 2026-08-27  
**Status:** Approved for autonomous implementation  
**User decision:** Minimal DSH plugin, Option A thin adapter; no further approval pauses required  
**Target article:** AUTO-DECTE JSS revision derived from R18 without modifying sealed R17/G10 outputs

## 1. Purpose and bounded claim

The R19 addition tests whether AUTO-DECTE can be mounted beside a real agent harness as an
external authoritative-record boundary. It does not turn AUTO-DECTE into an agent harness and
does not reproduce the authority contract in TypeScript.

The strongest permitted result is:

> At one pinned DeepSeek Harness revision, a loaded third-party plugin can transport an
> agent-origin candidate into the existing AUTO-DECTE candidate path; the model-facing plugin
> surface cannot confirm facts; a separate host-side decision can Accept or Correct the candidate
> through the existing Python/SQLite admission transaction; stale, tampered, unavailable-bridge,
> and unauthorized-confirmation cases fail without authoritative partial effect; and exported
> receipts remain verifiable after the DSH runtime is gone.

The experiment does not support model-accuracy, usability, user-productivity, industrial-effect,
universal-harness-portability, or unbounded security claims.

## 2. Frozen external baseline

- DeepSeek Harness release: `dsh-v0.1.1-rc.2`.
- Commit: `b150a551b`.
- Selection rationale: this is the immutable DSH revision examined by the 2026 architectural
  convergence preprint, so the implementation and literature comparison share one source state.
- DSH is a developer preview. All plugin APIs, package-lock bytes, Node/pnpm versions, profile
  configuration, and executed commands must be recorded in run metadata.
- A newer DSH revision may be discussed but must not be substituted after the experiment begins.

## 3. Alternatives considered

### 3.1 Dedicated model-callable candidate tool — selected

The plugin registers an explicit candidate-proposal tool and a read-only receipt-verification
tool. There is no model-callable confirmation function. Candidate writes and fact writes remain
different capabilities.

### 3.2 Observe every `tools/result` event — rejected

Automatic result capture would require heuristics to identify candidate-bearing outputs and map
arbitrary JSON into record fields. It would make the denominator and failure semantics unclear.

### 3.3 Gate every tool in `tools/pre-execute` — rejected

The DSH pre-execute seam governs tool permission, not authoritative business facts. It also lets a
listener execute before returning an approval decision, so side-effectful bridge calls at that seam
would confuse consent UI with the external authority contract.

## 4. Architecture

```text
Pinned DSH/Cordis runtime
  └─ AUTO-DECTE plugin (TypeScript; candidate + read-only tools only)
       └─ one-shot JSON request over stdin/stdout
            └─ Python bridge CLI
                 ├─ AI-suggestion candidate use case
                 ├─ existing candidate-only database facade
                 ├─ existing ReviewForms host-only confirmation
                 ├─ existing SQLite repository/CAS transaction
                 └─ receipt + manifest exporter

Offline verifier ── reads receipt/manifests/files directly; no DSH process required
```

The TypeScript package owns protocol conversion, process lifecycle, timeouts, stdout parsing, and
model-facing error normalization. It never opens SQLite, creates certificates, accepts reviewer
identity from model arguments, or computes an authoritative transition.

The Python bridge owns schema validation and application composition. The `propose` and `verify`
operations are available to the plugin. `host-confirm` is a separate CLI entry used only by the
experiment driver and is not listed in the DSH tool registry.

## 5. Components and ownership

### 5.1 `dsh-plugin-auto-decte`

- TypeScript Cordis plugin loaded through the real frozen DSH profile.
- Registers `auto_decte_propose` and `auto_decte_verify` through the public tool registry.
- Requires a configured absolute Python executable, bridge module root, database path, evidence
  root, and timeout.
- Fails closed on missing configuration, nonzero bridge exit, timeout, extra stdout, malformed
  JSON, mismatched request id, or non-PASS bridge status.
- Uses Cordis-managed registration so unload removes the tools but cannot remove external records.

### 5.2 Python AI-suggestion candidate use case

- Adds one candidate-only application service for immutable JSON evidence and an
  `AI_SUGGESTION` certificate.
- Requires a persisted, valid parent certificate because existing AUTO-DECTE semantics require AI
  suggestions to declare lineage.
- Adds an `AI_OUTPUT` evidence classification.
- Reuses the narrow candidate-write facade and adds no fact-write method.
- Persists evidence, certificate, and audit atomically. A database failure discards the stored
  evidence file best-effort and exposes no referenceable certificate.

### 5.3 Python bridge CLI

- Canonical one-request/one-response JSON protocol.
- Model-available operations: `propose`, `verify`.
- Host-only operations: `init-fixture`, `host-confirm`, `export-receipt`.
- Unknown operations reject before application composition.
- Every response contains `protocol_version`, `request_id`, `operation`, `status`, and either a
  typed result or stable error code.

### 5.4 R19 experiment driver

- Creates a fresh work directory and database per case.
- Boots the actual pinned DSH/Cordis Loader with the built plugin package.
- Invokes tools through DSH `ToolRuntime`, not by calling plugin functions directly.
- Invokes host confirmation only through the separate Python host command.
- Records DSH stdout/stderr, composed config, package lock, source revision, requests/responses,
  database digests, receipt, and manifest.

### 5.5 Offline verifier

- Recomputes hashes over exported records and their manifest.
- Does not import or execute DSH packages.
- A one-byte mutation must produce one exact path-level failure.

## 6. Protocol and data flow

### 6.1 Candidate proposal

The plugin accepts a bounded object:

- `form_id`, `field_key`, `value`, `expected_fact_version`;
- `parent_certificate_id`;
- DSH `session_id` and the immutable tool-execution identifier supplied by the host driver;
- producer id/version and a fixed selection-artifact id registered by the R19 experiment;
- optional confidence carried as metadata only and not interpreted as accuracy.

The bridge canonicalizes the complete request as JSON evidence, stores its bytes, verifies the
parent certificate, and creates a new AI-suggestion certificate whose evidence locator names the
DSH session, tool execution, and field. The response returns certificate/candidate/evidence ids
and hashes. Current authoritative record version must remain unchanged.

### 6.2 Host confirmation

The experiment driver supplies reviewer identity as a trusted-host precondition outside the model
tool arguments. It calls existing `ReviewForms.confirm` with the persisted certificate id. Accept
uses the candidate value; Correction commits an explicit different value while retaining the DSH
candidate and parent lineage.

### 6.3 Export and offline verification

The bridge exports the proposal request/response, candidate certificate, decision, transition,
record version, evidence hash, DSH source revision, plugin source hash, and database digest into a
non-self-referential manifest. The verifier checks those bytes without importing DSH.

## 7. Failure semantics

- Bridge unavailable or timeout: DSH tool returns controlled failure; no candidate or fact row.
- Malformed/extra stdout: controlled protocol failure; no follow-on confirmation.
- Unknown parent, stale expected version, substituted session/execution id, evidence mutation, or
  unregistered producer/artifact: reject with stable code.
- Model attempts `auto_decte_confirm`: DSH returns unknown tool because it is not registered.
- Host stale confirmation or tampered evidence: existing admission rejection; canonical logical
  database digest before and after must be identical.
- Plugin unload: tool registration disappears; already exported receipts remain independently
  verifiable.
- Partial files from a failed case remain in its non-overwriting failure directory and are never
  relabelled as a successful run.

## 8. Experiment matrix

| ID | Case | Required observation |
|---|---|---|
| D1 | Real Loader composition | Pinned DSH loads the built plugin and exposes exactly two tools |
| D2 | Candidate-only proposal | Candidate/evidence/certificate persist; fact version remains zero |
| D3 | Accept | Host confirmation creates exactly one successor with the proposed value |
| D4 | Correction | Candidate remains unchanged; successor holds the explicit corrected value |
| D5 | Stale confirmation | Controlled rejection and equal before/after logical DB digests |
| D6 | Tampered evidence | Controlled rejection and equal before/after logical DB digests |
| D7 | Model confirmation attempt | `auto_decte_confirm` is absent/unknown; no database change |
| D8 | Bridge unavailable | Tool fails closed; no candidate/fact change |
| D9 | Plugin unload | Tools disappear while external records and verifier remain usable |
| D10 | Offline mutation probe | Clean receipt passes; one-byte mutation reports exactly the changed path |

The denominator is ten declared cases. No favorable case may be omitted.

## 9. Tests and quality gates

1. Python red/green unit tests for the AI-suggestion use case and protocol validation.
2. Python integration tests for candidate atomicity, parent lineage, Accept, Correction, stale, and
   tamper behavior through production facades.
3. TypeScript tests for package shape, configuration, request ids, timeout/nonzero/malformed
   responses, and absence of a confirmation tool.
4. Actual pinned DSH Loader/ToolRuntime test.
5. Ten-case non-overwriting experiment with source/config/lock hashes.
6. Offline clean and one-byte mutation verification.
7. Existing AUTO-DECTE Python suite, Ruff, and mypy/available static checks.
8. Paper claim ledger, citation closure, LaTeX build, and independent audit reruns.

## 10. Paper integration rule

The DSH experiment enters the main manuscript only if D1--D10 all pass and its evidence manifest
verifies. Otherwise the failed integration remains in the artifact and the paper only cites DSH as
related work/future integration.

On success, related work will cite the harness-convergence study and distinguish Cordis plugin
composability from external authority. Evaluation will add one RQ on harness integration;
results will report the complete ten-case denominator; threats will disclose a single DSH
revision, deterministic driver rather than a live model, developer-preview API instability, and
the trusted-host reviewer-identity precondition.

## 11. Non-goals

- No DSH fork or patch to its core.
- No TypeScript reimplementation of certificate/admission semantics.
- No replacement of DSH session persistence, approval UI, sandbox, or agent loop.
- No live credentials or production data.
- No claim that a DSH approval is equivalent to attributable human authorization.
- No performance rerun of unrelated R17 grids unless the measured AUTO-DECTE path changes.
- No deletion or overwrite of R17, R18, or failed R19 outputs.

## 12. Completion criteria

R19 is technically complete only when the pinned-source checkout, plugin package, bridge, ten-case
run, clean/mutated offline verification, normalized paper input, claim-evidence ledger, manuscript,
compiled PDF, and updated source/evidence/release manifests all pass. Personal author metadata and
public artifact DOI remain author-only blockers and are not invented.
