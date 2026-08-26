# JSS R18 Experiment and Format Revision Design

**Date:** 2026-08-26
**Status:** approved approach; awaiting design-document review before implementation
**Selected approach:** A — balanced R18 revision

## 1. Objective

Produce a new, independently auditable R18 revision of the Journal of Systems and Software
manuscript. R18 will strengthen the empirical connection to an actual AI-origin candidate,
exercise the existing admission contract across representative production paths, and improve the
paper's novelty positioning and submission formatting without expanding the contribution into a
general agent framework or an unbounded performance claim.

The sealed R17/G10 release remains immutable:

`release-staging/2026-08-26-option-a-r17-rc4-g10-final/`

R18 must be created in a new revision workspace derived from the paper and source material in
that package. The stale top-level `jss/` tree is not an authoritative starting point and must not
be copied selectively into R18.

## 2. Boundaries

### 2.1 In scope

1. One frozen AI-origin candidate fixture with complete available provenance.
2. Six deterministic admission-lifecycle cases derived from that fixture.
3. New machine-readable evidence, manifests, receipts, and paper inputs for those cases.
4. Paper changes that explain the evaluated AI boundary, sharpen novelty, add hardware details,
   and improve reproducibility and formatting.
5. Citation verification, template review, figure review, LaTeX compilation, and a new
   pre-submission report.

### 2.2 Out of scope

- evaluating language-model accuracy, usability, or human decision quality;
- claiming deterministic re-generation of a hosted model response;
- adding LangGraph or another agent-orchestration framework;
- adding a new Alloy S3 scope solely to increase the reported state count;
- comparing against direct SQL or reporting a misleading "security overhead percentage";
- rerunning the entire frozen performance grid unless an R18 paper claim actually depends on a
  changed measured path;
- adding S3/object-storage experiments without a concrete reviewer-facing claim;
- changing author names, affiliations, CRediT roles, funding, acknowledgments, conflicts,
  corresponding-author data, or artifact DOI/URL placeholders.

## 3. Revision layout and immutability

Implementation will create a new isolated working directory, provisionally:

`revisions/2026-08-26-jss-r18/`

It will contain copied R17 paper/source inputs, the new experiment fixture and runner, reproduced
evidence, generated paper inputs, and the revised paper. No file inside the R17/G10 final package
will be edited, deleted, renamed, or overwritten. Every copied baseline file used by R18 will be
recorded with its original relative path and SHA-256 digest.

The eventual R18 release candidate, if all gates pass, will be created under a new
`release-staging/` directory. A failure remains in its own directory with its receipt and logs; it
must not replace R17/G10 or be described as a successful result.

## 4. AI-origin fixture

### 4.1 Purpose

The fixture demonstrates that the admission system can consume a candidate emitted by a real AI
system while keeping AI generation outside the trusted admission boundary. It does not test
whether the generator is accurate, safe, or repeatable.

### 4.2 Input and output

Use a self-authored synthetic three-field administrative record with no personal data, external
copyrighted content, or confidential material. Ask one available AI system to convert the input
into the repository's candidate JSON schema. Freeze the first schema-valid response; do not tune
the prompt until a favorable business value appears.

The fixture bundle must contain:

- the exact input presented to the AI system;
- the exact prompt/instruction text;
- the raw response before normalization;
- the normalized candidate JSON;
- the service/tool name and all model/version identifiers exposed by the host;
- the generation timestamp and locale;
- decoding parameters if exposed, otherwise an explicit `not_exposed_by_host` value;
- SHA-256 digests for every fixture file;
- a short provenance note explaining any unavailable metadata.

If the host does not expose an exact backend model revision, the paper must identify the source
as a hosted AI service session and state that exact-response regeneration is not claimed. The
archived response, rather than a new live call, is the reproducible experiment input.

### 4.3 Trust-boundary rule

The generator may propose candidate values and evidence locators only. It cannot issue an
authorization, select an authorized correction, change the expected record version, bypass
certificate validation, or write the canonical record. All admission checks and persisted
effects must use the same R17 contract and transactional implementation.

## 5. Lifecycle experiment

### 5.1 Cases

Run each case from a declared clean database snapshot, using the same frozen AI-origin candidate
where applicable:

