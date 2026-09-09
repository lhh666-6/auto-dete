# PRIOR_ART_PREDICATE_MATRIX.md — Auto-Decte Pre-Alloy Novelty Gate (G1)

> Date: 2026-08-23
> Status: **G1 CONDITIONAL PASS** after adding PCE, DTF, Transaction Binding Security / SPT-Txn, transactional-update provenance, and the previously audited CAP+PCL and SAGE-Mem sources. The pass applies only to the narrow composite contribution stated below, not to any constituent mechanism.
> Method: predicate-level kill-test, not domain-relabeling. Domain difference is not used as the sole distinction.
> Stop condition for direct collision:
>
> `Authorization(exact candidate identity + authorized value) -> versioned authoritative record transition`
>
> with record/field/evidence/version non-transferability and equivalent mechanism analysis.

---

## Comparison matrix

| Work | Admitted object | Authority object | Exact identity bound | Evidence / provenance | Version / freshness | Durable target state | Non-transferability relation | Mechanism ablation | Direct collision? | Evidence source |
|---|---|---|---|---|---|---|---|---|---|---|
| **MemTX** (arXiv:2607.23929) | agent memory record/entity/attribute/value promoted from staged observation to committed/action-safe belief | validate-and-commit pipeline; permission block; source authority weight; risk-tier transaction | entity+attribute slot, permission scope, source authority, provenance DAG, validity interval; **no certificate identity, no per-field record version** | yes: evidence check, source authority, provenance edges, derivation DAG | yes: logical clock, validity interval, snapshot isolation, stale late writes | durable shared agent memory; **not** authoritative business record with per-field `fact_sources` | permission laundering blocked, but no explicit `SameValue ⇏ SameAuthority` certificate non-transferability | empirical ablations on semantic-conflict adjudication, permission inheritance, cascade repair; no Alloy-style per-conjunct C-record/C-field/C-evidence/C-version/C-auth-cert ablations | **No** | arXiv full HTML: https://arxiv.org/html/2607.23929v2 ; local `research_scout/PRIOR_ART_THREATS.md` |
| **SAGE-Mem** (OpenReview 6lJ6J3dDOx; ICML 2026 SCALE workshop) | multimodal agent memory claim `q`, promoted from evidence to durable belief | write-time defense: semantic gate, support `sup(q) >= k`, independence `indep(q) = 1`, non-conflict `conflict(q) = 0` | promoted claim + provenance/source type/channel; **no record/field/version/expectedVersion/certificate/authorization tuple** | yes: evidence vs belief, provenance, channel trust, conflict with higher-trust state | some freshness via timestamps/conflict with higher-trust state; **no explicit versioned authoritative record version/CAS** | durable agent memory; **not** authoritative business record | no authorization token/certificate non-transferability; only evidence-belief promotion strictness | empirical attack benchmarks; no 12-conjunct mechanism ablation | **No** — explicit promotion formula is support/independence/conflict, not exact candidate-certificate authorization over versioned authoritative fact fields | OpenReview full text: https://openreview.net/pdf?id=6lJ6J3dDOx ; official page: https://openreview.net/forum?id=6lJ6J3dDOx |
| **PCE / Certified Traces** (arXiv:2605.24462) | agent-proposed execution trace containing intended actions, evidence, approvals, credentials, computations, and execution conditions | Permissibility Machine issues a checkable certificate under policy `Pi`; executor acts only on certified traces | exact proposed trace and policy-induced certified language; proposed/realized trace conformance; **no fixed record/field/evidence-locator/expected-record-version tuple** | yes: supporting evidence, source lineage, approvals, proof memory, policy lineage | versioned policy and re-certification; **not a per-record optimistic version transition** | realized execution trace and proof memory; may include record modification but does not define a per-field authoritative record/source-map state machine | generation is not permission and uncertified traces cannot execute; certificate is trace-specific | formal axioms/theorems and illustrative models; research-foundation paper rather than a field-level mechanism-ablation implementation | **No direct collision; YES it pre-empts proposal/certification/execution separation and “no certificate, no execution” as novelty.** | arXiv abstract/full HTML: https://arxiv.org/abs/2605.24462 and https://arxiv.org/html/2605.24462v1 |
| **DTF / Proof-Derived Authorization** (arXiv:2605.15228) | normalized intent and concrete governed mutation `X_t` | approved Justification Proof `JP_t`; evaluator consensus; ephemeral non-transferable Execution Identity `EI_t` | mutation specification, bound state/context snapshot, policy/version, risk, action/resource/time/obligations; proof-hash attestations | yes: append-only Evidence Chain links intent, context, policy, proof, approvals, identity, mutation, outcome | context freshness and versioned policy; stale-state adversarial cases; **no explicit expectedVersion/currentVersion record CAS** | governed infrastructure mutation plus append-only authorization lifecycle | `EI_t` is per-decision, proof-derived, non-transferable, exact-resource scoped; boundary drift is rejected | mechanism ablations remove consensus, `EI`, or Evidence Chain; boundary-drift and stale-state tests | **No direct collision on the full Auto-Decte tuple, but the generic proof-bound/context-bound/non-transferable governed-mutation claim is pre-empted.** Residual novelty must be the narrower field/evidence/version/authorized-value/source-anchor batch contract and its per-conjunct conformance. | arXiv abstract/full HTML: https://arxiv.org/abs/2605.15228 and https://arxiv.org/html/2605.15228v1 |
| **EBTE** (arXiv:2607.25364) | proposed tool execution / external action | server-held intent certificate, policy snapshot, authorized route, canonical tool metadata, context-risk | action claim fields: tool, payload, intent classes, resource/field/record/destination, evidence refs; digest-bound to current facts | yes: provenance, context dependency digests, evidence references | yes: policy/schema version, fact digests, replay/stale defense | tool execution boundary / external effect; **no** authoritative record fact state machine with per-field committed source anchor | explanation cannot grant authority; no exact certificate-ID non-transferability over candidate facts | explicit predicate ablation and 136 conformance scenarios; but no Alloy-style 12-conjunct ablation | **No** | arXiv full HTML: https://arxiv.org/html/2607.25364v2 ; local `research_scout/PRIOR_ART_THREATS.md` |
| **CapLease** (arXiv:2608.01710) | externalized tool action/effect after authorization | upstream authority gate + authenticated user confirmation + durable authorization budget | canonical action identity σ = (principal, canonical op hash, args hash, resource); execution context χ; authorization instance α = (σ, confirmation, budget) | provenance is upstream input; CapLease itself tracks durable authorization state | yes: validity interval, policy/schema epochs, stale rights, semantic replay defense | durable authorization ledger / action budget; **not** versioned authoritative fact records | cross-principal use blocked; replay resistance; but not certificate-bound candidate identity transfer over record facts | formal bounds + empirical evaluations; no Alloy mechanism ablation of Auto-Decte's C-record/C-field/C-evidence etc. | **No** | arXiv full HTML: https://arxiv.org/html/2608.01710v1 ; local `research_scout/PRIOR_ART_THREATS.md` |
| **SSRN 6938859 — CAP+PCL** (full 10-page text audited via Zenodo copy) | executable agentic action `R` = actor, role, action, resource, parameters, declared context | PCL deterministic policy layer; CAP pre-policy provenance-bound context verification | verification object binds `attribute_type/value`, issuer, subject, request_id, session_id, resource_scope, action_scope, nonce, expiry, integrity proof; **not** `certId + authorizedValue -> exact record/field/expectedVersion` | yes: provenance-bound context attestation, authenticity, integrity, authorized issuer, conflict detection | yes: `fresh(v)`, `bound(v,R)`, request/session binding, expiry, approval replay T4, stale session T5 | policy decision / action execution; **not** an authoritative versioned fact record model | partial: approval replay and ticket-scope binding; **not** certificate-bound candidate non-transferability over persistent fact fields | deterministic 2×2 causal isolation (PCL-only vs CAP+PCL) and T1–T8 classes; **not** 12-conjunct per-binding Alloy ablation | **No** — high proximity on context binding; no formal versioned authoritative record transition or per-binding mechanism ablation | SSRN abstract: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6938859 ; full PDF: https://zenodo.org/records/20539794/files/Chitan_2026_Ilion_CAP_PCL.pdf?download=1 |
| **Transaction Binding Security / SPT-Txn** (SSRN 6486738 + IETF draft-coetzee-oauth-spt-txn-tokens-03) | one concrete transaction / declared action executed under a short-lived TXN token | token chain CAT → CT → TXN; PEP verifies signature, expiry, audience, revocation, sender, chain, scope, context binding | TXN carries `transaction-context hash`, `intent digest` over canonicalized `{tool, params, target}`, `aud`, `holder_key`, `human_anchor`, policy/jurisdiction, attestation; **no candidate/evidence/record-field/expectedVersion fact identity** | yes: attested issuance, workload attestation, signed transaction receipts, transparency log | yes: `iat/exp`, short TTL, status-list revocation, intent/context freshness, policy context | external transaction/action execution; **not** versioned authoritative fact record with per-field source anchor | **explicit transaction binding / non-transferability**: token is cryptographically useless for any other declared action; TB game resists cross-context reuse | formal game-based definitions: TB, EUF-CCA, UNL, ZK-CP, tight reductions; no Alloy-style 12-conjunct record/field/evidence/version ablation | **No direct collision; YES it kills the claim that S5/non-transferability is a new primitive.** Does not formalize AI candidate certificate + authorizedValue → versioned authoritative fact transition. | SSRN page: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6486738 ; IETF draft full text: https://datatracker.ietf.org/doc/draft-coetzee-oauth-spt-txn-tokens/ |
| **Execution-Time Authorization (ETA)** (SSRN 6300558) | canonicalized action instance to be executed | ETA pre-execution authorization function; verdict ALLOW/DENY/ABSTAIN; human override for ABSTAIN | canonical action binding + bound policy/state/version inputs + replayable authorization artifact; not a certificate-bound candidate identity over a fact field | authorization artifact is independently reconstructable; no explicit evidence-identity candidate model in abstract | yes: versioned policy/state, state-freshness/release-binding, TOCTOU | governed system state / action execution; **not** demonstrated as versioned authoritative fact records with per-field `fact_sources` | authorization artifact replayable; no explicit SameValue ⇏ SameAuthority certificate non-transferability in abstract | formal framework, but no 12-way single-mechanism ablation in available summary | **No (high proximity)** | SSRN page: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6300558 |
| **Provenance for Transactional Updates** (Arab, 2019) | relational tuple versions produced by inserts, updates, deletes, commits, and transaction histories | database transaction semantics; no AI authorization object | tuple identifier, transaction identifier, operation, time/version annotations | yes: multi-version semiring provenance and reenactment | yes: SI/RC-SI histories and tuple versions | historical relational database states and update provenance | not an authorization-transfer property | formal algebra, proofs, implementation, and performance evaluation; no candidate-authorization mechanism ablation | **No; it pre-empts update/version lineage and reenactment as standalone contributions.** | IIT dissertation hosted by UIC database group: https://www.cs.uic.edu/~bglavic/dbgroup/assets/pdfpubls/A19.pdf |
| **Auto-Decte (TargetSystem_vNext)** | `CandidateUpdate -> AdmissionEvent -> CommittedFact`; durable per-field `RecordVersionRow.fact_sources` | `Authorization` bound to a persisted `Certificate` with embedded `Candidate`; human authorization; machine certificate | `Context(c) = (record, field, evidenceIdentity(content+locator), expectedVersion)` + primitive `CertId`; `Authorization.certificate` + `authorizedValue` | evidence identity = content hash + locator; persisted certificate embeds candidate | expectedVersion + current record version + successor version; CAS/freshness at admission | versioned authoritative records: `committedValue`, `committedSource`, `currentVersion` | `SameValue ⇏ SameAuthority`; authorization is not transferable to another certificate/context | 12 independent ablations ABL_1..ABL_10 with named counterexamples (to be executed in Alloy) | — (this is the compared system) | `formal/FORMAL_MODEL.md`, `formal/PROPERTIES.md`, `PRE_ALLOY_LOCK_v061.md` |

