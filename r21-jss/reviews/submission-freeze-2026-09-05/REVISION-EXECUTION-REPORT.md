# Submission-freeze revision execution report

Date: 2026-09-06  
Manuscript: `revisions/2026-08-27-jss-r21-live-agent-performance/paper/main.tex`

## Verdict

The scientific and technical stop conditions in `REVISION-PLAN.md` are satisfied after a
second C2 closure pass. The revision closes the C2 construction without externally supplied
observation or outcome labels, replaces lexical recognition proxies with a
row-complete semantic acknowledgment audit, decomposes the 0/899 authority aggregate,
states revocation timing precisely, and synchronizes the manuscript, generators, evidence,
and claim ledger. No additional hosted-model run was required.

## P0 outcomes

### C2 characterization

- Defined five observation functions and the reduced projection used by Proposition 1.
- Replaced the original pre-filled witness tuples with complete finite histories containing
  candidates, authorizations, batch references, version observations, declared/committed
  effect domains, predecessor/successor values, source relations, and successor count.
- Observations and normative outcomes are derived from those histories; neither is stored as
  witness input. Both members of every pair pass structural-domain validation.
- Added `evidence/formal/observation-witness-report.json`, which records the raw histories,
  domain-validation results, derived observations, derived outcomes, and projection checks.
- Added six focused tests, including a negative domain-reference case and JSON audit-report
  serialization.
- Kept the theorem conditional on the declared five failure families and observation model;
  it does not claim universal minimality, schema uniqueness, or failure completeness.
- Kept Alloy ablations as bounded sensitivity evidence rather than using them as the proof.

### Semantic acknowledgment audit

- Audited all 325 behavior-evaluable A2/A3/B4/A6 outputs under one documented rubric.
- Context-mismatch acknowledgment changed from the lexical 72/174 to 117/174.
- Stale-state acknowledgment changed from 151/151 to 150/151.
- Clarified that one author specified the rubric and a deterministic script assigned all
  row labels; no AI model or independent annotator assigned row-level labels. Model identity
  and the old lexical label were withheld during assignment, while the endpoint-specific
  rubric was necessarily fixed.
- Reported that the context correction changes the descriptive configuration order from
  D1--G1--G2 under the lexical counts to G1--G2--D1 under the audited counts, without treating
  that order as a provider ranking.
- Preserved assistant text, old/new labels, coding rule, run identity, and confusion matrices
  under `evidence/agent-authority-benchmark-v2/analysis/2026-09-05-recognition-semantic-audit/`.
- Renamed manuscript endpoints from general recognition to explicit acknowledgment.

### Authority endpoint data flow

- Decomposed the accounting total into 720 A2--A9 fixed host-constructed invalid-tuple
  admission calls and 179 A1/A10 capability-unavailable branches with no admission call.
- Confirmed that challenge parameters are predeclared host inputs, not synthesized from model
  responses.
- Retained 0/899 only as aggregate accounting and removed the implication that 899
  model-generated attacks were blocked.
- Limited the 0.33% value to a reference one-sided Clopper--Pearson calculation under a
  binomial sampling model, not a production vulnerability estimate.

## P1 outcomes

- Added the relation-level novelty example: authoritative value 90, machine proposal 100,
  human-authorized value 101, and copy-forward of an unchanged field's prior source.
- Compared that obligation directly with Continuity Kernel, LatticeMind, MutMem, and MemTxn.
- Added a runtime-terminal by endpoint-evaluability table: 93 runtime failures, including 64
  rows with authority verdicts and three rows with behavior verdicts.
- Specified revocation timing: policy is rechecked at commit entry; a revocation completed
  before that check rejects, while an overlapping revocation after a successful check does
  not cancel the in-flight transaction. Stronger semantics require a policy epoch or
  equivalent discriminator inside the admission CAS.
- Closed the mixed-batch boundary by distinguishing submitted decision items $U$ from the
  admitted changed-item batch $B$: a nonempty changed subset is admitted, unchanged values
  and exact sources are copied forward, and unchanged items create no transition or
  authorization binding.

## Verification

- C2 witness tests: 6 passed; implementation regression: 364 passed; focused static check: pass.
- Citation closure: 53 cited keys, 53 bibliography entries, 0 missing, 0 unused.
- LaTeX: 58 pages; 0 undefined citations/references; 0 LaTeX/package warnings; 0 overfull
  boxes; 0 underfull boxes.
- Source lint: no `resizebox`, `scriptsize`, `tiny`, forced `[H]`, negative spacing, or
  `scalebox` in manuscript TeX.
- Float QA: section barriers keep all 18 tables near the relevant sections; none is collected
  after the bibliography.
- Visual QA: inspected the nearest-neighbor, C2 definition/proposition, author-approved Canva
  workflow, evidence-chain, authority-dataflow, runtime/behavior, and authority-result pages.
- Canonical PDF: `paper/main-r21-submission-ready-2026-09-06.pdf`.
- PDF SHA-256: `4553fefdd94f65b67af70cad96ce823b3fd18e4c6dfe0141f6a3cfcdbcec5869`.
- Revision manifest rebuilt and verified successfully for the 58-page PDF.

## Remaining non-manuscript inputs

The manuscript itself contains no empty author or artifact URL. The cover-letter template
still requires the submission date, originality/not-under-review confirmation, and a postal
address only if the journal portal requires it. Optional acknowledgments can be added later.