| Case | Operation | Expected result |
|---|---|---|
| A1 | accept all candidate fields | one committed version; candidate sources retained |
| A2 | correct one field and accept the others | one committed version; correction and candidate sources distinguished |
| A3 | correct every field | one committed version; all authorized values and correction sources retained |
| A4 | mixed batch with accepted, corrected, and unchanged fields | one atomic commit; complete per-field source map including copy-forward |
| A5 | replay the authorization against a stale record version | rejection; canonical database digest unchanged |
| A6 | include one invalid item in a multi-field batch | whole-batch rejection; no partial record, trace, or source-map effect |

The experiment may reuse existing catalogue mechanisms, but each R18 case needs an independent
fixture identifier, expected projection, before/after digest, and receipt. Existing tests are not
counted as new R18 cases merely because their names are similar.

### 5.2 Recorded observations

For every case, record:

- candidate and authorization identifiers;
- before and after record versions;
- persisted field values and source types;
- completeness of the field-level source map;
- forward trace from authorization to transition;
- reverse trace from current field to candidate/correction origin;
- transaction outcome and error code;
- pre-call and post-call canonical database digests;
- command exit status and any unexpected exception.

### 5.3 Pass conditions

R18 experimental evidence passes only if:

1. A1--A4 produce exactly one expected atomic transition each.
2. Authorized corrections, rather than AI suggestions, determine corrected persisted values.
3. Every resulting field has one declared source relation, including unchanged copy-forward
   fields.
4. Required forward and reverse traces resolve without an orphan identifier.
5. A5 and A6 produce the declared rejection and preserve the canonical database digest.
6. The run reports zero command failures and its source, configuration, fixture, and lock hashes
   match the receipt.

No accuracy percentage will be computed from six lifecycle cases. The paper will report these as
contract-path demonstrations, not as a representative AI benchmark.

## 6. Performance and environment policy

R18 will retain the frozen R17 performance results unless source changes affect the measured
admission, trace, or storage paths. Hardware and runtime details missing from the prose will be
read from validated run metadata and reported explicitly, including CPU, logical core count,
installed memory, operating system, Python, SQLite, storage information when available, and the
declared timing grid.

If a required hardware field was not captured, the paper will say `not recorded` rather than
infer it. If implementation changes touch a measured path, the old performance numbers cannot be
carried forward; a new fully frozen performance run and comparison gate will be required.

## 7. Literature and argument revisions

The literature stage will verify sources before modifying the bibliography. R18 will add only
literature that supports a specific sentence, prioritizing primary or authoritative sources.

Required revisions are:

1. Add a compact ToolGate/CapChain comparison matrix across the seven residual-relation
   dimensions: evidence identity, authorization identity, intent/payload binding,
   target/context binding, freshness/version binding, atomic admission, and correction-aware
   durable lineage/reverse trace. Unknown cells remain `not established in cited source`.
2. Add foundational provenance grounding, including an authoritative provenance model and
   primary database-provenance work, after full-text/metadata verification.
3. State explicitly that the contribution is generator-agnostic admission: AI generation is
   outside the evaluated trusted boundary, while the frozen AI-origin case demonstrates input
   compatibility.
4. Add one concise intuitive accepted-versus-corrected field example before the formal tuple.
5. Add a limitations paragraph covering deletion/tombstones, manual fallback, database-engine
   portability, hosted-model metadata limits, and the absence of user or production validation.
6. Correct the tamper-probe wording so the manuscript distinguishes a test copy from the sealed
   artifact and does not imply that the valid release itself was modified.

The revision must not inflate related work with uncited names or convert absence of evidence in a
paper into a claim that a system lacks a property.

## 8. Paper and format changes

### 8.1 Structure

Keep the existing JSS modular structure unless compilation or narrative review identifies a
specific defect. Preserve the six research-question ordering and the distinction among bounded
formal evidence, executable conformance, lifecycle demonstration, and fixed-grid performance.

### 8.2 Tables and figures

- Add the ToolGate/CapChain matrix as an editable LaTeX table with source notes.
- Add the AI-origin lifecycle results to an existing evidence table or a compact new table,
  whichever produces clearer page layout.
- Retain current vector figures if their semantics remain correct.
- If the core flow changes, update the existing editable SVG master while preserving its recorded
  AI-ideation-to-vector provenance; do not submit an AI raster or an auto-traced bitmap.
