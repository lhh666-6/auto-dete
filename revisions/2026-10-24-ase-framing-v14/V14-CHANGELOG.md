# Framing revision v14 - 24 October 2026

Manuscript: **The Review-Execution Gap in Agentic Software: Approval Scope and Recovery**

29 pages, 0 undefined references, 0 overfull boxes. Derived from the v13 release; nothing
experimental changed. The third pass below adds one page (the archived reauthorization episode
and two verified references); it is the only change to the page count. The fourth pass applies the
author's external English revision to the abstract, introduction, related work, Table 2, the worked
example, the opening of Section 7.1 and the conclusion, and re-flows pages 1-6 without changing the
page count.

## What the paper now claims up front

The paper now states the increment at three levels and keeps them separate. The abstract: "we study
how approval scope governs candidate admission at a durable execution boundary and how agents
continue after rejection", followed by the 24/8 split, the rejection-boundary audit sentence and the
closing separation of admissibility from route selection. The introduction: a complementary question
posed after the existing mechanisms (authorized-value, freshness, atomicity and provenance held
fixed, how approval scope changes admissibility, which legal continuation an agent chooses after
rejection), with the four-role contract as the common basis. The discussion: "Approval scope
determines which replacements are admissible; continuation determines how the agent uses the
authority that remains." Recovery-route selection is therefore an evaluation target alongside
admission correctness, and the reports do not claim to explain why an agent chooses a route.

## Introduction (pp. 2-3)

- The positioning paragraph was rewritten. It keeps the single acknowledgement of prior mechanisms
  (reconstruction-aware authorization and transactional approval enforcement; post-review
  substitution and approval--execution binding failures), then asks the complementary question, names
  the four-role contract as the common basis, separates definitional admission consequences from
  empirically observed recovery choices, states the observed reauthorization despite available and
  visible reuse, and closes with the separate measurement of recovery commits, renewed authorization
  requests and subsequent confirmation.
- One redundant sentence that restated GitLab deployment approvals (already in the first paragraph)
  was deleted, and the "two connected parts" paragraph was tightened. No citation was dropped.

## Contributions (pp. 3-4)