---

## Predicate-level kill-test notes

The stop condition is:

> A prior work directly formalizes the same effective relation:
> `Authorization(exact candidate identity + authorized value) -> versioned authoritative record transition`
> with record/field/evidence/version non-transferability and equivalent mechanism analysis.

### MemTX

- Full text confirms: evidence, provenance, permissions, validity, snapshot isolation, validate-and-commit, tagged cascading repair, action gating.
- It does **not** contain a per-field authoritative record object with `currentVersion`, `committedSource`, or a `Certificate` whose `CertId` is bound to `(record, field, evidenceIdentity, expectedVersion)`.
- It also does not define `Authorization.authorizedValue` such that an admitted `Transition.value` must equal both the authorization value and the committed fact value in a versioned record.
- **Kill-test: NO.**

### SAGE-Mem

- Full workshop text was parsed.
- Explicit promotion rule:
  `q ∈ belief ⇔ q ∈ evidence ∧ sup(q) ≥ k ∧ indep(q) = 1 ∧ conflict(q) = 0`.
- This is evidence-support/independence/non-conflict admission into durable agent memory.
- There is **no** authorization object, no certificate identity, no record/field/expectedVersion fact-state, and no per-binding mechanism ablation.
- **Kill-test: NO.**

### PCE / Certified Traces

