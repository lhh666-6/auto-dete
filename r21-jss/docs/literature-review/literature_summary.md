---
title: Literature synthesis for certificate-bound authoritative admission
_version: synthesis_v2
_produced: 2026-08-27T03:44:27+08:00
_depends_on:
  - literature_summary.bib@bib_v2#e454499a0c97af2948822884c710f479e9d6e8de257b39916f27e18b09096df5
  - merged_candidates.json@v1#ac929d6
  - doi_verification-v3.json@v3#518cf90
  - deep-verify/full_report.json@v1#569c021
  - r18-provenance-foundations@v1#W3C-PROV-DM+3-DOI-Crossref
_verified: 2026-08-27T03:44:27+08:00
_verification_report: reviews/bib-validate/2026-08-27.md
_status: VERIFIED
---

# Literature synthesis for certificate-bound authoritative admission

## Scope and research question

This synthesis supports an evidence-locked Journal of Systems and Software (JSS) paper about a narrow systems relation: an AI-produced candidate is not itself authoritative; a separately attributable decision may admit an explicit value only when it is bound to the exact candidate, target record and field, persisted evidence identity, and expected pre-version; one valid multi-field decision creates one successor record version with a complete durable field-source map; correction preserves the candidate while allowing an explicitly authorized different value; malformed or substituted bindings fail without partial effect.

The search asks two questions. First, which parts of that relation are already occupied by authorization, provenance, transactional state, or agent-safety research? Second, which methodological precedents justify the paper's bounded relational analysis, formal--concrete projection, executable fault catalogue, stateful/concurrent tests, fixed-grid cost characterization, and hash-linked artifact package?

## Search and verification protocol

- **Cut-off:** 27 August 2026; no lower year bound.
- **Discovery tracks:** (A) certificate/proof/transaction-bound authority and mutation provenance; (B) bounded relational analysis, executable refinement, mutation, concurrency, and reproducibility; (C) JSS venue and in-venue method precedents.
- **Candidate set:** 46 records: 21 substantive neighbors, harness sources, and foundations; 15 methodological precedents; and 10 JSS papers.
- **Identity gate:** the 44 R18 records retain their prior Crossref/DataCite or official-source checks. The R19 supplement adds the arXiv record for Dai's harness analysis and the commit-pinned official DeepSeek Harness architecture document; all 46 identities were checked against their primary records.
- **Degraded integrations:** Paperpile and the local `scholarly` CLI were unavailable. Paperpile membership is therefore unconfirmed; no record is labelled `NEW` or `IN PAPERPILE`.
- **Evidence boundary:** bibliographic identity and abstract/method-level relevance are verified here. Sentence-level claims made in the manuscript still require R16 source-to-claim verification against the primary full text.

## Priority reading order

1. **ToolGate** (`liu2026toolgate`) — the strongest published collision risk for contract-grounded pre/post gates and verified symbolic-state commit.
2. **CapChain** (`choong2026capchain`) — the strongest published collision risk for capability-token enforcement, field gates, and signed provenance at a multi-agent state transition.
3. **PCE and DTF** (`liu2026pce`, `he2026dtf`) — the closest certificate/proof-derived authorization framing; both are current preprints and must not be presented as settled standards.
4. **Provenance foundations** (`buneman2001whywhere`, `cheney2009provenance`, `moreau2011opm`, `moreau2013provdm`) — the vocabulary for origin, derivation, responsibility, and interoperable provenance; foundational context rather than the paper's novelty.
5. **Transactional provenance** (`arab2018reenactment`, `arab2016rcsi`) — the principal lineage for versioned database-update provenance and replay, but descriptive rather than prospective authorization.
6. **TestEra and Alloy** (`marinov2001testera`, `jackson2002alloy`) — the clearest method lineage for bounded relational analysis and abstraction/concretization between a formal relation and an executing implementation.
7. **Alloy mutation and Elle** (`sullivan2017alloymutation`, `kingsbury2020elle`) — precedents for non-equivalent model mutants, independent checkers, histories, and interpretable counterexamples.
8. **JSS theory--tool--evidence exemplars** (`stachtiari2018correctness`, `alam2021dbverify`, `coppa2024concolic`, `song2023continuous`) — concrete models for positioning a formal method together with an implementation, empirical evidence, limitations, and open artifacts.
9. **Harness architecture and external verifiability** (`dai2026harnesses`, `deepseek2026architecture`) — the direct motivation and pinned host contract for the R19 integration, without treating one harness experiment as a general production validation.

