# Review closure: compact primary-source comparison

Date: 2026-10-07. **Ready for manuscript integration.** Five rows, three columns, existing citation keys only. No changes to `main.tex`, `supplement.tex`, figures, data or other reports. The table is intended for the end of Related Work and uses packages already present in the manuscript.

Applied [literature-triage-matrix](C:/Users/lenovo/.agents/skills/literature-triage-matrix/SKILL.md). There was no existing project matrix; created `.research/literature_matrix.md`. Prior metadata and publication-status findings in `FINAL-POLISH-CITATION-AUDIT.md` were reused, while the comparison cells below were checked against primary full-text sections and official documentation. No secondary summaries or additional suggested references were used.

## Ready-to-paste table

```latex
\begin{table*}[t]
\centering
\small
\caption{Conceptual comparison of authorization boundaries and reported continuation evidence, not a cross-system benchmark.}
\label{tab:authorization-comparison}
\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}p{0.20\textwidth}>{\raggedright\arraybackslash}p{0.32\textwidth}>{\raggedright\arraybackslash}X@{}}
\toprule
Work & Approval or binding focus & Reported continuation evidence \\
\midrule
LangChain HITL \citep{langchainHITL} &
Selected tool calls and arguments; approve, edit or reject. &
Documented checkpointed resumption with persisted graph state, execution of edited calls and rejection feedback to the model. \\
\addlinespace
Cordon \citep{chen2026cordon} &
Task transaction, result lineage, staged effects and approval scoped to object, action, sink and time window. &
Containment benchmarks and deterministic rollback/resume checks; released external effects require audit or compensation. \\
\addlinespace
Continuity Kernel \citep{he2026continuity} &
Proposal identity, exact predecessor, pre-state authority and evidence bound to activation. &
Bounded invariant checks and forward restoration under current authority. \\
\addlinespace
Commit-time authorization \citep{santosgrueiro2026committime} &
Witness freshness, causal priority, effect binding and eligibility at durability. &
Controlled invalidation separates endpoint success from authorized completion; guarded abort and witness-revalidation recovery. \\
\addlinespace
This work &
Machine proposal, corrected value, reviewed instance and executed transition. &
Paired instance-policy contrast after the same review, holding corrected value and retained context fixed; observed reuse/reauthorization, utility, integrity and continuation costs. \\
\bottomrule
\end{tabularx}
\end{table*}
```

The table body and caption total **150 words** (citation commands excluded). It should occupy roughly half a page at the existing 9 pt table size; final float placement and height must be verified by the integrating editor's compile. It needs no new package, bibliography entry, custom macro or numerical result.

## Cell-by-cell grounding

| Row | Approval/binding cell: exact location | Continuation/evidence cell: exact location |
|---|---|---|
| LangChain HITL | Official **Human-in-the-loop**, “Configuring interrupts” and “Decision types”: per-tool review configuration and approve/edit/reject decisions. | “Responding to interrupts,” “Decision types” (edit/reject), and “Execution lifecycle”: checkpointed resumption, edited-call execution, and rejection feedback returned to the agent. [Official documentation](https://docs.langchain.com/oss/python/langchain/human-in-the-loop). |
| Cordon | **§3.1, Table 2 (I8)** and **§3.3**: transaction scope, scoped approval and result lineage; **§4.5** stages external effects. | **§6.1–6.3, Table 5**: containment workloads and deterministic rollback/resume tests; **§3.4** separates local rollback from audit/compensation after external release. [Versioned full text](https://arxiv.org/html/2606.17573v1). |
| Continuity Kernel | **§2.2** and **§3.1, Table 2**: proposal identifier/seal, exact predecessor, pre-state authorization and evidence checks; **Appendix B.1, Table 12** specifies bindings. | **§4.3, Eq. 10; Appendix C.3** define forward restoration; **§§5.1–5.3, Tables 6–8** report bounded exploration and limits. [Versioned full text](https://arxiv.org/html/2608.11632v1). |
| Commit-time authorization | **§3, “Boundary checks,” Table 3**: the four named durability conditions. | **§4, “Design”; §5, “Primary result”; §6, “Blocking first, recovery second” and “Boundary effect and cost”**: controlled invalidation, endpoint/authorization separation, guarded abort and revalidation recovery. [Versioned full text](https://arxiv.org/html/2607.10487v1). |
| This work | **Main §§3.1–3.2**, especially Eqs. 2–5: four roles and the context/bound policy distinction. | **Main §6.1** (“Shared review history and unique policy difference”), **§§7.2–7.4**, Figure 3; **supplement §§S11–S12**: shared-checkpoint pairing, recovery paths, distinct U/I endpoints and costs with separate cohort denominators. |

## Comparison limits to preserve

- **Continuity Kernel already binds proposal identity.** It is a direct precedent, not a missing-feature baseline. Its bounded model is not evidence about this manuscript's particular paired continuation effect.
- Cordon's rollback results include deterministic trajectories without model calls; describing all of its recovery evidence as adaptive agent recovery would be too broad.
- CommitGuard reports recovery when fresh authority can be restored, in addition to guarded abort. Do not describe it as blocking-only or imply that endpoint/authorization separation originates here.
- LangChain's cited source documents an execution interface. This row makes no empirical performance or benchmark claim.
- The present manuscript's positioning is correction-specific: retained proposal value, authorized replacement, reviewed/executed identities, and a paired change to instance enforcement followed through actual continuations. This is an interpretation of the contrasted stated scopes, not proof of historical priority.
- The three research comparators retain their verified **arXiv preprint** status. No comparison of their numerical success rates is made, because workloads and denominators differ.

## Handoff

The matrix has five new rows (four external sources plus this work), zero pre-existing rows skipped. Read three primary papers through full-text HTML; a focused independent reader additionally checked the Continuity Kernel PDF sections. The official LangChain page supplies the fourth external row. All four citation keys already exist in the manuscript. The integrating editor should compile once, check the wide table at normal reading scale, and retain the surrounding sentence acknowledging existing proposal-identity binding.
