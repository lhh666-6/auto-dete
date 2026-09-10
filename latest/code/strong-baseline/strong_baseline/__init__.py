"""Strengthened transactional value-audit baseline (B1) for Auto-Decte.

This package implements Phase 2/4/5/6 of
``Auto-Decte_Baseline_Prompt_PaperAligned_v3.2.md``:

* ``B1 = transactional_value_audit`` -- a conventional transactional
  value-audit baseline that is strictly stronger than the frozen B0
  (``evidence/r27-standard-practice-baseline/run_baseline.py``) on conventional
  transactional/audit safeguards, while its human authorization remains
  **value-bound** and does not name the exact reviewed candidate.
* ``Full = candidate_bound`` -- the candidate-bound policy realized with the
  paper's real implementation vocabulary (human decision + immutable
  authorization binding + content-addressed certificate identity), used as the
  in-process comparator for E1.

Nothing in this package writes to the paper repository.  The frozen B0
harness is *imported* (hash-pinned) and never modified; see
:mod:`strong_baseline.b0_bridge`.
"""

from __future__ import annotations

__all__ = ["b0_bridge", "core", "policies", "cases", "analysis", "evidence"]
