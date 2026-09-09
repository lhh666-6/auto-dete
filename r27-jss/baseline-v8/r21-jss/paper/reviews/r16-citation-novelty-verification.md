# R16 citation and novelty verification

**Date:** 2026-08-25  
**Gate:** G9 — PASS  
**Manuscript:** *Certificate-Bound Admission of AI-Derived Updates into Versioned Authoritative Records*  
**Independent report:** `reviews/claim-verify/2026-08-25-1525.md`  
**Independent report SHA-256:** `b13207caf03a0ea47e4747f9b3938e13e4f9c4ee1747ddecbd74c4483f128395`

## 1. Decision

R16 is complete and G9 closes for the manuscript state compiled on 2026-08-25.
The independent fresh-context audit inspected all 36 cited records and evaluated
20 manuscript attribution/novelty claims. Its current-state result is 20/20
`ACCURATE`, with 0 Critical, 0 Major, 0 Minor, and 0 unverifiable claims. No
checked source satisfies the complete seven-part R0 kill test; therefore no
central collision triggers `RESEARCH-BLOCKED`.

This is an attribution-fidelity and scoped negative-search result. It is not a
proof of priority, a systematic-review completeness claim, or evidence that an
individual ingredient is novel.

## 2. Locked contribution wording

Every novelty statement now preserves the same seven relations locked at R0:

1. a persisted AI candidate distinct from the authoritative fact;
2. attributable authorization of that exact candidate and an explicit
   authorized value;
3. joint record, field, persisted-evidence-identity, and expected-pre-version
   binding;
4. one atomic nonempty multi-field authoritative-record successor;
5. a complete successor-wide field-source map;
6. Correction preserves the candidate while committing the separately
   authorized value; and
7. named per-conjunct counterexamples paired with executable fail-closed checks
   and no partial admission effect.

The complete relation appears in the introduction and in the closest-work
comparison. The discussion refers back to that same seven-part conjunction.
Broad novelty for verified state commit, capabilities, provenance, candidate/fact
separation, CAS, authorization tokens, or transaction reenactment is expressly
disclaimed.

## 3. Mandatory high-collision review

| Relation | ToolGate | CapChain | R16 disposition |
|---|---|---|---|
| Candidate distinct from fact | typed symbolic tool state; no durable candidate/fact pair | reducer-mediated agent fields; no candidate/fact pair | no complete match |
| Exact candidate plus explicit authorized value | no attributable correction decision/value relation | capability authorizes field forwarding/reading, not this pair | no complete match |
| Record + field + persisted evidence + pre-version | pre/postconditions bind tool state/output shape | field capability and provenance root, but no full authoritative-record tuple | no complete match |
| Atomic nonempty multi-field successor | conditional symbolic-state update | one incoming field/value merge in Algorithm 1 | no complete match |
| Complete successor-wide source map | absent | ProvChain is not a total source map for every successor field | no complete match |
| Correction preserves candidate | absent | absent | no complete match |
| Per-conjunct counterexamples plus executable fail-closed/no-partial-effect checks | different contract ablations | security arguments and gate harness, not the R0 matched catalogue | no complete match |

ToolGate was checked in the ACL 2026 Findings full text, especially Sections
3.2--3.5. CapChain was checked in the Applied Sciences version of record,
especially Sections 4.2--4.4 and Algorithm 1. These sources invalidate broad
claims about contract-gated state update and capability/provenance-aware merge;
the manuscript has been narrowed accordingly.

## 4. Sentence-level disposition

The independent report verifies the following 20 claim groups:

