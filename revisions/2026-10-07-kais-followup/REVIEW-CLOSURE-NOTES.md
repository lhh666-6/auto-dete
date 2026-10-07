# Review closure edits — 2026-10-07

## Scope

This targeted pass updates the manuscript and supplement, adds a primary-source comparison table, and refreshes the PDFs and delivery audits. The saved baseline is `qa/before-review-closure/`, corresponding to published commit `a72845f95d05399ad0ff2dfac203566ce60f5daf`. All formal display equations, existing empirical tables, measurements and author statements are unchanged. No raw data, scoring code, figure asset, type size or spacing was changed. Current compilation and visual checks are recorded in `FINAL-POLISH-VERIFICATION.md` and `FINAL-POLISH-PDF-QA.md`.

## Targeted clarifications

1. Main Section 3.1 replaces generic role repetition with the existing illustrative quantity example: baseline 90, candidate proposal 100, authorized value 101, unchanged batch B-008 with exact source t_b, and proposal retained in c_1. It explicitly distinguishes integer 101 from floating serialization 101.0 under the shared canonical JSON rule.
2. The same example scopes grant-consumption and idempotency behavior to the online facade: identical arguments plus the same key retrieve the old receipt without a new transition; a new key under the consumed grant is rejected semantic replay. The illustration is explicitly not a new experiment.
3. Supplement S3 expands the example's typed-value and replay distinction. A domain-specific typed adapter is described only as a prospective extension requiring common semantics across the planner, admission gate, trace verifier, independent oracle and formal projection, with renewed validation. No implemented or validated drop-in adapter is claimed.
4. Main Section 3.4 explicitly scopes the atomic multi-field guarantee to one record; cross-record/distributed atomicity is not validated. The Section S4 pointer now distinguishes single-record admission timings from trace workloads. S4 clarifies that the 1,000-record parameter is background population, not a cross-record transaction benchmark; every performance number is unchanged.
5. Main Section 8.4 states that the observed A/B recovery mixtures combine deployment and collection conditions and therefore cannot isolate model-capability differences. Existing selected-cohort, revision-visibility and inferential limitations remain. No universal latency acceptability or equivalence claim is introduced.

6. Related Work 2.3 now points to a compact five-row, three-column conceptual comparison. It explicitly acknowledges prior proposal-identity binding and recovery. Existing references support every external row; no reference was added. Cell-level source locations are recorded in `REVIEW-CLOSURE-COMPARISON.md` and `.research/literature_matrix.md`. This is not a cross-system performance comparison.
7. The running-example identifiers are consistently c_1, c_2 and t_1 in the Introduction, main formal explanation and supplementary example.

Net source-whitespace-token changes (including table markup): main +199, supplement +123. These are source-token counts, not rendered prose counts.

## Exact source diff

Zero-context unified diff; unchanged lines are omitted.

