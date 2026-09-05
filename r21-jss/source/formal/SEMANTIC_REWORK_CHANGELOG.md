# SEMANTIC_REWORK_CHANGELOG.md — GPT Semantic Gate Rework Round 5 (v0.5 -> v0.6)

> **Gate verdict received:** **REWORK** (`DEEPSEEK_SEMANTIC_REWORK_PROMPT_v05.md`).
> **Research direction:** unchanged. No `.als` was written, no paper was modified, no AI/OCR/agent feature was added, no Python code was changed.
> **Result:** all required changes P0, the mandatory dependency re-check, and both P1 cleanups are applied in v0.6.

---

## 1. Required change -> implemented change ledger

| Gate item | Required change | Implemented in |
|---|---|---|
| P0 | `orderedTrace` must enforce `stateInvariant` on every state in a reachable trace; no prose-only “plus stateInvariant” | FORMAL_MODEL.md §5.1, §5.2; PROPERTIES.md §1 (Structural reachability invariant) |
| P0 | The invariant must guarantee at minimum `currentVersion[r].record = r`; `(some committedValue[r,f]) iff (some committedSource[r,f])`; `committedSource[r,f].targetRecord = r` / `.targetField = f`; and must **not** add `committedSource in transitions` or `committedSource.value = committedValue` | FORMAL_MODEL.md §4.8; PROPERTIES.md §1 |
| P0 dep | Re-evaluate the dependency table with the invariant actually enforced; ABL_1, ABL_2a, ABL_2b, ABL_3, ABL_4a, ABL_4b, ABL_5, ABL_6, ABL_7, ABL_8, ABL_9, ABL_10 must remain structurally satisfiable; special attention to ABL_3 / `C-record` | FORMAL_MODEL.md §7.3 (ablation-by-ablation table + ABL_3 note); THREAT_MODEL.md §11; PROPERTIES.md §4 |
| P1-1 | Use the gate-required wording instead of labeling the producer/evidence/value/version/certificate/authorization checks as exclusive to the executable layer. Required wording: the formal trace predicate mirrors these binding checks, but the Alloy P6 corruption/minimality claim is restricted to source-anchor loss/replacement and source-version duplicates; individual binding-corruption necessity is evaluated through executable conformance tests and is not claimed as a separate Alloy minimality result | FORMAL_MODEL.md §12.3, §13, §15, §16; THREAT_MODEL.md §6, §12; PROPERTIES.md §1 P6, §9, §10 |
| P1-2 | The scientific persistence object is the Certificate with embedded Candidate. `State.candidates` is **kept as an auxiliary machine-artifact/reachability set that no P0–P6 claim depends on**; no `C-candidate-preexists`; durable prerequisite remains `e.certificate in e.pre.certificates` | FORMAL_MODEL.md §4.4, §4.8, §7; THREAT_MODEL.md §3; PROPERTIES.md §1 P2 |

## 2. Structural decisions recorded for the gate

### 2.1 P0: `stateInvariant` is inside `orderedTrace`

```
pred orderedTrace[tr: Trace] {
  wellFormedTrace[tr]

  all s: tr.states.elems |
    stateInvariant[s]

  init[tr.states[0]]

  all i: tr.events.inds |
    Occurs[tr.events[i], tr.states[i], tr.states[i.plus[1]]]
    and eventStep[tr.events[i]]
}
```

`ReachableState(s)` is defined through `orderedTrace`, so **every State in every reachable ordered trace satisfies `stateInvariant`**. The first state is covered by the same universal clause together with `init`; every post-state of every event edge is covered by the same clause. There is no separate prose dependency.

### 2.2 P0: the invariant is structural only

`stateInvariant` guarantees exactly the four required structural clauses:

1. `currentVersion[r].record = r`;
2. `(some committedValue[r,f]) iff (some committedSource[r,f])`;
3. `committedSource[r,f].targetRecord = r`;
4. `committedSource[r,f].targetField = f`.

It does **not** contain `committedSource[r,f] in s.transitions` (so a post-tamper state may keep a source anchor whose transition row was deleted), and it does **not** contain `committedSource[r,f].value = committedValue[r,f]` (that is the P5/P6 binding property, not structural validity).

### 2.3 P0 dependency re-check with the invariant enforced

No ablation witness required alteration. FORMAL_MODEL.md §7.3 records the check ablation by ablation:

| Ablation | Why the witness still satisfies the enforced invariant |
|---|---|
| ABL_1 | The effect writes the same `(r, f_B)` in both committed relations and advances `r`'s own version; field substitution is invisible to the invariant. |
| ABL_2a / ABL_2b | Evidence identity/owner mismatches are outside all four invariant clauses; the effect still writes `(r, f)` consistently. |
| ABL_3 / `C-record` | Retained `C-version` + `C-fresh` and the pre-state invariant give `e.expectedVersion = pre.currentVersion[r_B]` with `record = r_B`; the post-state advances `r_B` to its own successor and writes both committed relations on `(r_B, f)`. The prior derivation `stateInvariant => currentVersion[targetRecord].record = targetRecord` remains available, but it never mentions `candidate.targetRecord`, so `C-record` is still independently ablatable. |
| ABL_4a / ABL_4b | Attempt/certificate version mismatch or staleness is outside the invariant; the effect advances the true current version of `targetRecord`. |
| ABL_5 | Authorization/certificate identity mismatch is outside the invariant; `(r, f)` is written consistently. |
| ABL_6 | The invariant deliberately says nothing about `State.transitions` count/membership/source identity, so missing, duplicate, or source-detached transitions all remain satisfiable. |
| ABL_7 | `tamperStep` preserves `committedValue`, `committedSource`, and `currentVersion`; because there is no `committedSource in transitions` clause, deleted/replaced/duplicate-transition states remain structurally valid while the weakened verifier reports Complete. |
| ABL_8 | The invariant has no source-value/committed-value clause, so committed Y with source transition X (`X != Y`) is structurally valid and P5 fails exactly on that binding mismatch. |
| ABL_9 / ABL_10 | The invariant does not constrain `certificates` or `evidence`; conjuring either artifact leaves it satisfied. |