- Run figure QA for font consistency, color/grayscale distinction, arrow direction, text
  editability, print legibility, accessible description, and PDF embedding.

### 8.3 Metadata and declarations

All personal information remains marked `AUTHOR_INPUT_NEEDED`. The generative-AI disclosure will
be updated only to describe actual writing/figure/experiment assistance and author
responsibility. Artifact availability must not claim a DOI or public repository before the user
provides one.

### 8.4 Formatting quality gates

- Elsevier/JSS-compatible class and bibliography configuration;
- no unresolved citations, references, labels, or missing assets;
- no blocking LaTeX errors or warnings;
- no overfull material that clips or makes a table unreadable;
- consistent terminology, symbols, table captions, figure captions, and units;
- abstract, highlights, keywords, declarations, appendix, and cover-letter claims aligned with
  the final evidence;
- visual inspection of every changed page after the final compile.

Page count is an observation, not a target. Scientific content must not be removed merely to keep
the previous 35-page count.

## 9. Required workflow

Execute the user-specified workflow in this order:

1. `literature` — verify and synthesize the new provenance and nearest-work sources.
2. `paper-skill` — revise scientific content, tables, evidence ledgers, highlights, appendix, and
   disclosure text.
3. `latex-template` — check the venue preamble and template compatibility.
4. `academic-figure-skill` — audit and, only if needed, update editable vector artwork.
5. `pre-submission-report` — run the integrated submission checks and record remaining
   author-only fields separately from scientific/technical defects.
6. `latex` — perform the final clean compile, citation audit, warning review, and rendered-page
   inspection.

No later stage may silently alter an empirical number. A change to evidence sends the revision
back through paper generation and all downstream gates.

## 10. Traceability and verification

R18 will maintain a claim--evidence ledger for every new empirical statement. Each lifecycle
number or pass/fail statement must point to a normalized JSON path and, through a manifest, to the
raw receipt. Each literature comparison must point to the verified cited source. Generated
tables must retain a machine-readable intermediate.

Before declaring the revision technically complete:

1. verify baseline-copy hashes against R17/G10;
2. run the new lifecycle experiment from a clean environment;
3. validate receipts, manifests, normalized paper inputs, and source/config/fixture hashes;
4. run relevant unit, integration, catalogue, and comparison checks;
5. compile the paper from a clean copy;
6. perform code--paper, artifact-coherence, and reproducibility checks when available;
7. run the required skill workflow and resolve all Critical/Major findings;
8. repeat release/source/evidence manifest verification;
9. record unresolved items that only the author can supply.

## 11. Stop conditions

Stop and preserve evidence rather than weakening the design if:

- the AI-origin response cannot be archived with honest source metadata;
- a new experiment requires changing the frozen R17 contract merely to obtain a pass;
- a receipt or manifest hash does not match;
- an implementation change invalidates retained performance evidence and a valid replacement run
  is unavailable;
- a new literature source establishes a direct collision with the claimed composite
  contribution;
- paper prose would need to imply model accuracy, production validation, or public artifact
  availability that was not measured or supplied.

Missing personal information does not stop technical work. It remains a clearly separated
author-input gate.

## 12. Completion criteria

The R18 revision is technically complete when:

- the six-case AI-origin lifecycle evidence passes with intact manifests;
- all new claims are traceable and all retained R17 numbers still match their frozen source;
- the novelty matrix and provenance literature are source-verified;
- the paper clearly separates generator output, human authorization, and authoritative state;
- hardware details and experiment limitations are explicit;
- the template, vector artwork, citations, and rendered PDF pass their quality gates;
- the pre-submission report has no unresolved Critical/Major scientific or technical issue; and
- remaining blockers consist only of personal metadata or a public artifact identifier that the
  user has explicitly deferred.

## 13. Design self-review checklist

- The design strengthens the AI connection without turning the paper into an AI-accuracy study.
- The six cases test distinct contract paths and do not overstate a small sample as coverage.
- Negative cases use database digests to detect partial effects.
- Hosted-model metadata limits are disclosed rather than guessed.
- Retained performance data are invalidated if measured code changes.
- The R17/G10 final package and the stale top-level `jss/` tree cannot contaminate R18.
- Literature additions are tied to claims and require source verification.
- Core artwork remains editable vector output with honest AI provenance.
- Personal information remains untouched.
- The workflow order requested by the user is explicit and mandatory.
