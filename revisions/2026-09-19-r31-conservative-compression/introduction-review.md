> Stage record: later sections have now been edited and both PDFs compiled. FULL-REVISION-REPORT.md and reviews/verification.json supersede the earlier unchanged-file and uncompiled status below.

# Introduction — conservative compression and abstract alignment

## Section accounting

- Original prose: **551 words**; revised: **457 words**; reduction: **94 words (17.06%)**.
- Scientific claim affected: **No**, based on editorial semantic comparison.
- Count includes contribution titles and prose but excludes section/paragraph headings, reference commands, citation commands, inline/display mathematics, and the unchanged figure/caption. Hyphenated/slash compounds count as one whitespace-delimited word; identical rules apply before and after. No page reduction is inferred.
- Removed: duplicate introductory descriptions of five neighboring works already covered in Related Work §2.1, plus redundant wording in examples and contribution summaries.
- Moved to Supplement: **none**. No reproducibility information was removed or relocated.
- Equations, figure/caption, existing citation keys, RQ roadmap, and C1–C5 numbering are unchanged. The 35-case identifier was already established in the abstract and evaluation.
- The installed TeX word-count launcher could not run because its setup was unfinished. The stated explicit prose-count procedure was used instead; no environment changes were made to repair TeX. No compilation is claimed.

## Paragraph decisions and revised English

Every original prose paragraph and contribution item is accounted for below. KEEP items C2/C3 receive only the identified clarifications. Equations remain verbatim in the manuscript and are represented by editorial markers here. All replacements are applied to `paper/sections/01-introduction.tex`.

### P1 — COMPRESS

Reason: Remove filler while retaining operational uses and the authority/value/proposal/state question.

AI-generated updates can become persistent facts for reporting, payment, scheduling, or later decisions. Admission must establish which authority approved which value from which persisted proposal and record state.

### P2 — COMPRESS

Reason: Keep the 90/100/101 example and both attribution failures while shortening the unchanged-field explanation.

Consider an authoritative quantity of 90: a recognizer proposes 100, but a reviewer authorizes 101. Accepting a machine proposal of 101 yields the same final value with different attribution. Rewriting the candidate falsely attributes the correction to the model; dropping an unchanged batch-code field's earlier source preserves values but loses lineage. Admission must retain the predecessor 90, proposal $x_c=100$, and authorized value $x_a=101$, allowing [Equation 1 unchanged: $x_c\neq x_a$] with both value roles and the complete successor's sources intact.

### P3 (including prose around Equation 2) — COMPRESS

Reason: Replace the repeated five-work survey with a cited pointer to Related Work §2.1; retain the full relation and clarify that ordinary transactions/logging can implement it.

The target systems permit human correction of AI-generated field candidates, persist accepted updates, and require reconstruction of authorization and origin. Prior work provides activation, governed-memory, and transaction foundations [Original citation keys retained: he2026continuity,zhou2026latticemind,zhan2026authoritycollapse,saidi2026mutmem,cui2026memtxn], detailed in Section 2. We specify the correction-aware, field-level relation: [Equation 2 unchanged: exact candidate → candidate-bound human authorization → explicit authorized value → complete successor → total field-source attribution.] The candidate remains historical evidence, human authorization supplies value authority, and a trusted transaction constructs the successor. Ordinary transaction and logging facilities can implement this joint, checkable binding of proposal identity, a possibly different authorized value, and exact changed/unchanged field sources.

### P4 — COMPRESS

Reason: Retain all five failure families and omission-based comparison; keep the declared-model limitation in adjacent C2.

We ask which observations distinguish candidate substitution, correction erasure, stale replay, fragmented successors, and source ambiguity. Paired histories expose distinctions lost when an information class is omitted. The Python/SQLite reference realization Auto-Decte supports the following contributions:

### C1 — COMPRESS

Reason: Align the relation with the approved abstract, preserving the exact candidate, human-authorized value, original proposal, and complete successor attribution; local alignment need not shorten this item.

**Correction-aware admission contract.** Bind human authorization to the exact persisted candidate and explicit authorized value, preserving the proposal and every field's source in a complete successor.

### C2 — KEEP

Reason: Retain the conditional claim; the only editorial clarification explicitly identifies the five information classes, matching the approved abstract.

**Conditional failure distinguishability.** Five safe/unsafe history pairs establish class-wise irredundancy of five failure-distinguishing information classes within the declared failure and observation model.