## Thematic synthesis

### 1. Generation, certification, and authority are distinct phases

Proof-carrying authentication established the general idea that an untrusted requester can carry a machine-checkable justification evaluated by a small trusted checker (`appel1999pca`). Recent agent-safety work moves this boundary closer to AI actions. PCE separates proposal, certification, and execution (`liu2026pce`); DTF derives a short-lived execution identity from structured intent and justification (`he2026dtf`); SPT-Txn and Transaction Tokens bind authority and context to a transaction (`coetzee2026spttxn`, `tulshibagwale2026txtokens`); DPoP sender-constrains an OAuth token to a proof key and request (`fett2023dpop`); CapLease makes authorization consumption durable and replay resistant (`xu2026caplease`).

The literature therefore already occupies broad claims such as “generation is not permission,” “authority should be bound to context,” “tokens should be non-transferable,” and “replay should be prevented.” AUTO-DECTE cannot claim any of those primitives. Its defensible unit is the more specific candidate-to-authoritative-successor relation, including exact persisted evidence and expected-version binding, correction semantics, a complete successor source snapshot, and no-partial-effect rejection.

**Negative evidence:** no verified source in this cluster combines all seven relation elements in one model and executable implementation. This is a search result, not a legal novelty opinion or proof of absence.

### 2. Verified agent state and provenance are newly crowded

ToolGate keeps a trusted symbolic state, checks preconditions, invokes a tool, verifies postconditions, and only then commits the result (`liu2026toolgate`). CapChain inserts capability-aware enforcement and tamper-evident provenance at a multi-agent state merge layer (`choong2026capchain`). MemTX stages agent-memory writes under transactional validation and commit (`li2026memtx`). EBTE binds server-checked action claims to intent, payload, tool, provenance, and freshness (`zhu2026ebte`). CAP+PCL binds orchestration context to deterministic policy admission (`chitan2026cappcl`).

These papers invalidate any broad novelty language about “verified state evolution,” “capability-bound state writes,” “provenance-aware agent state,” “transactional AI memory,” or “contract-gated commit.” The residual distinction is not that AUTO-DECTE has a gate, token, provenance chain, or transaction. It is that authority names one persisted candidate and one explicit authorized value at a precise record/field/evidence/pre-version boundary, and that the successor stores a total field-source snapshot while corrections preserve the machine candidate.

**Negative evidence:** ToolGate and CapChain do not appear to provide the exact correction-aware candidate binding, expected authoritative record version, atomic multi-field successor, complete successor-wide source map, and matching substitution/corruption catalogue. R16 must verify any manuscript sentence making this comparison against their full texts.

### 2.1 Plugin harnesses expose a concrete external-verifiability boundary

Dai's comparative analysis of three LLM agent harnesses identifies external verifiability as absent from the examined architectures (`dai2026harnesses`). The result is a recent preprint and is used here as a scoped architectural observation, not as a universal statement about agent platforms. The official, commit-pinned DeepSeek Harness architecture describes a plugin-oriented composition model in which tools are registered through the plugin context and registrations are unwound when the plugin unloads (`deepseek2026architecture`).

R19 connects these sources through a deliberately narrow experiment: a pinned DSH plugin exposes candidate proposal and certificate verification, while the host retains the separate confirmation operation that can create an authoritative successor. Ten declared cases check schema exposure, candidate-only proposal, host-only confirmation, correction, stale/corrupt rejection, absence of a model-callable confirmation tool, fail-closed bridge behavior, unload semantics, and manifest tamper detection. This demonstrates an externally inspectable adapter boundary for one release and fixture; it does not show end-user utility, industrial scale, arbitrary-model safety, or superiority over other harnesses.

### 3. Transaction provenance explains history but does not grant authority

Classical database provenance separates why an output exists from where its values originated, and later surveys organize why-, how-, and where-provenance as related but non-equivalent explanations (`buneman2001whywhere`, `cheney2009provenance`). OPM and W3C PROV supply technology-independent and interoperable vocabularies for entities, activities, agents, derivations, and responsibility (`moreau2011opm`, `moreau2013provdm`). These foundations establish how to represent and exchange lineage; they do not themselves authorize a proposed state transition.

