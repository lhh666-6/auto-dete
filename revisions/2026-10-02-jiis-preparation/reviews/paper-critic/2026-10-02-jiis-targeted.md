# Targeted JIIS transfer audit — 2 October 2026

Scope: read-only review of `final-source` abstract, introduction, evaluation/results boundaries, captions, declarations, bibliography presentation, and supplementary metadata. No compilation, experiments, git operations, or scientific redesign. Page counts (25 main, 14 supplement), abstract word count (208), and DOI/source verification of the 26 references are supplied by the parent audit; they were not independently rerun here.

## Verdict

No scientific or framing blocker found in the reviewed text. The AI/database integration motivation is concrete, the exact-target/value distinction is retained, and the five conditional classes, Proposition 1 scope, 15 substitutions/165 agreements, presentation boundary, and cost limitations remain intact. No venue-specific citation additions or new experiments are needed for this transfer.

## Potential submission blocker — packaging only

- **Conditional: flatten the actual source upload.** `main.tex:36–46`, `sections/01-introduction.tex:41`, and `sections/07-evaluation-protocol.tex:22` refer to subdirectories. JIIS explicitly says not to use subfolders for LaTeX submission. The organized working source is fine, but the submission package must contain flat filenames with corresponding input/graphics references and required style files. If a separately verified flattened upload package already exists, this finding is closed. Do not flatten or rename frozen repository URLs merely for this requirement. Source: [JIIS submission guidelines](https://link.springer.com/journal/10844/submission-guidelines).

The submission interface must also receive the author-contribution and competing-interest statements; their presence in `sections/declarations.tex:11–27` does not replace those interface fields. This is a submission-time action, not a missing manuscript declaration.

## Minimal optional polish

1. **State the constructed/controlled evidence boundary in the abstract itself** (`main.tex:32`). Replace “In a policy comparison” with “In a controlled comparison of constructed histories”; replace “A server-held review-session gate rejects” with “In scripted browser cases, a server-held review-session gate rejects”. These small edits make the abstract consistent with the explicit scope at `sections/07-evaluation-protocol.tex:6,31,37` and `sections/09-discussion-threats.tex:18`. Recheck the 250-word ceiling and the 25-page ceiling after any edit. Existing body wording already prevents this from being a scientific blocker.
2. **Caption punctuation** (`sections/01-introduction.tex:42`; `sections/07-evaluation-protocol.tex:23`): add a full stop after each final disclosure sentence if editing anyway. No content change is necessary.

## Checks with no remaining fix

- The introduction (`sections/01-introduction.tex:4–37`) ties human-reviewed AI-derived updates to persistent operational records, candidate authorization, transaction checks, and field provenance. This fits the journal's stated AI/database integration and information-system validation interests without claiming a new AI algorithm. Editorial selection remains discretionary. Source: [JIIS aims and scope](https://link.springer.com/journal/10844/aims-and-scope).
- The relation's evidence is bounded by the declared observation model and finite Alloy scopes. Results distinguish context approval from instance approval (`sections/08-results.tex:8–18`); the context journal is not incorrectly labeled universally defective. Browser/display limits and single-machine, unequal-functionality cost comparisons are explicit (`sections/09-discussion-threats.tex:14–20`).
- Captions explain constructed examples, case denominators, timing boundaries, and storage exclusions. Figure 1's prototype use and script-rendered final diagrams are disclosed (`sections/declarations.tex:31`). The disclosure names tools, roles, verification, and human responsibility; it explicitly records the unavailable image model/version. Do not invent model versions. The existing declaration is a suitable alternative manuscript location under JIIS's LLM disclosure guidance.
- Statements and Declarations include availability, historical annotation/consent and ethics assessment, each author's contributions, funding, competing interests, AI assistance, and a descriptive Online Resource caption (`sections/declarations.tex:1–35`). The ethics assessment is transparently the authors' assessment, not a fabricated committee exemption.
- `ESM_1.tex:22–25` includes the article title, journal, author names, affiliation, and corresponding-author email. Main-text Online Resource references and `sections/declarations.tex:35` describe its content; `ESM_1.pdf` follows the required supplementary naming convention.
- Remaining JSS tags and the DKE-supplement directory (`ESM_1.tex:35–41`) identify frozen historical artifacts. DKE table labels, directories, and comments are internal identifiers. Neither is an erroneous current journal designation. Current visible journal metadata is JIIS (`main.tex:20`; `ESM_1.tex:25`).
- `filtered.bib` supplies DOI fields/primary URLs and the main source uses numbered square-bracket citations with `sn-basic`. Parent verification of 26 references is retained; the three Crossref subtitle splits do not justify corrective title changes.

No full manuscript research-quality rating was attempted. No project source files were changed.