- PCE already establishes the broad architecture `Proposal -> Certification -> Execution`, makes generation distinct from permission, and requires proposed/realized trace conformance.
- Its trace may contain record modifications, evidence, approvals, and policy lineage, so Auto-Decte cannot claim those ingredients or separation itself as new.
- PCE does not instantiate the exact per-field authoritative-record relation, the machine-candidate versus corrected authorized value distinction, a record-level expected-version CAS, or a durable per-field source anchor.
- **Kill-test: NO direct full-tuple collision; generic proposal/certificate/execution novelty is pre-empted.**

### DTF / Proof-Derived Authorization

- DTF is the strongest new threat. Its `JP_t=(M_t,S_t,Pi_t,R_t,B_t)` binds a proposed mutation to a context snapshot and policy; consensus derives a per-decision, non-transferable `EI_t`; `Valid(EI_t,X_t)` gates the actual mutation; an append-only Evidence Chain preserves the lifecycle.
- DTF also tests stale state, post-approval boundary drift, and mechanism ablations. Therefore proof-derived authority, context binding, non-transferability, append-only authorization evidence, and mechanism complementarity are not Auto-Decte inventions.
- The residual difference is narrower and conjunctive: a persisted AI candidate certificate; a distinct human `authorizedValue` supporting Correction; exact record/field/evidence-locator/expected-record-version binding; one atomic multi-field successor version; a complete per-field `fact_sources` snapshot; and per-conjunct formal plus concrete rejection/state-invariance evidence.
- **Kill-test: NO under the full locked tuple; YES against any broader “context-bound governed mutation” claim.**