- Reordered: the comparison model is contribution 1, the empirical recovery account is contribution 2,
  and cross-layer validation is contribution 3 ("Validation of distinct review-to-execution
  obligations").
- Contribution 2 now carries the availability audit in its own sentence ("saved-state and model-input
  audits establish that the original candidate and its usable grant remained available and visible in
  all 32 episodes") and closes with the three separated cost components. Scope words are unchanged: 32
  delivered pairs, 16 task definitions, 24 reuse, eight fresh authorizations.
- Contribution 3 groups relational and event-journal implementations, persisted-state checks, bounded
  formal analysis, the ToolGate adaptation and the separate pinned-SDK probes as distinct obligations
  rather than one end-to-end claim.

## Related work (pp. 4-6)

- Table 2, Guarded Commits row: mismatch handling now reads "Validated decision reuse or renewed
  review" instead of "Fresh authorization or review".
- The closest-comparison paragraph now states ReSA's repair obligations, consumed versions, grant
  scope and guard-patch path check, and Guarded Commits' validated decision reuse, renewed review,
  decision-policy comparison and commit-time artifact binding, then states the increment as the
  combination: hold those obligations fixed, vary the binding object, and sample the continuation an
  agent chooses after a failed binding, auditing state and input for route costs.
- It also distinguishes the reuse object: their reuse acts on a validated decision and derives a new
  authorization record, whereas one primary route here executes the original candidate under the
  still-valid original grant.

## Typesetting

- Bibliography inter-entry spacing set to 0.5em immediately before the bibliography so the reference
  list ends on page 28; the section 3 heading consequently opens page 7.

## Second pass after author review

- The closing paragraph of the closest-comparison discussion now states the study as a controlled
  scopes comparison plus an analysis of the continuations agents choose; it separates the two
  evidence uses explicitly (saved states and model inputs establish availability and visibility;
  execution records establish recovery, renewed authorization and confirmation costs), attributes
  derived-record reuse to Guarded Commits, and names the reuse object of the primary route here. The
  long ReSA sentence was split in two. No claim of priority or unified framework was added.
- "these routes cost differently" became "these routes incur different interaction costs".
- Float placement: the sn-jnl class redefines the table environment through threeparttable, and a
  [H] specifier fails there, so [ht] is used instead.
  Table 1 now follows the whole contribution list (p. 4) instead of splitting the second
  contribution. Table 2 is placed at the end of Related Work (p. 6, after the closing lines of
  Section 2.2) so that it no longer cuts the closest-comparison sentence or any paragraph of
  Section 2.2; Section 3 opens on p. 7. Table 7 is set as a bottom float at the end of
  Section 6.3 (p. 18), after the paragraph that cites it, and precedes Section 6.4 (p. 20), so the
  32-pair cost table is no longer separated from its subsection by the start of the feedback study.
- The manuscript remains 28 pages with no overfull box and no undefined reference.

## Online Resource 1 alignment

- OR1, S10 named Cordon as one of the closest execution-oriented comparisons. The main text removed
  Cordon in v12, so the sentence now lists the two remaining comparisons, Continuity Kernel and
  commit-time authorization, and the unit mapping was updated accordingly (accepted branch-head
  transition; durable effect licensed by a current authority witness). The task-transaction unit that
  belonged to Cordon was removed with it.
- OR1 was rebuilt from its source; it remains 30 pages with no overfull box and no undefined
  reference. ESM_1 therefore changes: it is no longer byte-identical to v12, while ESM_2 and the seven
  experimental archives remain byte-identical. Supplements carry no bibliography, so no entry was
  orphaned.

## Unchanged

As of the second pass: abstract, questions, definitions, figures, tables other than the one Table 2
cell, statistics and all experimental archives were unchanged, as were the data and software
statement, the v11 AI-assisted preparation statement and the other declarations. No model call or
new experiment was performed. The third pass changes some of these items; it adds no run.

## Third pass: evidence readout, metric definitions and layout

No experiment was added; every number below is read from records that were already frozen.

- **One archived reauthorization episode in the main text (Section 6.3, pp. 18-19).** A new paragraph
  reports episode FORMAL-G-006-A (supplementary A, one of the eight fresh-authorization cases) in its
  four parts: the saved rejection state (reviewed candidate c1 unchanged, grant a1 active for c1 with
  authorized value 23560, head version 2 which the rejected request also observed, no transition
  written), the saved model input that starts the next decision (proposal result for c1, authorization
  response for a1 with its authorized value, rejected c2 request with its feedback), the first
  post-feedback call (authorization requested for c2 rather than reuse of c1; host issues a2 for c2 with
  the same value and supersedes a1), and the execution (commit of c2 under a2 accepted, transition-1
  persisted, two later query-only calls). The paragraph states that the episode illustrates the
  mechanism and is not selected for typicality.
- **Online Resource 1, S12.6** now documents two archived examples instead of one: the existing
  original-B reuse episode and the new supplementary-A fresh-authorization episode, with a table of the
  recorded events, the event-member path inside `quota-recovery-complete.zip` and the state files that
  anchor rejection and recovery.
- **`qa/recovery_example.py`** now verifies both episodes from the two frozen archives (rejection reason
  and predicates, saved-state candidate/grant/head, saved-input candidate/grant/value/feedback, call
  order, single accepted commit, grant supersession, context-arm call count) and rewrites
  `tables/recovery-example-source.json` with per-example checks. `REPRODUCE-RECOVERY.md` lists the
  expected results for both. No published outcome changed.
- **First definition of I (Section 6.1).** The first sentence now defines I as conformance to the
  instance-bound reference contract before the later explanation that I = 0 is not a safety judgement
  under a context policy. Wording of the scoring rule is unchanged; no score was recomputed.
- **16-cell native-SDK check (Section 5.3).** The passage now names the crossed factors (two
  lifecycles, two decisions, four substitution targets) and accounts for all 16 cells: four execute
  substituted arguments; the two deferred-request-object-only cells and the two no-substitution
  approval cells execute the reviewed object; the eight override cells are as before. The two
  previously unstated cells were verified in the frozen study (`score-v1.json`, `REPORT.md`) and the
  matching clause was added to Online Resource 2, A17.
- **Finite-scope bounds (Section 5.1).** The passage now states the S1 and S2 bounds (records, fields,
  versions, states/events, admission items or transitions), notes that individual commands raise
  individual bounds, and decomposes the 72 command outcomes as 22 satisfiable and 14 unsatisfiable
  commands per profile, citing Online Resource 1, S2.5 and S2.6. The earlier draft cited S2 and omitted
  the decomposition; the label was corrected after checking the rendered supplement.
- **Related work (Section 2.1).** AgentSpec (ICSE 2026, pp. 2938-2950, DOI 10.1145/3744916.3764546,
  arXiv 2503.18666) and RefineAct (ASE 2026, pp. 993-1004, DOI 10.1145/3832783.3834409) are now cited in
  two sentences that state their runtime-enforcement and per-action confirmation dispositions and then
  the difference from this study. Both entries were verified against ACM-deposited Crossref records and
  the camera-ready PDFs; RefineAct has no arXiv record, so no eprint field was invented. ReSA and Guarded
  Commits remain the closest comparisons. The bibliography now holds 41 entries, 40 of them cited.
- **Figure 4.** A summary row was added inside the figure ("Instance-bound recovery: 32/32 . Reuse: 24 .
  Fresh authorization: 8"), with the three counts derived from `figure-data.json` and assert-guarded,
  and the cost panel now notes "delta = instance minus context". The caption's delta wording was
  harmonised to the same convention. Measured height increase: 7.4 pt at inclusion; no plotted value,
  marker, cohort alignment or colour changed, and the other four figure PDFs are byte-identical.
- **Data and software availability.** Rewritten as four labelled paragraphs that keep the entry point,
  the three frozen trees, the resource contents and the reproduction route, but use readable link
  labels instead of bare 40-hex strings, one SHA-256 digest and long ZIP filenames. The entry point was
  corrected: the previous reproduction-guide link resolved to the earlier KAIS guide, which does not
  name the seven ASE archives, so it now points at the pinned reproduction guide of the released
  version (tag `ase-layout-v13-2026-10-24`). The dropped claims are recorded in the packaging notes
  below.
- **Layout.** Table 2 became a top float on p. 7 so Section 3 opens on p. 6 without a table-only page;
  Figure 4 follows the paragraph that first cites it (p. 19); Table 7 is a top float on p. 20; the
  example paragraph continues across pp. 19-20. Final state: 29 pages, 0 overfull boxes, 0 undefined
  references, 0 unresolved citations.

## Fourth pass: external English revision (24 October 2026)

Source: `ase_revision_text.docx`, supplied by the author as six pages of replacement prose with
page locators. Applied as text only: no figure, table label, citation key, numerical result or
archive changed, and the page locators in that document refer to the pre-revision 29-page build.
Rebuilt state: 29 pages, 0 overfull boxes, 0 undefined references, 0 unresolved citations; abstract
230 words; 41 bibliography entries, 40 cited.

- **Abstract** replaced. The question sentence now names admission under approval scope and
  continuation after rejection; the five evidence layers are one sentence; the 24/8 split is
  followed by the boundary-specific audit ("at the observed rejection boundary in all 32 episodes,
  saved states establish that reuse was valid and actual model inputs contain the reviewed
  candidate, grant and authorized value"); the closing sentence separates admissibility from route
  selection and asks for recovery, renewed authorization and confirmation to be measured apart.
- **Introduction** re-flowed around one line: approval scope fixes admissible replacements,
  continuation is a separately observable choice. Gerrit and GitLab stay in the first paragraph;
  ReSA, Guarded Commits, Loopjacking and Approval Laundering are no longer introduced here (they
  remain in Related Work, which keeps the closest-neighbour positioning); the c1/c2 example is
  shortened; the three RQs and three contributions are kept, with contribution 2 now carrying the
  24/8 split and the "reuse was valid and visible at the observed rejection boundary" audit;
  contribution 3 now claims tested conditions and assumptions rather than layer guarantees; the
  Table 1 lead-in separates the paired comparison ($K=R$) from the comparator cases.
- **Related work (2.1-2.2)** reduced from about 680 to 580 words. The study-level positioning is
  consolidated in the last paragraph of 2.1 ("our controlled comparison varies approval scope under
  common correction and persistence requirements..."); AgentSpec and RefineAct are two sentences
  without the repeated runtime-enforcement contrast; the Guarded Commits distinction is now the
  concrete one (its reuse path appends a derived resolution record; one route here executes the
  original reviewed candidate under its still-valid original grant); the two failure analyses keep
  the tested-configuration caveat and the version-1 preprint statement.
- **Table 2** re-headed: Source / Binding object / Response to change / Boundary / Evidence basis;
  group headings shortened to the three source families; the caption was split into a short caption
  and a note below the table, which keeps the failure-analysis caveat, HITL and the version-1
  preprint sentence. The "Compared:" and "Analyzed:" prefixes were dropped because the Evidence basis
  column now carries that distinction; "Context, content and instance scope" replaces
  "Compared: context, content and instance". The revision's fourth group heading ("Current study")
  was not added: the "This work" row already closes the table, so the heading duplicated it.
- **Section 6.3 example** replaced by the revision's 123-word compression. The event chain is
  unchanged (c2 rejected as INSTANCE_MISMATCH without a transition; c1, active grant a1 authorizing
  23560 and a current predecessor in the saved state; next input holds the proposal that created c1,
  the grant response and the mismatch feedback; first call requests authorization for c2; a2 issued
  for the same value and supersedes a1; commit of c2 under a2 persists transition-1; two query-only
  calls follow). The S12.6 pointer and the statement that the episode is not selected for typicality
  are kept.
- **Section 7.1** opening five paragraphs replaced by three: (i) admissibility versus continuation,
  with the "not a new enforcement mechanism" hedge kept as the closing sentence; (ii) the 32/24/8
  observation, the rejection-state and next-input audit, and the explicit limit that the records do
  not establish why the agents sometimes chose reauthorization or whether that was optimal; (iii) the
  path-label comparison, the interface/telemetry implication and truthful stopping. "Read together,
  the results..." and the four numbered design implications follow unchanged.
- **Conclusion** replaced: admission versus continuation, then the 24/8 split with "although reuse
  was available and visible at each observed rejection boundary", the tool-call result with no
  established task-completion advantage, the unmeasured human-review cost, the feedback comparison,
  and the separate measurement implication.
- **Layout.** Table 2 was moved from the end of Section 2.2 to directly after the Section 2.1
  paragraph that first cites it, so it is now a top float on p. 5 instead of blocking p. 6 (the
  previous placement left about nine blank lines before Section 3). Table 1 stays at the top of
  p. 4, Figure 4 at the top of p. 19, Table 7 at the top of p. 20; Section 3 opens p. 7, Section 7.1
  p. 21, the conclusion p. 23, Statements and Declarations p. 24, references pp. 25-29. The
  compressed example and the re-flowed discussion keep the worked example and its figure on adjacent
  pages.
- **Copy decisions made while applying.** Serial commas follow the supplied text. "For these
  preprints" became "For the preprints cited here". The caption says "binding objects", not
  "authorized objects", to match the column. One escaping artifact introduced by the import script
  (an accented "s" in "Agent Framework's") was caught in the rendered page and fixed.

## Final polish and freeze (same day, after the author's last review)

Three changes were made and nothing else in the manuscript was touched.

- **Contribution order.** The contributions now read C1 comparison model, C2 validation of
  review-to-execution obligations, C3 empirical recovery account. Only the two enumerated items
  were exchanged; their text is unchanged. The order now matches RQ1-RQ3, Sections 3-6 and Table 1.
- **Figure 1 placement.** The figure environment stays directly after the paragraph that first
  cites it, but its placement specifier is now `[b]`. It therefore sits at the foot of page 2,
  below the introduction heading and the first three paragraphs, instead of occupying the top of
  page 2 above the heading. Source position and float content are unchanged.
- **Section 7.1.** The sentence "The evidence is a comparison of scopes and their continuations,
  not a new enforcement mechanism." was deleted as redundant with the related-work comparison.
  The surrounding paragraph is otherwise unchanged.

## Packaging (completed)

- **Payloads.** `Manuscript.pdf` (29 pages), `ESM_1.pdf` (31 pages), `ESM_2.pdf` (25 pages),
  `Manuscript-source.zip` (flat portal source, 11 members) and `ESM_3.zip` (README, MANIFEST,
  MASTER-MANIFEST, a 63-member `Manuscript-sources.zip` and the seven experiment archives).
  | File | Bytes | SHA-256 |
  |---|---|---|
  | Manuscript.pdf | 3732553 | `a710e0650df3f3d759b555786c22fd743565caf3d7d1642adc15bdfe9243a2fe` |
  | Manuscript-source.zip | 3163497 | `3010c29140fa7d688ecc3724aed9c81816bebc983c32bde5a8349fba2dddfbbe` |
  | ESM_1.pdf | 544456 | `3a5a22285d8f05dcfc5f2311126ca12525a52107b8fceea5f8361b65fee5919b` |
  | ESM_2.pdf | 623695 | `cafb10d26df9df71b451286d4081abadab39ac501698b21562f616ef72f22688` |
  | ESM_3.zip | 12699374 | `386c82abf1c1d1cef8f1c63dc0f7b141548aa9c32de48d6a2ea0cdf55b9341ca` |
- **Independent rebuild.** Both source ZIPs were extracted and compiled from scratch: 29 pages each,
  and the extracted PDF text is identical to the supplied `Manuscript.pdf`.
- **Archive integrity.** Every `ESM_3.zip` manifest entry matches its member by byte count and
  SHA-256; the seven reproduction archives are byte-identical to v13; `MASTER-MANIFEST.json`
  inventories all 63 members of `Manuscript-sources.zip`.
- **Package.** `submission/ASE-2026-10-24-v14/` holds `ready-to-upload/` (six files) and
  `author-notes/` (metadata, upload map, Springer checklist, declarations, cover letter, inherited
  v9-v13 records); the 20 MB submission ZIP and its `sha256` files sit beside it.
  `SOURCE-MANIFEST.json` was regenerated for the 62-file source tree, `README.txt` rewritten,
  `FINAL-FREEZE-v14.json` records 125 files, and `audit/VERIFICATION.json` was updated.
- **Release control.** This state is committed to `main` and tagged
  `ase-framing-v14-2026-10-24`, pushed to `origin` (fast-forward from the v13 release `f557071`);
  the tag points at the commit that carries this changelog. The manuscript's data and software
  statement still cites the published v13 release, because the study artefacts are unchanged
  between the two and only manuscript sources and layout differ; the v14 tree is additionally
  frozen here in `FINAL-FREEZE-v14.json`.

## Independent final audit (read-only)

A separate read-only audit pinned the manuscript at `main.tex` `48e3847c…` and `main.pdf`
`a710e065…` and returned PASS on all six requested checks: citations (40 cited keys, 41 entries,
no cited-but-missing; AgentSpec = Wang et al. 2026a and `wang2026agr` = 2026b), supplement
cross-references (every S/A target exists; S12.6 holds both archived episodes), numeric consistency
(all reported counts and intervals reconcile with OR1/OR2 and the shipped tables), declarations
(AI statement verbatim; v13 tag, guide and ESM_3 manifests verified), external inputs and archives
(23/23 hashes, seven reproduction archives present and hash-matching) and the build (29 pages,
0 overfull, 0 undefined references/citations, no `??`). Non-blocking observations were recorded but
not acted on: one uncited legacy bibliography entry (`testera`), an ambiguous A17 "freeze" hash
label in Online Resource 2, duplicate PDF hyperlink destinations, and the "Codex CLI" host mentioned
in Section 6 alongside the frozen Codex-declaration wording. All are author-judgement items; none
affects the manuscript's claims or the package contents.



## Remaining open items

- **Withdrawal confirmation.** The package is prepared for a new submission after the earlier ASE
  submission is confirmed withdrawn; no submission has been made and none should be made first.
- **Tag push.** The v14 commit and tag exist only locally. Pushing them is an author decision and is
  not needed by the manuscript, whose availability statement cites the published v13 release.
- **Experiment-archive inventories.** `MASTER-MANIFEST.json` covers the eight top-level archives and
  the full 63-member inventory of `Manuscript-sources.zip`; the seven experiment archives keep their
  own internal manifests, seals and start-here guides rather than duplicating thousands of member
  digests. The availability sentence claims only that "manifests record their files and SHA-256
  digests", which holds at this level.
- **Optional checks before upload.** The two external historical archives are not embedded; their
  pinned URLs and digests are listed in `REPRODUCE-RECOVERY.md`, and dependent readbacks require
  downloading them. Human-review cost remains unmeasured by design.