```diff
--- before/main.tex
+++ main.tex
@@ -65 +65,33 @@
-AgentDojo separates task utility from security outcomes in interactive tool environments \citep{debenedetti2024agentdojo}. Recent preprints also place authorization at the execution boundary. Cordon \citep{chen2026cordon} stages local changes and external effects within a task-level transaction, with lineage, scoped approval and recovery. Continuity Kernel \citep{he2026continuity} binds proposal identity, predecessor state, pre-state authority and evidence to atomic state activation. Commit-time authorization \citep{santosgrueiro2026committime} checks whether authority remains fresh, causally prior, effect-bound and eligible at durability, and separates authorized completion from endpoint success. Our comparison fixes the corrected value and retained context while varying whether execution must use the reviewed candidate instance. The contract preserves the machine value, authorized replacement and reviewed/executed identities as separate roles. Paired live continuations reveal how enforcing that relation changes the next action, recovery path and execution cost.
+AgentDojo separates task utility from security outcomes in interactive tool environments \citep{debenedetti2024agentdojo}. Table~\ref{tab:authorization-comparison} compares nearby authorization and recovery mechanisms. Prior work already binds proposal identity and supports recovery. Our intervention fixes the corrected value and retained context while varying whether execution must use the reviewed instance. It separates machine proposal, authorized replacement and reviewed/executed identities, then measures subsequent actions, recovery paths and costs.
+
+\begin{table*}[t]
+\centering
+\small
+\caption{Conceptual comparison of authorization boundaries and reported continuation evidence, not a cross-system benchmark.}
+\label{tab:authorization-comparison}
+\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}p{0.20\textwidth}>{\raggedright\arraybackslash}p{0.32\textwidth}>{\raggedright\arraybackslash}X@{}}
+\toprule
+Work & Approval or binding focus & Reported continuation evidence \\
+\midrule
+LangChain HITL \citep{langchainHITL} &
+Selected tool calls and arguments; approve, edit or reject. &
+Documented checkpointed resumption, execution of edited calls and rejection feedback. \\
+\addlinespace
+Cordon \citep{chen2026cordon} &
+Task transaction, result lineage, staged effects and scoped approval. &
+Containment benchmarks and deterministic rollback/resume checks; released external effects require audit or compensation. \\
+\addlinespace
+Continuity Kernel \citep{he2026continuity} &
+Proposal identity, exact predecessor, pre-state authority and evidence bound to activation. &
+Bounded invariant checks and forward restoration under current authority. \\
+\addlinespace
+Commit-time authorization \citep{santosgrueiro2026committime} &
+Witness freshness, causal priority, effect binding and eligibility at durability. &
+Controlled invalidation separates endpoint success from authorized completion; guarded abort and witness-revalidation recovery. \\
+\addlinespace
+This work &
+Machine proposal, corrected value, reviewed instance and executed transition. &
+Paired instance-policy contrast after the same review; observed reuse/reauthorization, utility, integrity and continuation costs. \\
+\bottomrule
+\end{tabularx}
+\end{table*}
@@ -81,3 +113,3 @@
-The committed transition retains the proposal as origin evidence and the authorization as the authority for the chosen value. Correction permits $x_c\jneq x_a$; it does not rewrite the immutable proposal to make the two values appear equal.
-
-Contract value comparisons use canonical JSON equality, written $\jeq$: sorted-key, whitespace-minimal serialization must agree. Consequently, an integer, a floating-point serialization and a Boolean remain distinguishable when their serialized values differ. This equality is shared by change detection, admission value checks, tracing and the independent oracle.
+For illustration, a record has quantity 90 and batch \texttt{B-008} sourced from $t_b$. Candidate $c_1$ proposes 100; review authorizes 101. The successor contains quantity 101 through $t_1$ and the unchanged batch with exact source $t_b$. Correction permits $x_c\jneq x_a$; $c_1$ retains 100. In the online facade, successful commit consumes the grant: identical arguments with the same idempotency key return the prior receipt without a new transition; a new key under the consumed grant is rejected as semantic replay. Online Resource 1, Section S3 develops this construction, which is not an additional experiment.
+
+Contract value comparisons use canonical JSON equality, written $\jeq$: sorted-key, whitespace-minimal serialization must agree. Thus integer \texttt{101} and floating serialization \texttt{101.0} are distinct values; Booleans also remain distinguishable when their serialization differs. Change detection, admission value checks, tracing and the independent oracle share this equality.
@@ -121 +153 @@
-Decision, authorization binding, transitions, complete version, sources and audit effects commit together, or the authoritative state stutters. Candidate and review preparation already persisted before the attempted admission remain historical evidence. Online Resource 1, Section S2 states the full P0--P6 contract, no-op handling and mixed-submission semantics.
+Decision, authorization binding, transitions, complete version, sources and audit effects commit together, or the authoritative state stutters. This multi-field guarantee is single-record; cross-record or distributed atomicity is not validated. Candidate and review preparation already persisted before the attempted admission remain historical evidence. Online Resource 1, Section S2 states the full P0--P6 contract, no-op handling and mixed-submission semantics.
@@ -165 +197 @@
-The persistence contract also makes implementation cost measurable. Complete confirmation and source reconstruction are timed separately, with exact output agreement checked across the 36 paired trace-workload cells. Online Resource 1, Section S4 retains the complete admission, tracing and storage grids and their timer boundaries. Agent-level friction is measured after the online policy intervention, where the additional work is an observed part of continuation.
+The persistence contract also makes implementation cost measurable. Complete confirmation and source reconstruction are timed separately, with exact output agreement checked across the 36 paired trace-workload cells. Online Resource 1, Section S4 separates single-record admission timings from trace workloads varying field count, history depth and background record population. Agent-level friction is measured after the online policy intervention, where the additional work is an observed part of continuation.
@@ -301 +333 @@
-The supplementary A cohort was selected by its original availability state and collected later. Requested aliases and settings support route reconstruction, but A's unexposed returned model revision limits exact response reproduction. Retained inputs, responses, checkpoints and independent scores support retrospective verification within that scope.
+The supplementary A cohort was selected by its original availability state and collected later. The observed A/B recovery mixtures combine deployment and collection conditions, so they do not isolate differences in model capability. Requested aliases and settings support route reconstruction, but A's unexposed returned model revision limits exact response reproduction. Retained inputs, responses, checkpoints and independent scores support retrospective verification within that scope.
--- before/supplement.tex
+++ supplement.tex
@@ -250,3 +250,5 @@
-Consider a two-field record at version $v$: quantity is 90 with source $t_q$, and batch is \code{B-008} with source $t_b$. Candidate $c_A$ proposes quantity 100 for version $v$. A reviewer authorizes quantity 101 from $c_A$. The legal successor $v+1$ has quantity 101 from a new transition $t_A$, batch \code{B-008} from the exact previous source $t_b$, and an authorization naming both $c_A$ and 101. Candidate $c_A$ still contains 100. This is an explanatory construction, not an additional measured case.
-
-An equal-valued retry $c_B$ can have the same value and retained review context while being a different persisted instance. Under instance-level authorization, substituting $c_B$ for $c_A$ must fail; under the declared context-level policy it may be admitted. A concurrent successor invalidates the expected predecessor. A proposed two-field admission cannot be split into two commits merely because the final endpoint is the same. Replacing the unchanged batch source with an equal-valued transition also loses the exact source relation.
+Consider a two-field record at version $v$: quantity is 90 with source $t_q$, and batch is \code{B-008} with source $t_b$. Candidate $c_1$ proposes quantity 100 for version $v$. A reviewer authorizes quantity 101 from $c_1$. The legal successor $v+1$ has quantity 101 from a new transition $t_1$, batch \code{B-008} from the exact previous source $t_b$, and an authorization naming both $c_1$ and 101. Candidate $c_1$ still contains 100. Canonical JSON equality distinguishes authorized integer \code{101} from floating serialization \code{101.0}, even if a domain treats their numeric magnitudes as equal. This is an explanatory construction, not an additional measured case.
+
+A newly persisted equal-valued candidate $c_2$ can have the same value and retained review context while being a different instance. Under instance-level authorization, substituting $c_2$ for $c_1$ must fail; under the declared context-level policy it may be admitted. A concurrent successor invalidates the expected predecessor. A proposed two-field admission cannot be split into two commits merely because the final endpoint is the same. Replacing the unchanged batch source with an equal-valued transition also loses the exact source relation.
+
+In the online facade, successful commit consumes the authorization. Identical arguments and the same idempotency key retrieve the prior receipt without creating a transition; using a new key under that consumed grant is semantic replay and is rejected (Section S8). A domain-specific typed adapter would be an extension: normalization would need shared semantics across the planner, admission gate, trace verifier, independent oracle and formal projection, followed by renewed validation. Such an adapter is not an implemented or validated drop-in replacement for canonical JSON equality.
@@ -391 +393 @@
-At 128 fields, 100 versions, and 1,000 total records, the medians are 170.24 ms for bulk access and 509.09 ms for point access, a point/bulk ratio of 2.99. Statement counts are 12 and 693. This comparison is not a rerun of the historical preoptimization algorithm and is not combined with historical-machine timings. The archive retains paired differences and bootstrap intervals; those intervals describe repeated observations on this machine, not cross-deployment variation.
+At 128 fields, 100 versions, and 1,000 total records, the medians are 170.24 ms for bulk access and 509.09 ms for point access, a point/bulk ratio of 2.99. Statement counts are 12 and 693. The record count varies background population for trace access; it does not measure a cross-record atomic transaction. This comparison is not a rerun of the historical preoptimization algorithm and is not combined with historical-machine timings. The archive retains paired differences and bootstrap intervals; those intervals describe repeated observations on this machine, not cross-deployment variation.
```
