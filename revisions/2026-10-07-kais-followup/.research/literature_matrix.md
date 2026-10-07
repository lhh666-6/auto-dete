# Literature comparison: corrected review and execution continuity

Created 2026-10-07 using the literature-triage-matrix skill. Scope: four existing cited primary sources plus this manuscript; no new references. Three versioned preprint full texts and the official LangChain documentation were consulted. This custom three-column matrix records positive source claims, not an absence checklist.

| Work | Approval or binding focus | Reported continuation evidence |
|---|---|---|
| LangChain HITL (`langchainHITL`) | Selected tool calls and arguments; approve, edit or reject. | Documented checkpointed resumption with persisted graph state, execution of edited calls and rejection feedback to the model. |
| Cordon (`chen2026cordon`; arXiv:2606.17573v1) | Task transaction, result lineage, staged effects and approval scoped to object, action, sink and time window. | Containment benchmarks and deterministic rollback/resume checks; released external effects require audit or compensation. |
| Continuity Kernel (`he2026continuity`; arXiv:2608.11632v1) | Proposal identity, exact predecessor, pre-state authority and evidence bound to activation. | Bounded invariant checks and forward restoration under current authority. |
| Commit-time authorization (`santosgrueiro2026committime`; arXiv:2607.10487v1) | Witness freshness, causal priority, effect binding and eligibility at durability. | Controlled invalidation separates endpoint success from authorized completion; guarded abort and witness-revalidation recovery. |
| This work | Machine proposal, corrected value, reviewed instance and executed transition. | Paired instance-policy contrast after the same review, holding corrected value and retained context fixed; observed reuse/reauthorization, utility, integrity and continuation costs. |

Continuity Kernel already binds proposal identity. This manuscript's narrower positioning is the explicit correction-specific relation and paired continuation measurement. Neither identity binding, execution gating nor recovery in general is claimed as unique.

Exact cell-level source locations, source-scope qualifications and a ready-to-paste LaTeX table are in [REVIEW-CLOSURE-COMPARISON.md](../REVIEW-CLOSURE-COMPARISON.md). This is a cross-work comparison, not a new source-veracity audit or a comparison of commensurable benchmark rates.
