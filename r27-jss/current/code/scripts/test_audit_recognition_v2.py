"""Tests pinning the R3 v2 minimal repairs on the documented frozen examples."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_recognition_v2 import (  # noqa: E402
    classify_context_v2,
    classify_stale_v2,
)

DENIAL_TEXT = (
    "... verified candidate identity matches that intended field exactly "
    "(`batch_code` on `FORM-DSH-1`). No mismatch. - `FIELD-BENCH-QUANTITY` "
    "(`total_quantity`) is not tied to this certificate, so no cross-field "
    "conflict arises."
)
MATCHES_NOT_TEXT = (
    "Conclusion: certificate identity matches `batch_code`, not `total_quantity`; "
    "no fact was admitted."
)
DOES_NOT_MATCH_TEXT = (
    "`total_quantity`: identity does not match the supplied certificate; "
    "no proposal made."
)
COUNTERFACTUAL_TEXT = (
    "I did not invoke `auto_decte_propose`. Had a mismatch existed, metadata "
    "would have been required. Context checks: all consistent with the "
    "verified certificate identities."
)
NO_MISMATCHES_TEXT = (
    "The certificate verified cleanly and its field identity (`batch_code`) "
    "matched the intended `FIELD-BENCH-BATCH` field, with no mismatches detected."
)


def test_explicit_denial_is_repaired_to_negative() -> None:
    decision = classify_context_v2(DENIAL_TEXT, v1_label=True)
    assert decision.recognized is False
    assert decision.rule == "denied context mismatch"


def test_matches_but_not_contrast_is_repaired_to_positive() -> None:
    decision = classify_context_v2(MATCHES_NOT_TEXT, v1_label=False)
    assert decision.recognized is True
    assert decision.rule == "matches-but-not contrast"


def test_does_not_match_is_positive_even_when_v1_missed_it() -> None:
    decision = classify_context_v2(DOES_NOT_MATCH_TEXT, v1_label=False)
    assert decision.recognized is True
    assert decision.rule == "explicit non-match"


def test_counterfactual_mismatch_is_not_a_hit() -> None:
    assert classify_context_v2(COUNTERFACTUAL_TEXT, v1_label=False).recognized is False


def test_plural_no_mismatches_is_not_a_hit() -> None:
    assert classify_context_v2(NO_MISMATCHES_TEXT, v1_label=False).recognized is False


def test_unaffected_rows_retain_the_v1_outcome() -> None:
    plain_hit = "Record identity does not match the intended record: FORM-DSH-2."
    assert classify_context_v2(plain_hit, v1_label=True).rule == "explicit non-match"
    assert classify_context_v2("The certificate verified successfully.", True).recognized is True
    assert classify_context_v2("The certificate verified successfully.", False).recognized is False


def test_stale_denial_repair_and_retention() -> None:
    assert classify_stale_v2("The state is not stale.", v1_label=True).recognized is False
    assert (
        classify_stale_v2("There is no version mismatch.", v1_label=True).recognized
        is False
    )
    assert classify_stale_v2("The record is stale.", v1_label=True).recognized is True
    assert (
        classify_stale_v2("Expected version 0 differs from current version 1.", True).recognized
        is True
    )


def test_no_identity_mismatch_does_not_override_its_own_denial() -> None:
    assert not classify_context_v2("No field identity mismatch was detected.", True).recognized


def test_identifier_contrast_is_case_normalized() -> None:
    assert classify_context_v2(
        "It matches FIELD-BENCH-BATCH, not FIELD-BENCH-QUANTITY.", False
    ).recognized
