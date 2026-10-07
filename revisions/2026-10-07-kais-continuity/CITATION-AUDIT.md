# Citation and positioning audit

Audit date: 7 October 2026. Scope: the immutable reference revision's `main.tex`, `supplement.tex`, inline 17-entry bibliography, and the preserved baseline `filtered.bib`. This audit did not edit the reference manuscript. It checks the manuscript's actual literature claims and the closest directly linked neighboring work, rather than claiming an exhaustive literature search.

## Main conclusion

The strongest positioning is a correction-specific execution contract and a paired study of what its enforcement makes a continuing agent do. Generic approval, exact action binding, transactional persistence, provenance, separation of utility from authorization, and feedback-driven recovery all have prior art. The existing manuscript largely respects those boundaries. Two close execution-oriented preprints should be acknowledged in the third related-work block: commit-time authorization and Cordon. Their omission is more important than adding another general agent survey.

## Priority changes

1. **Add the closest omitted execution comparisons.** [Temporary Authority, Permanent Effects](https://arxiv.org/html/2607.10487v1), by Igor Santos-Grueiro, studies authority validity at the durable-effect boundary and explicitly distinguishes endpoint success from authorized completion. [Cordon](https://arxiv.org/html/2606.17573v1), by Zheng Chen and colleagues, groups staged effects, lineage, scoped approval and recovery within task-level transactions. Neither should be described as merely a per-call approval system.
2. **Keep the positive, narrow contribution.** The paper varies reviewed-instance equality while preserving the corrected authorized value and retained context. That is a sharper claim than inventing approval, integrity-aware evaluation, or recovery. A missing keyword in a prior paper does not establish that its framework cannot encode correction; avoid such exclusion claims.
3. **Remove the bibliographic footnote.** The current Continuity Kernel footnote contains a full bibliographic description. [KAIS author instructions](https://link.springer.com/journal/10115/submission-guidelines) disallow bibliographic details in footnotes. Mention posted preprint versions in ordinary text, with identifying arXiv links. The same instructions restrict the formal reference list to published/accepted cited works.
4. **Use more precise PROV wording.** Replace “PROV-DM separates entities, activities and agents” with “PROV-DM models entities, activities, agents and their responsibility relations.” The model permits an agent also to be an entity or activity.

## Proposed third related-work block

Heading: Trustworthy execution and recovery

AgentDojo separates task utility from security outcomes in interactive tool environments. Recent preprints also make authorization part of the execution boundary. Cordon (Chen et al., 2026; arXiv:2606.17573) stages local changes and external effects within a task-level transaction, including lineage, scoped approval and recovery. Continuity Kernel (He and Yu, 2026; arXiv:2608.11632) binds proposal identity, predecessor state, pre-state authority and evidence to atomic state activation. Commit-time authorization (Santos-Grueiro, 2026; arXiv:2607.10487) checks whether authority remains fresh, causally prior, effect-bound and eligible at durability, and separates authorized completion from endpoint success. These works establish nearby execution and recovery boundaries. Our comparison fixes the corrected value and retained context while varying whether execution must use the reviewed candidate instance. The contract preserves the original machine value, the authorized replacement and the reviewed/executed identities as separate roles. Paired live continuations then reveal how enforcing that relation changes the next agent action, recovery path and execution cost.

Use the existing AgentDojo citation. Link each arXiv identifier directly. Move the Alloy/Kodkod/TestEra methodological sentence into formal realization if this replacement removes their only citations. Keep the first two blocks focused on (1) approval and guided correction and (2) transactions and provenance; no additional block is needed.

## Other precise replacements

- Introduction, “Correction creates a distinct continuity problem.” Suggested: “Correction exposes separate obligations for value authorization and reviewed-instance continuity.” This names the distinction without implying correction invented the general authorization gap.
- Abstract, “Instance-bound execution prevents all 17 observed substitution violations in standardized queued handoffs.” Optional precision: “Instance-bound execution rejects all 17 standardized substitutions admitted by retained-context authorization.” The original is already scoped, but the replacement makes the observed intervention explicit and avoids suggesting natural-prevalence evidence.
- Supplement, “The arXiv records ... retain these works as preprints without a linked journal reference.” Suggested: “The arXiv records accessed on 7 October 2026 do not display linked journal references; this comparison refers to the posted preprint versions.” Absence of a journal-reference field cannot prove that a work has never been accepted elsewhere.

No change is needed to the explicit acknowledgment that context-equivalent authorization can be coherent under a different accountability contract. Preserve the separation of standardized G handoffs from agent-managed N previews, the lack of observed N substitutions, bounded formal scope, the deployment coverage imbalance, and the non-equivalence interpretation of the completion interval.

## Closest-neighbor details to retain in the supplement

- [Continuity Kernel, arXiv:2608.11632](https://arxiv.org/html/2608.11632v1), Jun He and Deying Yu. Section 2.2 explicitly permits evaluators and approvers to issue signed evidence, while activation checks pre-state authority. The current description of identity, predecessor, approver evidence and lineage is supported. Its unit is an accepted branch-head transition. Do not frame this as absent exact proposal binding.
- [Commit-time authorization, arXiv:2607.10487](https://arxiv.org/html/2607.10487v1), Igor Santos-Grueiro. Sections 3 and 6 cover boundary checks, fail-closed enforcement and repair. Its evaluated emphasis is blocking authority-invalid effects, with recovery also considered. The present paper's controlled correction and reviewed-instance comparison is the appropriate differentiator.
- [Cordon, arXiv:2606.17573](https://arxiv.org/html/2606.17573v1), Zheng Chen, Hanqing Liu, Duling Xu, Dong Dong, Jialin Li, Bangzheng Pu and Jidong Zhai. Table 2, invariant I8, scopes approval to a transaction object, action, sink and time window. Sections 4.5–4.6 describe staged effects and recovery. Its unit is a task transaction.
- [MemTxn, arXiv:2607.27834](https://arxiv.org/abs/2607.27834), Hanshuai Cui and colleagues. The current supplement's source-supported admission and complete-state recovery description is supported by the authors' abstract.
- [MutMem, arXiv:2608.02843](https://arxiv.org/abs/2608.02843), Walid Saidi. Signed memory mutations and no-fork predecessor continuity are supported by the authors' abstract.

The inspected arXiv records identify the claimed works and posted 2026 versions. This audit does not independently validate their experimental results, which need not be repeated in the revised manuscript.

## Existing citation checks

All checks below use primary publications, author-hosted manuscripts, publisher records or official documentation. “Supported” means the cited descriptive claim is supported, not that the external work's experiments have been independently reproduced.

| Existing key | Checked source and result |
| --- | --- |
| langchainHITL | [Official HITL documentation](https://docs.langchain.com/oss/python/langchain/human-in-the-loop): supports interruption, approval, edited arguments and rejection feedback. It also warns that edits can cause later replanning or additional calls. Supported; do not imply approval/resumption is new. |
| yakout2011guided | [VLDB paper](https://www.vldb.org/pvldb/vol4/p279-yakout.pdf): automated suggested repairs and user feedback are explicit. Supported. |
| he2016falcon | [Publisher record](https://doi.org/10.1145/2882903.2915242): Falcon generalizes a user update and interactively validates repair queries. Supported. |
| gray1981transaction | [Original paper copy](https://www.cs.utexas.edu/~dahlin/Classes/GradOS/papers/Gray81.pdf): atomic, durable state transformations. Supported. |
| kung1981occ | [Author-hosted paper](https://www.eecs.harvard.edu/~htk/publication/1981-tods-kung-robinson.pdf): read/validation/write phases and conflict validation. Supported as foundational context; do not attribute this manuscript's exact candidate contract to OCC. |
| buneman2006curated | [Institutional paper copy](https://www.pure.ed.ac.uk/ws/files/16509719/Provenance_Management_in_Curated_Databases.pdf): Section 2.2 includes unchanged-data and copy links across transactions. Current fine-grained provenance/copy-forward comparison is supported. |
| moreau2013provdm | [W3C Recommendation](https://www.w3.org/TR/2013/REC-prov-dm-20130430/): entity/activity/agent and responsibility relations are supported; use the wording correction above. |
| clark1987integrity | [IEEE record](https://ieeexplore.ieee.org/abstract/document/6234890) and the original paper reproduced in the [NBS workshop report](https://www.govinfo.gov/content/pkg/GOVPUB-C13-53cea27893e32c65e9a4284a461829a4/pdf/GOVPUB-C13-53cea27893e32c65e9a4284a461829a4.pdf): authenticated users, controlled well-formed transactions and auditing support the comparison. |
| owaspTransactionAuthorization | [Official cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transaction_Authorization_Cheat_Sheet.html): server-side enforcement/data and a final execution gate are explicit. Supported. |
| mershad2015approval | [Author-hosted paper](https://www.cs.purdue.edu/homes/aref/papers/ic2e2015.pdf), Section IV.B: approval uses cell ID and a list/range of record timestamps. The unusually specific manuscript claim is directly supported. |
| buneman2001whywhere | [Institutional paper copy](https://www.research.ed.ac.uk/files/16509989/Why_and_Where_A_Characterization_of_Data_Provenance.pdf): why/where provenance foundation and publication metadata verified. |
| cheney2009provenance | [Author-hosted survey](https://homepages.inf.ed.ac.uk/jcheney/publications/provdbsurvey.pdf): covers why/how/where provenance. The PDF has a 2007 volume imprint but a 2009 copyright; the manuscript's conventional 2009 citation does not need changing on this evidence alone. |
| arab2018reenactment | [Author publication record](https://www.cs.iit.edu/~dbgroup/bibliography/AG17c.html) and [deposited paper](https://par.nsf.gov/servlets/purl/10048274): retroactive provenance capture for transactional histories is explicit. Supported. |
| debenedetti2024agentdojo | [NeurIPS proceedings paper](https://proceedings.neurips.cc/paper_files/paper/2024/file/97091a5177d8dc64b1da8bf3e1f6fb54-Paper-Datasets_and_Benchmarks_Track.pdf): separate utility/security evaluation in stateful tool environments is explicit. The [proceedings record](https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html) verifies title, authors, venue and DOI. |
| jackson2002alloy | [Author-group manuscript](https://groups.csail.mit.edu/sdg/pubs/2002/alloy-journal.pdf): relational specification and automated analysis support the stated use. |
| torlak2007kodkod | [Author-group paper](https://groups.csail.mit.edu/sdg/pubs/2007/tacas07-torlak-jackson.pdf): finite-bounded relational model finding is explicit. |
| marinov2001testera | [Author-hosted ASE paper](https://users.ece.utexas.edu/~khurshid/testera/testeraASEbib.pdf): abstraction/concretization between Alloy instances and concrete Java structures is explicit. |

## KAIS-facing assessment

[Official scope](https://link.springer.com/journal/10115/aims-and-scope) includes knowledge/data engineering, advanced information-system infrastructure and agent architectures. That supports a systems-facing explanation of accountable agent state changes. It does not establish likely acceptance. The strongest fit is the concrete relation linking authorization, persistent information, provenance and subsequent execution.

Other directly relevant [author requirements](https://link.springer.com/journal/10115/submission-guidelines): 150–250-word abstract, 4–6 keywords, numeric square-bracket citations, editable source plus compiled PDF, and relevant declarations. The reference abstract has about 208 whitespace-delimited tokens and six keywords. The Springer template is recommended; the page does not make its use mandatory. Maintain the data/software and AI-assistance disclosures, and provide the required authorship/conflict information in the submission interface when submitting.

## Limits of this audit

This is a literature-claim and positioning check. It does not certify all DOI redirects, independently reproduce outside papers, audit the prospective study's raw evidence, or establish that the proposed relation is absent from all prior literature. Several DOI pages failed to load; accessible author or institutional copies supported the associated checks. No citation was fabricated, no publication acceptance was inferred from a preprint record, and no immutable source file was changed.