Reenactment and MV-semiring work reconstruct how tuple versions arise from update histories under snapshot-based isolation (`arab2018reenactment`, `arab2016rcsi`, `arab2019thesis`). This lineage is directly relevant to durable lineage, concurrency-aware reconstruction, and historical what-if reasoning. It does not by itself establish whether a proposed value was authorized before commit, whether authority referred to the exact AI candidate and evidence object, or whether a rejected decision left authoritative state unchanged.

The distinction matters for the paper's contribution statement: provenance is a necessary representational ingredient, not the novelty. AUTO-DECTE uses prospective admission constraints plus durable successor provenance, whereas transactional reenactment primarily supplies retrospective derivation and explanation.

**Negative evidence:** no located transaction-provenance source supplies the complete candidate/decision/correction contract. Conversely, AUTO-DECTE does not replace general transaction provenance, query-level lineage, or reenactment.

### 4. Bounded analysis and formal--concrete projection require explicit scope

Alloy and Kodkod justify finite-scope relational model finding and counterexample search (`jackson2002alloy`, `torlak2007kodkod`). Their key methodological lesson is lexical discipline: an UNSAT command is a result within a declared scope, not an unbounded proof. TestEra makes abstraction and concretization explicit by executing Java and projecting results back to an Alloy relation (`marinov2001testera`). SAT-based code verifiers similarly connect program executions to relational constraints under finite bounds (`dennis2006sat`, `galeotti2013taco`).

AUTO-DECTE's formal evidence should therefore be presented as a bounded model plus selected executable projections. The paper must state the exact scopes, command counts, SAT/UNSAT meaning, concrete projection denominator, and mapping assumptions. It may not infer SQLite refinement for all executions merely because a finite wrapper catalogue and the Alloy model both pass.

Alloy mutation work motivates non-equivalent constraint mutants and tests that distinguish their behavior (`sullivan2017alloymutation`). General mutation research clarifies that killed mutants are an adequacy signal, not proof that every constraint is globally necessary or that synthetic mutants represent all real faults (`jia2011mutation`, `just2014mutants`).

**Negative evidence:** no located paper uses the exact combination of whole-conjunct Alloy ablation, a corrupt item paired with a Full-valid item, matching rejection/stutter, and a database-level no-partial-effect projection. This supports describing the protocol as a specific design choice, not as an established sufficient criterion.

### 5. Stateful and concurrent evidence is configuration-bound

QuickCheck supplies the lineage for executable properties, generated inputs, and replayable counterexamples (`claessen2000quickcheck`). PULSE and CHESS demonstrate that controlled schedules and deterministic replay can expose concurrency faults that ordinary unit tests miss (`claessen2009pulse`, `musuvathi2008chess`). Elle shows how an independent checker can infer and explain anomalies from client-observed histories (`kingsbury2020elle`).

These precedents support AUTO-DECTE's deterministic state-machine profiles, failpoints, real thread/process contenders, raw histories, and independent relational oracle. They also enforce a limitation: Erlang scheduling, CHESS-controlled events, distributed-database histories, and the frozen Windows/Python/SQLite configuration are not interchangeable. The reported one-winner behavior and cost measurements are observations for declared tests and configurations, not universal liveness, isolation, or deployment claims.

**Negative evidence:** no external study reproduces AUTO-DECTE's exact SQLite configuration, failpoints, authority-object checks, or fixed performance grid. Internal rerun and manifest checks are not an external independent reproduction.

### 6. Reproducible artifacts need more than a green local run

Fuzzing-evaluation research warns that configuration, repetitions, budgets, and complete reporting determine whether comparisons are interpretable (`klees2018fuzz`). Repeatability audits show that source availability does not guarantee buildability or executability (`collberg2016repeatability`). Artifact-evaluation research emphasizes documented, consistent, complete, and exercisable packages (`hermann2020artifacts`). JSS-specific studies additionally motivate executable experiment descriptions and durable artifact hosting (`kessel2024openscience`, `liu2024artifacts`).

