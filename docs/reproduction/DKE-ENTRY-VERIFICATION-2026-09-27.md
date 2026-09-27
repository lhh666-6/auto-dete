# DKE reviewer entry verification — September 27, 2026

This check concerns the reviewer entry point and its commands, starting from
manuscript/package commit `ae26ffc0d8a15cac5572770897aaa0f2a57aba8c`.
It does not replace the fixed experimental deposit or its measurements.

| Command/check | Result checked in this session |
|---|---|
| `prepare` | 173 files extracted from the two fixed commits; selected source/input hashes verified; archived databases excluded. |
| Clean sparse checkout | Preparation and archived reanalysis also passed in a separate clone containing only the entry point and root files. |
| `verify` | E1/E2 aggregates recomputed from raw records; all E3 per-cell summaries recomputed from 22,400 raw timings and matched. |
| `test` | Ten supplementary tests passed. |
| `formal` | Nineteen Python witness tests passed. |
| `e1` | Full 495-case execution and automatic comparison to the deposit. See the receipt below. |
| `e2` | Full 60-case execution and automatic comparison to the deposit. See the receipt below. |
| E3 dependency/fixture smoke check | All four sections executed with the original script's explicitly reduced pilot grid; this was a setup check, not a fresh full benchmark. |
| Output preservation | Preparation over an existing workspace refused; its snapshot remained byte-identical. |
| Source integrity | A deliberate temporary source change was detected; original bytes were restored and hashes rechecked. |

The E2 check used the installed Windows Chrome through `DKE_CHROME` and the
reviewer driver package Playwright 1.58.0. Its disposable adapter changed only
the browser launch path. It did not modify the archived driver or case logic.

The current manuscript, supplement, tables, fixed experiment scripts and
archived results were unchanged. This check did not rerun the full E3 timing
grid, the Alloy solver, or hosted-model calls. The reviewer guide distinguishes
these activities from deterministic reanalysis and fresh E1/E2 execution.

The accompanying [receipt](DKE-ENTRY-VERIFICATION-2026-09-27.json) records the
checked aggregates, runtime and source pins. Reviewers can generate their own
receipts with the commands in the [reviewer guide](../../REVIEWER_GUIDE.md).
