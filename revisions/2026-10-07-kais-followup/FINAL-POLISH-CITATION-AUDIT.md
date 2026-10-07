# Final-polish citation audit — 7 October 2026

**Verdict: all three sources exist, their metadata is verified, and the current Section 2.3 attributions are supported.** Add ordinary numeric citations and the three bibliography entries below. No expansion of related work is needed. This audit did not edit `main.tex` or any other manuscript file.

## Verified metadata

| Proposed key | Exact title and full author list | Verified version/date | Primary identifiers |
|---|---|---|---|
| `chen2026cordon` | **Cordon: Semantic Transactions for Tool-Using LLM Agents**. Zheng Chen; Hanqing Liu; Duling Xu; Dong Dong; Jialin Li; Bangzheng Pu; Jidong Zhai. | 2026; v1, submitted 16 June 2026, 06:21:14 UTC. Only v1 is listed in the arXiv submission history. | [Versioned arXiv record](https://arxiv.org/abs/2606.17573v1); [DOI 10.48550/arXiv.2606.17573](https://doi.org/10.48550/arXiv.2606.17573). |
| `he2026continuity` | **Beyond Memory: A Transactional Continuity Kernel for Long-Lived AI Agents**. Jun He; Deying Yu. | 2026; v1, submitted 12 August 2026, 04:28:49 UTC. Only v1 is listed. | [Versioned arXiv record](https://arxiv.org/abs/2608.11632v1); [DOI 10.48550/arXiv.2608.11632](https://doi.org/10.48550/arXiv.2608.11632). |
| `santosgrueiro2026committime` | **Temporary Authority, Permanent Effects: Commit-Time Authorization for LLM Agents**. Igor Santos-Grueiro. | 2026; v1, submitted 11 July 2026, 21:48:53 UTC. Only v1 is listed. | [Versioned arXiv record](https://arxiv.org/abs/2607.10487v1); [DOI 10.48550/arXiv.2607.10487](https://doi.org/10.48550/arXiv.2607.10487). |

All three DOI links resolved to their matching arXiv abstract pages. The latter two initially returned an internal error in the browser tool; direct read-only HTTP retrieval subsequently returned status 200 with the matching arXiv destination. Metadata is therefore not inferred from identifier patterns.

## Attribution checks and qualification

- **Cordon: PASS.** The current description of a task-level boundary combining staged local/external effects, lineage, scoped approval and recovery is supported by Sections 3.1–3.4, Table 2 (scoped approval), and Sections 4.1/4.4–4.6. Avoid implying automatic rollback of already released external effects: its guarantee distinguishes reversible local state from external compensation/audit. The current sentence does not make that overclaim. [Primary full text](https://arxiv.org/html/2606.17573v1).
- **Continuity Kernel: PASS.** The introduction explicitly includes proposal identity, predecessor state, pre-state authority and acquired evidence in the atomic activation unit; Sections 2.2 and 3 explain the proposal/evidence seal and commit-time checks. The current attribution is accurate. Do not position this source as lacking proposal-identity binding. [Primary full text](https://arxiv.org/html/2608.11632v1).
- **Commit-time authorization: PASS.** The abstract, Section 3 and Section 6's reporting discussion support the four boundary conditions and the separation of endpoint utility from authorized completion. The current summary makes no unsupported claim about universal effectiveness. Stronger enforcement claims would require its protected-surface and emitted-evidence qualifications. [Primary full text](https://arxiv.org/html/2607.10487v1).

**Publication-status note:** no verified published successor was found in the targeted title searches or arXiv records. Cordon's HTML includes a EuroSys ’27 template header and the year 2027, but its arXiv submission history is 2026 v1, and the first author's own [publication list](https://zhengchencs.github.io/publications/) labels it “arXiv 2026.” Retain the verified preprint description; do not infer conference acceptance, proceedings pages or an ACM DOI from template text. No source contradiction requires changing the substantive Section 2.3 sentences.

## Ready-to-paste bibliography entries

Insert these after the AgentDojo entry and before Alloy, preserving the current numeric `natbib`/embedded-`thebibliography` style and first-citation order:

```latex
\bibitem{chen2026cordon} Chen Z, Liu H, Xu D, Dong D, Li J, Pu B, Zhai J (2026) Cordon: Semantic Transactions for Tool-Using LLM Agents. arXiv preprint arXiv:2606.17573v1. \url{https://doi.org/10.48550/arXiv.2606.17573}.
\bibitem{he2026continuity} He J, Yu D (2026) Beyond Memory: A Transactional Continuity Kernel for Long-Lived AI Agents. arXiv preprint arXiv:2608.11632v1. \url{https://doi.org/10.48550/arXiv.2608.11632}.
\bibitem{santosgrueiro2026committime} Santos-Grueiro I (2026) Temporary Authority, Permanent Effects: Commit-Time Authorization for LLM Agents. arXiv preprint arXiv:2607.10487v1. \url{https://doi.org/10.48550/arXiv.2607.10487}.
```

## Minimal in-text replacement

Replace only the three author/year/arXiv-link parentheticals in the existing paragraph with the corresponding `\citep{...}`. The resulting three sentences are:

```latex
Cordon \citep{chen2026cordon} stages local changes and external effects within a task-level transaction, with lineage, scoped approval and recovery. Continuity Kernel \citep{he2026continuity} binds proposal identity, predecessor state, pre-state authority and evidence to atomic state activation. Commit-time authorization \citep{santosgrueiro2026committime} checks whether authority remains fresh, causally prior, effect-bound and eligible at durability, and separates authorized completion from endpoint success.
```

Keep the surrounding AgentDojo and present-paper comparison sentences unchanged.

## bib-validate checks and limitations

Applied `C:/Users/lenovo/.agents/skills/bib-validate/SKILL.md`, including its embedded-bibliography cross-reference, metadata/DOI and preprint-status guidance, narrowly to this requested insertion. The active manuscript uses `thebibliography`; the baseline's historical `.bib` file is not its active reference source. At inspection, all 17 existing cited keys had entries and none were unused; the three proposed keys do not collide with existing keys. The three current bare hyperlinks are not unresolved LaTeX keys, but adding them as formal references makes their citation treatment consistent.

Paperpile and `scholarly` CLI/MCP capabilities were unavailable. Per the skill's graceful-degradation rule, reference-manager synchronization is **not assessed**, rather than classified as missing or fabricated. Primary arXiv abstract pages, full HTML papers and the Cordon author's publication list were read directly. Report routing is limited to this explicitly requested audit file; no review index, manuscript or reference-manager write was performed. Compile/cross-reference verification after insertion remains the owning manuscript editor's step.

## Post-insertion editorial integrity check

**PASS — no actionable issue found.** Compared active `main.tex` and `supplement.tex` with `qa/before-final-polish/` after the three entries were inserted. This was a read-only source comparison, not a raw-data rerun.

- All eight main and two supplement display-equation blocks are unchanged. All two main and nineteen supplement table-content blocks are unchanged, including scientific cells and denominators.
- The complete prospective-methods section is unchanged. Original versus selected supplementary scope, pre-response selection, retained failures/unknowns, the exploratory A-only bootstrap, conditional recovery interpretation, and the explicitly post hoc sensitivity view remain stated. The supplemental methods/results prose is unchanged by this polish.
- The shortened abstract's mean extra-call figures (original B 1; supplementary A 1.60) agree with the verified outputs. Detailed recovery counts, medians, latency and completion intervals remain in Results. The new statement permitting multiple legal recovery sequences is supported by the observed reuse and reauthorization paths; no unsupported empirical claim was introduced.
- Main now contains exactly three images: concept, prospective pair design, and follow-up behavior/cost comparison. The evidence-chain and original recovery-path figures are present in the supplement with their substantive captions preserved. All six referenced image files exist. Both documents have zero unresolved local references and zero duplicate labels.
- Active main has twenty bibliography entries and twenty cited keys, with no missing, unused or duplicate keys. The three inserted entries and their attributions match the primary-source verification above. The remaining seventeen entries are unchanged.

Source fingerprints at this check: `main.tex` SHA-256 `74104e2679292940481b2b102ee25e4e14bd567aae72220c8f516a8635fc1860`; `supplement.tex` SHA-256 `cd02015a18611b75c9afff21dda8380924338de280f0331a0800462fbf97906d`. PDF layout/compilation remains a separate check.