**Result:** all twelve named ablations remain structurally satisfiable with `stateInvariant` enforced; `ABL_3` remains independent. The expected Alloy counterexamples are unchanged.

### 2.4 P1-1 wording: formal vs executable P6 checks

The v0.5 label that treated the detailed binding checks as exclusive to the executable layer was removed. The required wording is now used consistently:

> The formal trace predicate mirrors these binding checks, but the Alloy P6 corruption/minimality claim is restricted to source-anchor loss/replacement and source-version duplicates. Individual binding-corruption necessity is evaluated through executable conformance tests and is not claimed as a separate Alloy minimality result.

The detailed checks remain inside `traceComplete` as the concrete verifier contract; the Alloy claim is still only source-anchor loss/replacement + source-version duplicate detection.

### 2.5 P1-2 Candidate auxiliary state

`State.candidates` is kept (option A) and is now explicitly called an **auxiliary machine-artifact/reachability set**. No P0–P6 claim depends on it: the contract and every property read the candidate through `Certificate.candidate`. The scientific persistence object remains the **persisted Certificate with embedded Candidate**; the durable admission prerequisite remains `e.certificate in e.pre.certificates`, and no `C-candidate-preexists` conjunct was introduced.

---

## 3. Mandatory Round-6 self-check

1. **Does every State in every reachable ordered trace satisfy `stateInvariant`?**
   **Yes.** `orderedTrace` itself asserts `all s: tr.states.elems | stateInvariant[s]`, and `ReachableState` is defined through ordered traces. This is structural, not a prose side condition.

2. **Can `currentVersion[r]` belong to another Record in a reachable trace?**
   **No.** Every reachable state satisfies `currentVersion[r].record = r`; the initial state satisfies it because `initialVersion[r].record = r`, and every effective step advances to a successor of the same record.

3. **Can `committedValue` and `committedSource` have different domains in a reachable trace?**
   **No.** Every reachable state satisfies `(some committedValue[r,f]) iff (some committedSource[r,f])` for every `(r, f)`.

4. **Does `stateInvariant` intentionally allow `committedSource` to reference a deleted Transition after `TamperEvent`?**
   **Yes.** There is no `committedSource[r,f] in s.transitions` clause. Deleting/replacing the source transition changes only `transitions`; the preserved anchor can dangle, and that dangling anchor is exactly the P6 `Incomplete` case.

5. **Does `stateInvariant` intentionally avoid equating source value with committed value?**
   **Yes.** There is no `committedSource[r,f].value = committedValue[r,f]` clause. That equality is the P5/P6 binding property; its violation after corruption is observable via `traceComplete`, not a structural-state exclusion.

6. **Are ABL_1–ABL_10 still structurally satisfiable after the invariant is enforced?**
   **Yes.** FORMAL_MODEL.md §7.3 records the check ablation by ablation (table in §2.3 above). No witness had to be altered; the expected counterexamples are unchanged.

7. **Is ABL_3 still independent?**
   **Yes.** With `C-record` removed, `C-version` + `C-fresh` + `stateInvariant` derive only that `candidate.expectedVersion.record = e.targetRecord` (via `pre.currentVersion[targetRecord].record = targetRecord`). Nothing derives `candidate.targetRecord = e.targetRecord`. The S3 witness (candidate for `r_A`, effective write to `r_B`) lands in an invariant post-state.

8. **Is formal-vs-executable P6 wording accurate?**
   **Yes.** The documents now use the required sentence: the formal trace predicate mirrors the binding checks, but the Alloy P6 corruption/minimality claim is restricted to source-anchor loss/replacement and source-version duplicates; individual binding-corruption necessity is evaluated through executable conformance tests and is not claimed as a separate Alloy minimality result. The prior exclusive-execution label is no longer used for those checks.

9. **Is Candidate persistence explicitly certificate-embedded, with `State.candidates` only auxiliary or removed?**
   **Yes.** Candidate is embedded in the persisted `Certificate`; `State.candidates` is kept only as an auxiliary machine-artifact/reachability set that no P0–P6 claim depends on; no `C-candidate-preexists` exists; the durable prerequisite is `e.certificate in e.pre.certificates`.

10. **Has no `.als` been written?**
    **Yes — zero `.als` files exist in the repository, and none is included in the ZIP.** No Alloy run or compilation has been performed. Full Alloy implementation remains forbidden until GPT issues PASS.

---

## 3.1 Pre-submission correction (internal multi-perspective review, 2026-08-23)

- **P6 source-version uniqueness quantifier fixed.** In `FORMAL_MODEL.md` and `PROPERTIES.md`, the previous `and one u: s.transitions | ... and u = t` allowed Alloy to parse `u = t` inside the quantifier body, making the duplicate check vacuous. Both occurrences are now written as `and (one u: s.transitions | u.targetRecord = r and u.targetField = f and u.toVersion = src.toVersion)` with no trailing `and u = t`.
- No `.als` was written; no paper, code, or experiment changes were made.

## 4. Return verdict

All v0.5 gate items are applied: P0 invariant enforcement, P0 dependency re-check (all twelve ablations satisfiable, ABL_3 independent), P1 wording cleanup, and P1 Candidate-auxiliary-state cleanup. The ten mandatory answers are all **Yes / correctly scoped**.

**PASS-READY**
