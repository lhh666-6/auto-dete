# Submission-freeze revision execution report

Date: 2026-09-05  
Manuscript: `revisions/2026-08-27-jss-r21-live-agent-performance/paper/main.tex`

## Verdict

The scientific and technical stop conditions in `REVISION-PLAN.md` are satisfied. The
revision closes the C2 construction, replaces lexical recognition proxies with a
row-complete semantic acknowledgment audit, decomposes the 0/899 authority aggregate,
states revocation timing precisely, and synchronizes the manuscript, generators, evidence,
and claim ledger. No additional hosted-model run was required.

## P0 outcomes

### C2 characterization

- Defined five observation functions and the reduced projection used by Proposition 1.
- Added five safe/unsafe history pairs with different normative authority outcomes and
  identical observations after removal of the targeted class.
- Added `source/formal/observation_witnesses.py` and its tests as executable checks of the
  construction.
- Kept the theorem conditional on the declared five failure families and observation model;
  it does not claim universal minimality, schema uniqueness, or failure completeness.
- Kept Alloy ablations as bounded sensitivity evidence rather than using them as the proof.

### Semantic acknowledgment audit

- Audited all 325 behavior-evaluable A2/A3/B4/A6 outputs under one documented rubric.
- Context-mismatch acknowledgment changed from the lexical 72/174 to 117/174.
- Stale-state acknowledgment changed from 151/151 to 150/151.
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

## Verification

- Focused tests: 24 passed.
- Citation closure: 53 cited keys, 53 bibliography entries, 0 missing, 0 unused.
- LaTeX: 57 pages; 0 undefined citations/references; 0 LaTeX/package warnings; 0 overfull
  boxes; 0 underfull boxes.
- Source lint: no `resizebox`, `scriptsize`, `tiny`, forced `[H]`, negative spacing, or
  `scalebox` in manuscript TeX.
- Float QA: section barriers keep all 18 tables near the relevant sections; none is collected
  after the bibliography.
- Visual QA: inspected the nearest-neighbor, C2 definition/proposition, author-approved Canva
  workflow, evidence-chain, authority-dataflow, runtime/behavior, and authority-result pages.
- Canonical PDF: `paper/main-r21-submission-ready-2026-09-05.pdf`.
- PDF SHA-256: `7e346c535da35d3247d75b4d9546788d91956419a52644233142f038ee9fc527`.
- Revision manifest rebuilt and verified successfully for the 57-page PDF.

## Remaining non-manuscript inputs

The manuscript itself contains no empty author or artifact URL. The cover-letter template
still requires the submission date, originality/not-under-review confirmation, and a postal
address only if the journal portal requires it. Optional acknowledgments can be added later.