### C3 — KEEP

Reason: Retain the evidence chain; the only clarification replaces the generic executable catalogue description with its existing 35-case identifier.

**Relational and transactional realization.** Connect the contract to bounded Alloy checks, a CAS-protected transaction, selected formal–concrete projections, and the 35-case fault catalogue.

### C4 — COMPRESS

Reason: Shorten the connective while retaining frozen v8, persistence equivalence, three configurations, and separate model/host observations.

**Cost and integration evidence.** Characterize frozen v8 persistence-equivalent admission and trace costs; separate restricted-agent task outcomes from host-enforced authority checks across three qualified configurations.

### C5 — COMPRESS

Reason: State seven-of-eight agreement once for both controls, retaining equal-valued substitution and the richer-context qualification.

**Evaluated-control separation.** Both frozen and strengthened transactional value-audit controls agree with candidate-bound admission on seven of eight single-history cases. Equal-valued candidate substitution separates them; richer recorded review context narrows the distinction.

### P5 — constructed workflow — COMPRESS

Reason: Remove generic team framing and combine the policy qualification with instance accountability; retain the separate review-event requirement.

Two extraction retries may share a record, field, and authorized value but differ in timestamps and evidence locators. Value-level approval suffices to establish that a value was approved; instance-level accountability asks which persisted artifact was reviewed. When policy requires this distinction, candidate-bound admission records the reviewed instance and rejects substitution. The current path records value-changing updates; renewed review without a value change requires a separate review-event path.

### P6 — trust boundary — KEEP

Reason: This concise trust qualification and pointer to Contract are necessary and unchanged.

The contract records and rechecks authority under externally supplied host authentication and review-channel integrity; the trust boundary is detailed in Section 3.

### P7 — roadmap — KEEP

Reason: Preserve the RQ1–RQ8 roadmap and admission-boundary figure pointer unchanged.

The paper proceeds from the admission relation (Section 3) to relational encodings (RQ1–RQ2), persisted behavior and controls (RQ3–RQ5), and cost and integration (RQ6–RQ8). Figure 1 shows the admission boundary.

### Figure 1 caption — KEEP

Reason: Preserve rejection semantics, responsibility-versus-truth qualification, and AI-assistance disclosure. The full caption is unchanged.

Correction-aware authoritative-state admission. Only candidate-bound Accept or Correction decisions proceed to transactional admission. The declared distinction checks, host-policy revalidation, and version compare-and-swap protect creation of a complete successor and total source map. Reject, failed validation, or a lost compare-and-swap leaves authoritative state unchanged. Authorization records responsibility, not factual truth. AI-assisted diagram scripting: OpenAI Codex (gpt-6-astra, OpenAI, September 2026 revision); deterministic vector rendering of the declared workflow.

## Repetition and primary narrative locations

| Material | Overlap | Primary detailed account |
|---|---|---|
| Five neighboring works | Introduction P3 and Related Work §2.1 | Related Work §2.1; Introduction now retains cited positioning only. |
| Admission relation | Abstract, Introduction chain/C1, Contract, Discussion | Contract for definitions; Introduction for the visible chain and positioning. |
| Five-class irredundancy | Abstract, C2, Proposition 1, Discussion | Contract/Proposition 1 for the full argument and its boundary. |
| Evaluated-control separation | Abstract, C5, Results RQ5, Discussion | Results RQ5 for outcomes; Discussion for richer-context implications. |
| Trust assumptions | Abstract, P6, Contract, Discussion | Contract for the full boundary; concise local qualifications remain. |
| Review without value change | Workflow and Contract | Contract for the technical restriction; retain its consequence in the workflow. |

These are recommended primary accounts for detailed exposition. Brief Abstract/Introduction summaries are necessary repetition, not material to eliminate wholesale.

## Novelty visibility and preservation

The 90/100/101 example shows how equal final values conceal different proposal/authorization histories. The unchanged five-link relation and C2 foreground the correction-aware obligation and conditional characterization before implementation/evaluation. Ordinary transaction/logging feasibility remains explicit. No claim of a new primitive, universal necessity, minimality, completeness, uniqueness, or general superiority is added.

Both equations, the full figure environment, and the existing citation keys/order were compared with r31 after normalizing line endings and are unchanged. Only the approved Abstract and Introduction have changed in the separate source copy; all 45 other files remain byte-identical to the submitted archive. Related Work and later sections, including the Supplement, remain unedited.