### EBTE

- Full text confirms typed action claims, server facts, digest-bound evidence, policy/version freshness, and predicate-level conformance ablation.
- Its authorized object is a **tool effect/action**, not a committed fact field in a versioned authoritative record. It does not have `committedSource` or `fact_sources` anchor semantics.
- **Kill-test: NO.**

### CapLease

- Full text confirms durable authorization state, canonical action identity, confirmation binding, version/policy epochs, replay protection.
- Its target is **authorization consumption/effect budget**, not admission of a candidate value into a per-field authoritative fact state.
- **Kill-test: NO.**

### SSRN 6938859 CAP+PCL

- Full PDF was audited via the Zenodo copy.
- CAP usability predicate: `usable(v,R) := authentic(v) ∧ intact(v) ∧ fresh(v) ∧ bound(v,R) ∧ authorized_issuer(v) ∧ scope_compatible(v,R) ∧ no_conflict(v,B_R)`.
- This is a strong context-provenance binding layer for executable actions.
- It does **not** formalize a per-field versioned authoritative record, a certificate-bound candidate identity, `authorizedValue`, or `committedSource`; it has `request_id/session_id/nonce/resource_scope/action_scope`, but no fact-version state machine.
- It also does not perform a 12-conjunct per-binding Alloy ablation; its ablation is a 2×2 causal benchmark (PCL-only vs CAP+PCL).
- **Kill-test: NO direct collision; high proximity on provenance/request binding.**
- Residual note: its title/domain is not a collision; it is related work to cite.

### Transaction Binding Security / SPT-Txn

