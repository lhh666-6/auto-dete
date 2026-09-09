# Citation ledger

This ledger records the post-R16 state of every source family cited in the
manuscript. `FULL_TEXT_PASS` means that the retained sentence was checked
against a primary full text. `OFFICIAL_SPEC_PASS` and `PRIMARY_RECORD_PASS`
denote an official specification or publisher/author record sufficient for the
bounded wording used. These labels validate attribution, not priority.

| Key(s) | Retained manuscript use | R16 status | Primary-source locator and boundary |
|---|---|---|---|
| `appel1999pca` | requester constructs a machine-checkable proof; server checks it with a small trusted base | FULL_TEXT_PASS | Princeton author PDF, architecture and implementation discussion; no claim that PCA binds the AUTO-DECTE seven-part relation |
| `fett2023dpop` | sender-constrains an OAuth token to a proof key and presenting HTTP request | OFFICIAL_SPEC_PASS | RFC 9449, abstract and protocol overview |
| `coetzee2026spttxn`, `tulshibagwale2026txtokens` | SPT-Txn binds one declared action/resource; Transaction Tokens propagate signed authorization/request context through a call chain | VERSION_PINNED_PASS | IETF Datatracker versions `-03` and `-11`; both are explicitly described as works in progress, not standards |
| `xu2026caplease` | durable authorization-consumption state for replay-resistant agent actions | FULL_TEXT_PASS / PREPRINT | version-pinned preprint; only the retained durable-consumption characterization is used |
| `liu2026pce`, `he2026dtf` | separation of proposal/certification/execution; proof-derived execution authority | FULL_TEXT_PASS / PREPRINT | arXiv full texts `2605.24462` and `2605.15228`; manuscript labels both as preprints |
| `zhu2026ebte`, `chitan2026cappcl` | typed server-held admission context; provenance-bound context plus deterministic policy admission | FULL_TEXT_PASS / VERSION_PINNED | EBTE preprint plus version-pinned Zenodo CAP+PCL report; no standards status implied |
| `li2026memtx` | staged, validated, durable agent-memory writes | FULL_TEXT_PASS / PREPRINT | MemTX preprint, validate-and-commit pipeline |
| `he2026continuity` | off-commit candidates, exact predecessor/freshness checks, and atomic installation of a complete accepted unit | FULL_TEXT_PASS / PREPRINT / HIGHEST_COLLISION | arXiv `2608.11632`; used to disclaim general candidate/authority-separation and atomic-activation novelty |
| `zhou2026latticemind` | write-time claim reconciliation, explicit claim status, supersession, and provenance-aware current memory | FULL_TEXT_PASS / PREPRINT / HIGHEST_COLLISION | arXiv `2608.08236`; comparison is limited to relations reported in public v1 |
| `zhan2026authoritycollapse` | source-authority constraints can be erased while claim content survives consolidation | FULL_TEXT_PASS / PREPRINT / HIGHEST_COLLISION | arXiv `2608.01679` v2; used for authority-collapse framing, not as an admission protocol |
| `saidi2026mutmem` | cryptographically authorized persistent-memory weight mutation bound to provenance and predecessor history | FULL_TEXT_PASS / PREPRINT / HIGH_COLLISION | arXiv `2608.02843`; explicitly distinguished from admission of a non-authoritative field candidate |
| `cui2026memtxn` | answer-model-external transaction boundary for source-supported update, visibility, and recovery | FULL_TEXT_PASS / PREPRINT / HIGH_COLLISION | arXiv `2607.27834`; kept distinct from `li2026memtx` |
| `salas2026governed` | governed execution through versioned authority/fact state and dependency provenance | FULL_TEXT_PASS / PREPRINT | arXiv `2608.12761`; used for correct-versus-governed distinction |
| `delattre2026cage` | joint certification of typed-return source-binding and numerical uncertainty | FULL_TEXT_PASS / PREPRINT | arXiv `2607.29190`; authorization-theory neighbor, not a persistent-state admission protocol |
| `bhardwaj2026superlocalmemory` | governed admission, generation fencing, transaction verification, and completion manifests | FULL_TEXT_PASS / PREPRINT | arXiv `2608.08253` v2; used to disclaim governed-write novelty |
| `nakayashiki2026staleconstraints` | immutable provenance can remain reachable while agents fail to revisit superseded constraints | FULL_TEXT_PASS / PREPRINT | arXiv `2608.25553` v3; used as empirical freshness motivation |
| `liu2026toolgate` | Hoare-style pre/postcondition checks around tool execution and typed symbolic-state update | FULL_TEXT_PASS / HIGH_COLLISION_NARROWED | ACL 2026 Findings full text, Sections 3.2--3.5; invalidates broad verified-state-commit novelty but does not supply the complete seven-part relation |
| `choong2026capchain` | field-scoped capability and current provenance predecessor checked before persistent reducer merge | FULL_TEXT_PASS / HIGH_COLLISION_NARROWED | Applied Sciences 16(15):7776, Sections 4.2--4.4 and Algorithm 1; invalidates broad capability/provenance novelty but its admitted update is one incoming field/value operation, not the complete seven-part relation |
| `greshake2023indirect` | untrusted content can be interpreted as instructions and alter external API use in LLM-integrated applications | FULL_TEXT_PASS | ACM AISec 2023 paper, DOI `10.1145/3605764.3623985`; used only to motivate the indirect-prompt-injection threat |
| `debenedetti2024agentdojo` | AgentDojo separates utility and security evaluation over 97 tasks and 629 security cases | FULL_TEXT_PASS | NeurIPS 2024 Datasets and Benchmarks paper, DOI `10.52202/079017-2636`, pp. 82895--82920; R21 is expressly not presented as an AgentDojo-scale benchmark |
| `arab2016rcsi`, `arab2018reenactment`, `arab2019thesis` | retrospective multi-version transaction provenance and reenactment | FULL_TEXT_PASS | primary papers and dissertation; text expressly distinguishes retrospective explanation from prospective authorization |
| `buneman2001whywhere` | why-provenance and where-provenance distinguish why an output exists from where its values originate | FULL_TEXT_PASS | ICDT 2001 primary paper, DOI `10.1007/3-540-44503-X_20`; used as provenance vocabulary, not as an authorization or admission protocol |
| `cheney2009provenance` | surveys why-, how-, and where-provenance in databases | FULL_TEXT_PASS | Foundations and Trends in Databases survey, DOI `10.1561/1900000006`; supports only the taxonomy and database-provenance background |
| `moreau2011opm` | the Open Provenance Model supplies a technology-independent causal-history vocabulary | FULL_TEXT_PASS | Future Generation Computer Systems OPM v1.1 specification paper, DOI `10.1016/j.future.2010.07.005`; no claim that OPM supplies candidate-bound authorization or admission |
| `moreau2013provdm` | W3C PROV models entities, activities, agents, derivation, and responsibility | OFFICIAL_SPEC_PASS | W3C Recommendation `REC-prov-dm-20130430`; used only for general provenance vocabulary and responsibility relations |
| `dai2026harnesses` | a source-level comparison reports explicit extension seams across three LLM agent harnesses | FULL_TEXT_PASS / PREPRINT | arXiv `2608.23953` v1; supports the bounded architectural-comparison sentence, not equivalence among harnesses or authority guarantees |
| `deepseek2026architecture` | DeepSeek Harness registers model-facing capabilities on `ctx.tools` and routes execution through a guarded runtime pipeline | OFFICIAL_SPEC_PASS / VERSION_PINNED | official architecture documentation pinned at commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28`; supports only the exercised harness integration boundary |
| `jackson2002alloy`, `torlak2007kodkod` | finite-scope relational analysis through SAT-based model finding | FULL_TEXT_PASS | Alloy and Kodkod primary papers; manuscript states bounded outcomes, never unbounded proof |
| `marinov2001testera` | concretization of Alloy-generated inputs and abstraction of Java outputs | FULL_TEXT_PASS | TestEra primary paper, architecture/mapping description |
| `dennis2006sat`, `galeotti2013taco` | bounded program/specification translation and finite execution-space search | FULL_TEXT_PASS | primary SAT-based checker papers; wording separated from TestEra's bidirectional mappings |
| `sullivan2017alloymutation`, `jia2011mutation`, `just2014mutants` | mutation sensitivity is useful but killed mutants are neither universal necessity proofs nor substitutes for real faults | FULL_TEXT_PASS | primary mutation-analysis sources; manuscript reports finite denominators and exact operators |
| `claessen2000quickcheck`, `claessen2009pulse`, `musuvathi2008chess` | stateful property generation and controlled schedule exploration | FULL_TEXT_PASS | QuickCheck, PULSE, and CHESS primary papers; no guarantee is transferred to the present implementation |
| `kingsbury2020elle` | independent checking of observed transactional histories | FULL_TEXT_PASS | PVLDB Elle paper; use limited to independent history checking |
| `collberg2016repeatability` | disclosed source differs from code that builds and executes | FULL_TEXT_PASS | primary repeatability study; sentence no longer shares unsupported clauses with the other artifact sources |
| `hermann2020artifacts` | artifact packages should be documented, consistent, complete, and exercisable | FULL_TEXT_PASS | author preprint and ACM record; exact evaluation criteria retained |
| `klees2018fuzz` | configuration and repetition can change fuzzing-evaluation conclusions | FULL_TEXT_PASS | primary fuzzing-evaluation paper; claim isolated from generic artifact-build wording |
| `kessel2024openscience`, `liu2024artifacts` | JSS examples of executable experiment descriptions and durable artifact practice | PRIMARY_RECORD_PASS | JSS/ScienceDirect article records and full texts; used only as venue-specific exemplars |
| `stachtiari2018correctness`, `alam2021dbverify`, `song2023continuous`, `coppa2024concolic` | JSS examples connecting formal/analysis methods, executable software, and empirical assessment | PRIMARY_RECORD_PASS | JSS/ScienceDirect article records and full texts; no stronger common methodology is attributed |

## Prohibited use

- Do not cite any work as establishing Auto-Decte's complete dual-value field-admission relation unless that exact relation is reported.
- Do not describe preprints or active Internet-Drafts as standards or settled results.
- Do not use a DOI landing-page abstract to support a stronger full-text claim.
- Do not keep an attribution sentence that R16 cannot locate in the primary source.

## Current disposition after the 2026-09-03 collision update

- All active citation keys resolve to the bibliography.
- All preprints, reports, and Internet-Drafts are labeled by status and version.
- The nearest new public artifacts were checked and forced removal of broad
  admission, transaction, candidate/authority-separation, freshness, activation,
  mutation, and provenance novelty claims. The retained claim is the dual-value
  human-Correction specialization plus its five-class failure-distinguishability
  characterization and bounded formal--concrete evidence.
- No `CLAIM_PENDING` or `HIGH_COLLISION_PENDING` item remains.