These sources support locked dependencies, environment capture, non-overwriting failures, one command surface, raw-to-paper lineage, manifests, and tamper probes. They do not establish that those mechanisms are sufficient for external reproducibility. The final paper must distinguish “locally verified frozen package” from “independently reproduced,” and R17 must perform a clean-extraction release test.

### 7. JSS rewards a theory--implementation--evidence package

JSS precedents commonly connect a formal or rigorous method to a concrete tool, executable model, case, or empirical evaluation. Correctness-by-construction work links formal requirements to executable models (`stachtiari2018correctness`); database verification conditions are realized in a prototype and evaluated (`alam2021dbverify`); continuous verification joins formal reasoning, implementation, cost, and open material (`song2023continuous`); SPIN is connected to concrete Java traces (`adalid2014spin`); concolic consistency checks expose implementation defects across engines (`coppa2024concolic`); hybrid specification is evaluated rather than asserted (`liu2021hybrid`).

The venue fit is therefore strong for a regular research article, provided the paper makes its formal--concrete bridge visible, reports the fixed-grid cost results including unfavorable cells, and foregrounds threats to validity. Quantitative verification and self-adaptive-system examples reinforce the need to define uncertainty, scope, tool support, and public artifacts (`alasmari2022uncertainty`, `passler2025selfadaptive`).

## Intellectual lineage

The literature forms a five-step lineage rather than a single direct ancestor:

1. **Proof-carrying requests** establish a small trusted checker for untrusted requests (`appel1999pca`).
2. **Context- and transaction-bound authority** narrows when a credential may be exercised (`fett2023dpop`, `tulshibagwale2026txtokens`, `coetzee2026spttxn`).
3. **Agent execution/state gates** apply preconditions, postconditions, capabilities, and provenance to AI-driven effects (`liu2026pce`, `he2026dtf`, `liu2026toolgate`, `choong2026capchain`).
4. **Data and transaction provenance** supplies origin/derivation vocabularies and explains durable successors and histories (`buneman2001whywhere`, `cheney2009provenance`, `moreau2011opm`, `moreau2013provdm`, `arab2018reenactment`, `arab2016rcsi`).
5. **Bounded relational and executable checking** supplies a way to state, project, mutate, and test the composite relation (`jackson2002alloy`, `marinov2001testera`, `sullivan2017alloymutation`, `kingsbury2020elle`).

AUTO-DECTE sits at their intersection. Its contribution must be stated as a composition with an exact operational boundary, not as the invention of any step in this lineage.

## Debate and alternative interpretations

| Debate | Strongest interpretation | Conservative resolution for the paper |
|---|---|---|
| Is postcondition-verified state commit already the result? | ToolGate occupies that broad formulation. | Claim only the exact candidate/authorized-value/evidence/pre-version relation and successor source snapshot. |
| Is capability-bound provenance already the result? | CapChain occupies capability enforcement and provenance at a merge layer. | Treat capabilities and provenance as antecedents; isolate the human candidate-bound correction contract. |
| Does a certificate make an AI output authoritative? | PCE/DTF show certificates can gate actions, but certificate semantics vary. | Define the certificate fields and trusted checks explicitly; do not inherit guarantees from terminology. |
| Does bounded UNSAT prove correctness? | Alloy/Kodkod provide exhaustive search only within encoded bounds. | Say “bounded SAT/UNSAT analysis”; disclose scopes and model-fidelity risk. |
| Do killed mutants prove necessity? | Mutation work supports fault sensitivity, not universal necessity. | Report operator, denominator, non-equivalence check, and bounded interpretation. |
| Do one-winner tests prove concurrency correctness? | PULSE/CHESS/Elle show useful controlled evidence, not universal schedules. | Bind the claim to the tested implementation, workload, OS, Python, SQLite, and recorded histories. |
| Does a manifest prove reproducibility? | Artifact studies show availability/executability are separate. | Claim local integrity and rerunnability only after R17; reserve “reproduced” for an independent run. |

## Cross-cluster synthesis and residual gap

Across all clusters, the literature covers nearly every component individually: proof-carrying authorization, transaction-bound tokens, verified postconditions, capability-aware state transitions, standard provenance interchange, database why/how/where provenance, signed provenance, transactional memory admission, multi-version update lineage, bounded relational analysis, abstraction/concretization, mutation testing, stateful generation, controlled scheduling, anomaly checking, and artifact evaluation.