- Full IETF draft text was parsed; SSRN abstract confirms formal TB definition.
- It directly formalizes the idea that an authorization token must be bound to a specific transaction context and that cross-context reuse is a security failure.
- Therefore **S5 / `SameValue ⇏ SameAuthority` cannot be sold as a new authorization primitive**. The correct Auto-Decte position is:
  - non-transferability is a known security pattern;
  - Auto-Decte's contribution is the **specific concrete instantiation** of that pattern for AI-derived candidate certificates entering versioned authoritative fact records,
  - plus the **12-way mechanism-necessity ablation** and executable conformance.
- It does **not** formalize:
  - a persisted machine `Certificate` with embedded `Candidate`;
  - a human `Authorization.authorizedValue` distinct from `Candidate.value`;
  - `record/field/evidenceIdentity/expectedVersion` as a fact-transition context;
  - a durable per-field `committedSource` / `fact_sources`;
  - ABL_1..ABL_10.
- **Kill-test: NO direct collision on the full Auto-Decte tuple, but YES it kills the S5-as-new-primitive framing.**
- **G1 impact:** must add to Related Work; must not present S5 as a novel primitive.

### Execution-Time Authorization (ETA)

- High proximity on canonical action + versioned policy/state + replayable authorization artifact.
- It lacks the certificate-embedded candidate, evidence identity, per-field authoritative fact state, and 12-way mechanism ablation.
- **Kill-test: NO; high proximity.**

### Provenance for Transactional Updates

- Multi-version update provenance, transaction histories, reenactment, and historical what-if analysis are established database-provenance topics.
- This work has no AI candidate certificate or authorization predicate, but it means version/source lineage and replay cannot be claimed as new mechanisms.
- **Kill-test: NO; supporting lineage contribution only.**

---

## Supplementary related work (lower current risk)

- **Policy-coupled Decision Attestation** (SSRN 7108538): binds an institutional AI decision to the versioned policy/source clause that governed it. Not yet fully audited in this run; initial evidence suggests lower risk than SPT-Txn. Should be tracked for Related Work rather than treated as a G1 blocker unless full audit reveals a direct predicate collision.
- **ConsistencyGate / FAVA / OpenPort / CHAP / SAFEFLOW** etc.: listed in `research_scout/PRIOR_ART_THREATS.md` as medium/high adjacent work. No direct collision established in the local prior-art audit.

---

## G1 decision after Option A approval

**No direct predicate-level collision found** under the currently available official evidence for the full Auto-Decte effective relation:

`Authorization(exact candidate certificate + authorizedValue) -> versioned authoritative per-field fact transition`.

**This is not a novelty green light for S5 or for the generic architecture.** PCE establishes proposal/certification/execution separation; DTF establishes proof-derived, context-bound, non-transferable governed mutation plus append-only authorization evidence and mechanism ablation; SPT-Txn establishes transaction-bound authorization; database provenance establishes versioned update lineage. The remaining defensible Auto-Decte contribution is:

1. The **combined, field-level admission contract** for AI-derived candidate certificates: exact record, field, evidence identity, expected record version, certificate identity, and human `authorizedValue`, including Correction where the authorized/committed value differs from the machine candidate;
2. **Atomic multi-field authoritative-record semantics** with one successor version and a complete per-field durable source snapshot, not merely an executed action or generic mutation lifecycle;
3. **Per-conjunct mechanism-necessity analysis and executable conformance** showing that each substitution/corruption family is rejected without partial state effects, while legal Accept and Correction lifecycles remain reachable.

**Locked claim skeleton:** Auto-Decte does not invent certificates, transaction binding, non-transferable authority, human review, CAS, provenance, source anchors, or mutation evidence chains. It contributes and evaluates their exact composition as a batch admission contract for AI-derived updates entering versioned authoritative records.

**Conclusion: G1 CONDITIONAL PASS.** No direct full-tuple collision was found in the verified primary sources. The contribution is incremental and defensible only at this narrow composite level. The user approved Option A on 2026-08-23, so batch Alloy/refinement work may proceed. Any new source that supplies the same field/evidence/expected-version/authorized-value/source-snapshot relation plus equivalent mechanism evidence reopens G1 and may trigger `RESEARCH-BLOCKED`.
