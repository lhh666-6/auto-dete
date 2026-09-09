# FINAL CODEX HANDOFF — AUTO-DECTE R21 JSS revision

Date: 2026-09-06 (Asia/Shanghai)

## 1. Final research question

Which observable relations must a correction-aware authoritative-state admission boundary
retain to distinguish declared candidate-to-authority failures, and can one transactional
realization preserve that boundary under varying live-agent behavior?

## 2. Final contribution

The revision contributes (C1) correction-aware authoritative-state admission semantics,
(C2) a five-class conditional failure-distinguishability characterization, (C3) bounded
formal and transactional realization evidence, and (C4) behavioral validation of the
admission boundary across three qualified live-agent configurations. The DSH/plugin result
remains an adapter-boundary demonstration, not a claim that a harness supplies authority semantics.

## 3. What changed in the system

The R21 overlay adds a two-tool MCP surface (`auto_decte_propose` and
`auto_decte_verify`), deterministic scenario preparation, host-only confirmation for
stale and cross-context checks, a locked live-agent environment, an equivalent
materialization arm, and form-scoped reverse-trace loading. Model-callable fact writes
remain absent; authoritative mutation stays in the trusted host transaction.

## 4. What changed in formal and conformance evidence

The frozen formal/conformance baseline is preserved. Across two bounded Alloy scopes, all
66 outcomes match their declarations. The selected projection contains 9 intended SAT and
20 mapping-mutant UNSAT cases; the executable catalogue passes 35/35. The recorded
implementation quality summary contains 354 Python tests, Ruff exit 0, strict mypy exit 0
over 52 typed files, 2 stateful tests, and 33 rollback/concurrency tests. Proposition 1 now
has five explicit safe/unsafe history pairs. The checker stores neither observations nor
outcomes: it validates each complete finite history, derives all five observations and the
normative outcome from its relations, and shows that each pair has unequal derived outcomes
but equal reduced observations when its target class is removed. The generated JSON report
records every raw history and derived result.

## 5. New experiments and results

The repeated live-agent Final retains all 1,260 planned executions across three qualified
configurations, three prompt variants, fourteen scenarios, and ten repetitions per cell.
Benign completion is 320/335. The authority aggregate is 0/899 and is explicitly decomposed
into 0/720 fixed host-constructed invalid-tuple calls and 0/179 capability-unavailable branches;
it is not described as 899 model-generated attacks. Ninety-three runtime failures (D1 76,
G1 4, G2 13) are reported separately, including 64 with a complete authority verdict and
three with a behavior verdict. A row-complete semantic audit changed the lexical proxies to
117/174 context-mismatch and 150/151 stale-state acknowledgments. The earlier
canonical six-scenario live-agent run remains an integration example. The feature-equivalent baseline covers ten cells and
2,000 pairs; all relational fingerprints match, with full-path p50 17.820–194.862 ms
and prevalidated materialization p50 10.469–16.479 ms. The optimized trace comparison
covers 36 cells and 7,200 observations per side; every optimized observation uses
exactly 12 SQL statements, with p50 4.338–53.049 ms and maximum p95 64.360 ms.

## 6. Claims deliberately removed or bounded

The manuscript does not claim live-model accuracy, usability, authenticated actor
identity, process isolation, production effectiveness, cross-harness generality,
industrial scale, security proof, unbounded proof, total SQLite refinement, correct
human judgment, or independent reproduction. The comparator gap and trace ratios are
descriptive; they are not causal phase decompositions or hardware-independent guarantees.

## 7. Remaining limitations

The repeated benchmark covers three qualified configurations and synthetic fixtures; its
authority-invariance result is descriptive over the executed population, not a provider
ranking or general AI-safety result. The host authentication boundary is assumed trusted. Performance and storage
measurements are Windows/Python/SQLite fixed-grid observations. The necessity scenarios
cover the declared operational failure model, not all possible failures. Section 9
collects the detailed limitations while each experiment retains one local boundary.

## 8. Test, citation, and build results

Six focused C2 witness tests and all 364 implementation regression tests pass; the witness
source also passes the focused static check. Citation audit finds 53 active
keys matched one-to-one with 53 bibliography entries. The current JSS manuscript rebuild is
58 pages with zero undefined citations/references, zero LaTeX/package warnings, zero overfull
boxes, and zero underfull boxes. Section float barriers keep every table near its first-use
section instead of collecting tables after the references. Visual QA passed on the C2,
workflow, evidence-chain, authority-dataflow, and RQ8 pages. The canonical reviewer PDF is
`paper/main-r21-submission-ready-2026-09-06.pdf` (58 pages, 1,113,376 bytes); its final SHA-256 is
`4553fefdd94f65b67af70cad96ce823b3fd18e4c6dfe0141f6a3cfcdbcec5869`.

## 9. Evidence and integrity identity

The R21 paper-input manifest covers three normalized inputs, two generated tables,
88 source-evidence files, and 4,982,570 bytes; its SHA-256 is
`022cbb890600789293c377a78cd8920b762dac6bb1dff3324b62b66b2a5b1ca0`. The canonical
live-agent receipt SHA-256 is
`1c11dbf9d8d8bc196e847630fb44c266caf9070ee2980d39d120072734c231ec`. The final
non-self-referential revision manifest was built and verified after all document edits.
An isolated one-byte mutation probe produced an exact hash failure; the clean copy
remained valid. Historical failed runs are retained and excluded from citable inputs.

## 10. Reproducibility and package boundary

The standalone overlay includes source, formal, tools, runner, frozen evidence, paper
repository, locked live-agent `pyproject.toml`/`uv.lock`, and documented Windows/MiKTeX/
Poppler prerequisites. Copied baseline directories were byte-identity checked against
the prior locked release. The manuscript points to the immutable Git tag
`r21-jss-2026-09-06-v5`, whose package manifest covers the deposited files after the
semantic-audit and mixed-batch clarification update.

## 11. Venue, figure, and author-controlled items

Journal of Systems and Software remains the target. The core workflow now uses the exact PDF
export of the author-approved editable Canva design `DAHUNAr-imw`; a matching SVG converted
from that PDF is retained beside it. Canva rasterized some decorative layers, so this is a
hybrid export. The independently reconstructed pure vector is explicitly a fallback,
not represented as the same Canva file. The AI-generated concept raster is retained only as
non-submitted ideation provenance. The single author is Liang Hanghao, College of Computer
Science and Electronic Engineering, Hunan University; the corresponding address is
`zwu691403@gmail.com`. Funding is none, ethics review is recorded as not applicable because
there are no human participants or personal data, and acknowledgments may be added later.

## 12. READINESS VERDICT

SCIENTIFIC AND TECHNICAL FREEZE PASSED. ONLY JOURNAL-PORTAL AND COVER-LETTER CONFIRMATIONS
REMAIN OUTSIDE THE MANUSCRIPT.