The residual gap that survives this search is relational rather than component-level. No verified work was found that requires, in one operational contract:

1. a persisted AI-produced candidate distinct from the committed authoritative fact;
2. attributable authority naming that exact candidate and an explicit authorized value;
3. binding to record, field, persisted evidence identity, and expected pre-version;
4. one decision atomically creating a nonempty multi-field successor record version;
5. a complete durable per-field source map in the successor;
6. correction that preserves the candidate while committing a different explicit value; and
7. named per-conjunct counterexamples plus executable rejection of matching substitution/corruption families with zero partial effect.

This is the only novelty formulation supported by the present search. “No verified work was found” must remain a scoped search statement, not an absolute priority claim.

## Structured gaps and why they matter

### Conceptual gap

Existing work often binds authority to an action, tool call, token, proof, or state transition. It does not consistently distinguish the identity of a persisted machine candidate from the explicit value a human authorizes, especially when correction changes the committed value without erasing the original candidate. This matters because conflating proposal and authority makes later audit unable to determine what the machine proposed, what a person approved, and what actually became authoritative.

### Methodological gap

Formal models, concrete implementations, mutation tests, and concurrency checks are often evaluated separately. The missing method is an explicit, mutation-tested projection from persisted pre/post states into the same relation used by the bounded model, combined with a finite independent fault catalogue and no-partial-effect assertions. This matters because two green but disconnected suites do not establish that the implementation realizes the model.

### Contextual gap

Agent-memory, tool-use, OAuth, and transaction-provenance systems optimize different trust and isolation boundaries. None directly evaluates a local authoritative-record admission service with persisted evidence identity, per-field source snapshots, correction, SQLite CAS, and a complete lifecycle package. This matters because security and consistency guarantees do not transfer automatically across execution, memory, token, and record-admission contexts.

### Evaluation gap

The literature supports rigorous artifacts but does not make a source manifest, BOM-linked normalized inputs, non-self-referential evidence manifest, and deliberate tamper probe a sufficient reproducibility theorem. This matters because the paper must report what the package actually establishes—integrity and local rerunnability—without upgrading it to independent reproduction.

## Claim rules for the JSS manuscript

- Use **“bounded relational analysis”**, not an unqualified proof claim.
- Describe **selected formal--concrete projections** and their finite denominator; do not claim full SQLite refinement.
- Call the 35-case result **complete for the declared catalogue**, not exhaustive over arbitrary faults.
- Report the two negative 128-field sparse-change admission deltas; do not select only favorable cells.
- Bind trace, admission, and storage measurements to the frozen Windows/Python/SQLite grid; do not infer asymptotic or industrial performance.
- State novelty only for the seven-part combination above. Treat certificates, capabilities, provenance, CAS/OCC, append-only traces, mutation, and reproducibility mechanisms as prior ingredients.
- Treat ToolGate and CapChain as mandatory R16 full-text comparisons.
- Quarantine any AI-generated diagram as non-submitted ideation. The submitted JSS figure must be independently constructed from the verified system specification and exported from an editable vector master because the current JSS guide prohibits AI-created or AI-altered submitted images.

## Annotated bibliography