| ID | Claim group | Current result |
|---:|---|---|
| 1 | proof-carrying and transaction-bound authority | PASS |
| 2 | proposal/checking/execution/durable-mutation separation | PASS |
| 3 | transaction provenance reconstructs histories | PASS |
| 4 | scoped seven-part negative-search statement | PASS |
| 5 | ToolGate/CapChain preclude broad novelty | PASS |
| 6 | Proof-Carrying Authentication checker characterization | PASS |
| 7 | DPoP, Transaction Tokens, SPT-Txn, and CapLease | PASS |
| 8 | PCE and DTF | PASS |
| 9 | EBTE, CAP+PCL, and MemTX | PASS |
| 10 | exact related-work restatement of the residual conjunction | PASS after repair |
| 11 | transaction reenactment and multi-version provenance | PASS |
| 12 | Alloy and Kodkod bounded SAT analysis | PASS |
| 13 | TestEra versus Dennis/TACO mechanisms | PASS after split attribution |
| 14 | mutation analysis and real-fault limits | PASS |
| 15 | stateful/concurrency testing and Elle | PASS |
| 16 | source availability versus executable artifacts | PASS after split attribution |
| 17 | JSS executable-experiment and artifact practice | PASS |
| 18 | JSS theory--implementation--evidence exemplars | PASS |
| 19 | antecedent engineering mechanisms are not isolated novelty | PASS |
| 20 | final novelty-validity boundary | PASS |

The focused repairs were: restoring every R0 relation in the closest-work
sentence; separating TestEra's concretization/abstraction mechanism from
Dennis/TACO bounded code checking; separating Collberg, Hermann, and Klees by
the proposition each supports; and removing stale future-verification language.

## 5. Local primary-source freeze used for collision checking

| File | Bytes | SHA-256 |
|---|---:|---|
| `capchain.pdf` | 901875 | `1e0824df0d1794a2b0fd607d6de08d53989753d025f9274df98a973846cc12ac` |
| `caplease.pdf` | 450880 | `f3baaaf4711b98a6fb9eff605ac037a7d01c7a827799746981000be4bc802527` |
| `cappcl.pdf` | 352063 | `d944f024b68ee55417c38d811af8871d7550489a4044062ab6a3f9c06871a558` |
| `dtf.pdf` | 362453 | `d75dc8815f4d62a4e13132dc8ddecd46ff573e6272a8ac25043f9277f893f8ff` |
| `ebte.pdf` | 313301 | `0095234c1cf139e5805a9d0cd8e49a0366009c7d987b07d371b2c47f807e0718` |
| `memtx.pdf` | 848643 | `70a55fada7121a5d47fae3185fd09dca18d69826020dcb165323c044c65b1944` |
| `pce.pdf` | 4850454 | `2674e1ab540e8ef5297b656bcb886a10a5783ad804735593bc1522968b5d45d2` |
| `toolgate.pdf` | 3395441 | `7073bc0a27cf0f002ea4d1ef0ec3726d5c70c7e44a218e78f46d92284aba289d` |

These local copies supplement the official standards, publisher, author-hosted,
and version-pinned repository sources listed in the independent report. They are
R16 working material, not paper evidence inputs.

## 6. Mechanical verification after repair

| Check | Result |
|---|---|
| Active citation keys | 36 |
| Active keys missing from `references.bib` | 0 |
| Bibliography records | 40 |
| Deliberately uncited literature-pool records | 4 |
| Remaining pending-claim markers | 0 |
| `pdflatex`/BibTeX build | PASS |
| PDF pages | 35 |
| Blocking LaTeX/package/undefined/overfull warnings | 0 |
| Benign underfull boxes | 1 |
| Compiled PDF SHA-256 | `0cfde38c0d0411e7a99e669817c9015c606fee33222cbd88e5f90160de307c68` |

MiKTeX emitted its local installation-maintenance notice that updates had not
been checked; it did not affect compilation or manuscript diagnostics.

## 7. Gate conclusion

`G9 — Citation fidelity: PASS.` R17 may assemble and independently test the
post-paper release candidate. Author identity, affiliations, declarations,
funding, acknowledgments, and artifact hosting remain author-only metadata and
are not part of this citation-fidelity gate.
