# Annotation procedure: deposited source documents

This file records where the deposited procedure documents came from, how the
blinding was performed, and one discrepancy between the pre-registered
convention and the practice reported in the manuscript. It supplements
`README-REPRODUCE.md`, which covers the label data and the agreement statistics.

## Source packages

| Package | SHA-256 (of the .zip) |
|---|---|
| `独立盲标教学与填写包` (2026-09-07, textual-acknowledgment task) | `b657d3f693de5fa3591cbe32890459ca286ff1a1ba93e40894217066ec1bcd36` |
| `独立盲标包-B-任务完成` (2026-09-09, benign task completion) | `260ec876e32f3806489e7e3bc5eef979131f32953b0535babc57d049e1d34067` |

The archives that annotators actually received are **not** redistributed. The
files below are byte-exact extractions, so an authorised holder of either
archive can confirm that what is deposited here is what was issued.

## Deposited files

| File | SHA-256 | Byte-exact? |
|---|---|---|
| `CODING-MANUAL-zh.md` | `216aaa8638fdcf7072776bc65b2792d52d4210fa09be2a49f444d7cb3743c5f5` | yes |
| `RETURN-AND-STATISTICS-PROTOCOL-zh.md` | `bfaa5001ba1cd81017d117fcf5ccfeb5a9be7216600cfb40e322463cd9517568` | yes |
| `BLIND-PACKAGE-README-zh.txt` | `149ce7b6fef485a41211a77e5771966d7c9a4d4f984d893c6e0b3242ef057b03` | yes |
| `BLIND-PACKAGE-MANIFEST.json` | `315d7cce165ec18fc66e97527a08002dfb13b4216f0f52e5d863fdc31dfb727b` | yes |
| `CODING-MANUAL-en.md` | this translation | added 2026-09-11, not part of the issued package |
| `RETURN-AND-STATISTICS-PROTOCOL-en.md` | this translation | added 2026-09-11, not part of the issued package |

The first four values reproduce the hashes recorded in the package's own
manifest (`BLIND-PACKAGE-MANIFEST.json`), except that the manifest is
self-referential and therefore does not list itself.

`TEXTUAL-ACKNOWLEDGMENT-RUBRIC-2026-09-07.md` (SHA-256
`eb064e5f26d9d35157e248890d4283dfa00cf57e4337cb8b3090ddc1b579f3ee`) is the
shared rubric issued with the earlier textual-acknowledgment package; it is
deposited alongside the acknowledgment evidence.

## Blinding transformation

Both coders received the same workbook, in which columns A--C were fixed and
only D--G were theirs to fill. The transformation applied before issue was:

- `execution_id` -> `EXEC-XXXX`, `session_id` -> `SESSION-XXXX`,
  `scenario_id` -> `SCENARIO-XXXX` (768, 757, and 360 replacements recorded);
- the scenario word was additionally rewritten in 18 places, in 4 cases still
  readable in the issued files;
- previous labels, model configuration identifiers, prompt variants,
  repetitions, the author mapping table, and the paper's scoring outcomes were
  withheld from the package;
- row order was shuffled with seed `20260909`.

The package manifest records the residual leak counts after these edits:
`exec_pattern` 0, `session_id` 0, `scenario_json` 0, `model_name` 0, and
`scenario_word_per_case` 4. Blinding can therefore be claimed for the removed
identifiers, but not as a guarantee that the response text itself carries no
clue; the coding manual accordingly asks the coder to record any metadata clue
noticed in column G.

## Freeze

The issued workbook has 360 rows (B1--B4, 90 each) with all label, rationale,
and uncertainty cells blank, and `evaluable_by_original_rule` = 335 with 25
unscorable runs. `BLIND-PACKAGE-MANIFEST.json` records `rows: 360`,
`shuffle_seed: 20260909`, and `private_key_in_blind_package: false`.

## Discrepancy: adjudication by a non-author third party was not obtained

`RETURN-AND-STATISTICS-PROTOCOL-zh.md` step 3 states that disagreements should be
adjudicated by **a non-author third party (or by consensus)**. That is not what
happened. One coder is the second author and the adjudicator was the first
author, so the adjudication was author-involved and, for the 12 adjudicated
items, adjudicated by a single author rather than by a third party or by
consensus.

The manuscript and supplement disclose that the annotation was author-involved
and that the adjudication was not independent third-party adjudication. What the
pre-registered convention asked for and did not receive is recorded here so that
the published description is not read as compliance with a protocol that was in
fact met only in part. The original two label columns are preserved unchanged,
all 11 pre-adjudication human--rule disagreements remain listed in
`disagreements-*.csv`, and no adjudicated label replaces a pre-adjudication
label in the agreement analysis.

## Not deposited

- The issued archives themselves, and the completed workbooks. Their SHA-256
  values are in `README-REPRODUCE.md` and in `BLIND-PACKAGE-MANIFEST.json`; the
  normalised CSV is a complete 360-row extraction of the label columns.
- `01_盲标教学与填写指南.pdf` (issued teaching guide) and
  `03_完整原文阅读册.html` (full-text reader). Both reproduce task text and model
  responses that are already derived from the frozen matrix, and the reader
  duplicates deposited frozen inputs. Their hashes are recorded in
  `BLIND-PACKAGE-MANIFEST.json`.
- `rows.json` and `04_备用填写表.csv`, which are the reader and the workbook in
  another format.
- The AI pre-annotation workbook (`正式标注.xlsx`, SHA-256
  `a1b6cf9334c4b8a79f199245f7202a17b0368e9d346df42d9ca82d35d0fa7284`). It
  self-declares that its D--G columns were pre-labelled by an AI under the same
  manual, states that it "must not be passed off as an independent human result
  that did not use AI", and leaves the coder-identity and independence
  declaration fields blank. It is a working aid, not a returned annotation; the
  deposited A1 labels are not its output (the two agree on 357 of 360 rows).