| Key | Pillar | Annotation and connection to AUTO-DECTE | Confidence |
|---|---|---|---|
| `liu2026toolgate` | Closest collision | Verified pre/post tool execution and symbolic-state commit; narrows all broad verified-state-evolution claims. | A |
| `choong2026capchain` | Closest collision | Capability-aware merge, field gates, and signed provenance; narrows capability/provenance novelty. | A |
| `liu2026pce` | Certificate boundary | Separates proposal, certification, and execution; lacks the exact record-field correction contract. | B |
| `he2026dtf` | Proof-derived authority | Proof-bound execution identity and evidence chain; closest generic governed-mutation framing. | B |
| `li2026memtx` | Transactional agent state | Validate-and-commit for evidence-bearing memory; different target and provenance semantics. | B |
| `zhu2026ebte` | Server-side claims | Binds action claims to intent, payload, provenance, and freshness; governs tool effects, not candidate admission. | B |
| `xu2026caplease` | Replay-resistant authority | Durable Issue--Prepare--Commit authorization consumption; no per-field successor provenance. | B |
| `chitan2026cappcl` | Context attestation | Provenance-bound context plus deterministic policy admission; version-specific Zenodo record required. | B |
| `coetzee2026spttxn` | Transaction-bound token | One action/resource/policy, canonical intent and receipts; active individual draft, not a standard. | B |
| `tulshibagwale2026txtokens` | Transaction context | OAuth WG draft for propagating integrity-protected transaction context; still work in progress. | B |
| `fett2023dpop` | Sender constraint | Standard proof-of-possession and replay-detection antecedent; binds request/presenter, not candidate/value. | A |
| `appel1999pca` | Foundational authorization | Machine-checkable proof attached to a request; conceptual ancestor for small trusted checkers. | A |
| `arab2018reenactment` | Transaction provenance | Multi-version update lineage and reenactment; retrospective explanation rather than prospective authority. | A |
| `arab2016rcsi` | Concurrency-aware lineage | Reenactment under read-committed snapshot isolation; no authorization semantics. | A |
| `arab2019thesis` | Provenance synthesis | Broad treatment of transactional updates and versioned workspaces; prefer peer-reviewed article where possible. | B |
| `buneman2001whywhere` | Database provenance foundation | Distinguishes why an output exists from where an output value originated; foundational descriptive lineage, not prospective authority. | A |
| `cheney2009provenance` | Provenance survey | Systematizes why-, how-, and where-provenance and their relationships for databases. | A |
| `moreau2011opm` | Interchange foundation | Technology-independent causal-history model designed for provenance exchange and shared tooling. | A |
| `moreau2013provdm` | Provenance standard | W3C Recommendation for interoperable entities, activities, agents, derivations, and responsibility relations. | A |
| `dai2026harnesses` | Harness comparison | Recent three-harness architectural comparison that motivates the external-verifiability question; preprint claims remain version-sensitive. | B |
| `deepseek2026architecture` | Pinned host contract | Official DSH architecture at the tested release commit; defines the plugin/tool lifecycle against which R19 is scoped. | B |
| `greshake2023indirect` | Agent security | Establishes that untrusted data can redirect tool/API behavior through indirect prompt injection; motivates L2 without turning six cases into a security benchmark. | A |
| `debenedetti2024agentdojo` | Agent security evaluation | Separates task utility and security over 97 tasks and 629 cases in a dynamic tool environment; directly limits the interpretation of R21's one-run-per-scenario probe. | A |
| `jackson2002alloy` | Formal method | Defines lightweight relational modeling and finite-scope analysis; supports bounded claim language. | A |
| `torlak2007kodkod` | Solver foundation | Relational-to-SAT model finding; supports explicit scopes, bounds, and solver-artifact reporting. | A |
| `marinov2001testera` | Formal--concrete bridge | Explicit abstraction/concretization around real program executions; nearest projection precedent. | A |
| `dennis2006sat` | Bounded code checking | Reduces code/specification behavior to relational SAT under finite bounds; not a database refinement result. | A |
| `galeotti2013taco` | Tight bounded verification | Shows value and limits of bounded SAT checks over concrete programs. | A |
| `sullivan2017alloymutation` | Model mutation | Alloy-specific mutation and equivalent-mutant reasoning; direct support for constraint ablation design. | A |
| `jia2011mutation` | Mutation survey | Frames mutation adequacy, operators, denominators, and equivalent mutants. | A |
| `just2014mutants` | Mutation validity | Empirically limits mutant-to-real-fault inference; supports conservative necessity wording. | A |
| `claessen2000quickcheck` | Property-based testing | Generator/property/replay lineage for deterministic stateful profiles. | A |
| `claessen2009pulse` | Concurrent testing | Controlled scheduling and shrinking for race discovery; assumptions do not transfer to SQLite. | A |
| `musuvathi2008chess` | Schedule exploration | Deterministic concurrency replay; DOI-less but verified on the USENIX page. | B |
| `kingsbury2020elle` | Independent history checker | Infers anomalies from experimental histories and emits interpretable witnesses; closest oracle precedent. | A |
| `klees2018fuzz` | Evaluation design | Repetitions, fixed budgets/configurations, and complete reporting; supports non-selective frozen grids. | A |
| `collberg2016repeatability` | Artifact repeatability | Shows that availability does not ensure build/run success; supports external-clean-run caution. | A |
| `hermann2020artifacts` | Artifact evaluation | Community expectations for documented, complete, consistent, and exercisable artifacts. | A |
| `stachtiari2018correctness` | JSS formal/tool exemplar | Formal requirements, executable model, and system cases; strong venue precedent. | A |
| `alam2021dbverify` | JSS database exemplar | Verification conditions plus a database-program prototype and evaluation. | A |
| `alasmari2022uncertainty` | JSS quantitative verification | Theory, tool support, and bounded evaluation; supports clear uncertainty/scope reporting. | A |
| `song2023continuous` | JSS open evidence | Formal method, implementation, measured cost, and open materials in one paper. | A |
| `passler2025selfadaptive` | JSS recent formal systems | Model checking, concrete case, and public artifact; useful for claim-bounded positioning. | A |
| `adalid2014spin` | JSS formal--concrete trace | Connects SPIN/LTL reasoning to concrete Java execution, monitoring, replay, and tooling. | A |
| `coppa2024concolic` | JSS consistency checking | Cross-checks symbolic and concrete states across engines and reports real implementation defects. | A |
| `liu2021hybrid` | JSS hybrid specification | Integrates formal specification into a practical workflow and evaluates it rather than relying on formalism alone. | A |
| `kessel2024openscience` | JSS executable experiments | Test-driven executable experiment descriptions and repetition/reproduction concerns. | A |
| `liu2024artifacts` | JSS artifact trends | Motivates durable hosting, documentation, and discoverable research artifacts. | A |

## Confidence breakdown

| Grade | Count | Meaning |
|---|---:|---|
| A | 36 | Formal publication, standard, or official publisher/proceedings record with DOI/stable-source metadata confirmed. |
| B | 12 | Official preprint, active draft, Zenodo object, thesis, DOI-less official proceedings record, or commit-pinned project documentation; identity is verified but status/version is less stable. |
| C | 0 | No unverified or secondary-only item was admitted. |

The B set comprises six arXiv preprints, two active Internet-Drafts, one version-specific Zenodo deposit, one thesis, one DOI-less USENIX proceedings paper, and one commit-pinned official DSH architecture document. ToolGate and CapChain are A-grade collision risks even though they are very recent. The R18 supplement adds four A-grade provenance foundations; R19 adds the two B-grade harness sources used for the plugin experiment; R21 adds two A-grade prompt-injection/evaluation sources that bound the live-agent probe.

## Coverage gaps and freshness risks

- The 2026 agent-safety literature is fast-moving. Recheck arXiv versions, Crossref, ACL/IEEE/ACM proceedings, Zenodo version lineage, and IETF draft revisions immediately before submission.
- Dai's harness paper and the tested DSH release are both very recent. Recheck the preprint version and release/commit identity immediately before submission, and keep every R19 claim bound to the recorded release and fixture.
- Patent, commercial-product, GitHub, and exhaustive non-English searches were outside this academic literature sprint. The result is not a legal prior-art opinion.
- Paperpile membership and canonical user citekeys remain unverified because the integration was unavailable. The current keys are project-local and must be reconciled if Paperpile later becomes available.
- Full-text sentence-level verification remains open for every manuscript claim, especially ToolGate, CapChain, PCE, DTF, MemTX, and the JSS papers used to justify venue conventions.
- JSS author metadata, public artifact DOI/URL, CRediT roles, funding, conflicts, and corresponding-author details are author-only information and remain placeholders for the paper phase.
- JSS's current AI artwork rule conflicts with submitting an AI-derived core diagram. The compliant path is an independently constructed vector figure; editorial permission or a venue change would be required to submit AI-generated/altered artwork.

## Literature-phase handoff

The literature supports proceeding to the paper-writing stage with a sharply bounded contribution claim. The paper should be a regular JSS research article organized around: trust boundary and exact relation; bounded model; transactional realization; selected formal--concrete projection; independent catalogue and stateful/concurrent evidence; fixed-grid cost characterization; artifact lineage; and explicit threats to validity. The literature does not support production-effectiveness, industrial-validation, unbounded-correctness, universal-concurrency, asymptotic-performance, or independent-reproduction claims.
