# Post-Pilot Final Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Pilot-to-Final resource decision, source freeze, and mandatory Final freeze check reproducible and fail-closed.

**Architecture:** A non-networked post-Pilot module validates and binds Pilot inputs before creating a resource decision and Final configuration. A create-only freeze builder stages the minimum runtime tree, while the existing runner verifies that frozen tree before and after every live Final dispatch.

**Tech Stack:** Python 3.11, pathlib, argparse, JSON, pytest, Ruff.

---

### Task 1: Bind the resource decision to a complete Pilot

**Files:**
- Create: `source/agent-authority-benchmark/auto_decte_agent_benchmark/post_pilot.py`
- Create: `source/agent-authority-benchmark/tests/test_post_pilot.py`

- [ ] Write a failing test whose fixture contains a valid 112-coordinate Pilot manifest,
  qualification roster, summary, and provider-credit attestation; assert that the new function
  writes a create-only gate with Pilot/config/credit SHA-256 bindings.
- [ ] Run `pytest tests/test_post_pilot.py -q` and confirm the import or API fails because the module
  is absent.
- [ ] Implement JSON loading, manifest verification, exact phase/count/roster checks, resource-row
  construction, no-overwrite JSON writing, and `decide_resource_gate` delegation.
- [ ] Add failing tests for incomplete/tampered Pilot, false provider credit, roster mismatch, and an
  existing output; implement only the validation needed to pass them.
- [ ] Run `pytest tests/test_post_pilot.py tests/test_resource_gate.py -q` and commit the task.

### Task 2: Stage a minimal verified Final source tree

**Files:**
- Modify: `source/agent-authority-benchmark/auto_decte_agent_benchmark/freeze.py`
- Modify: `source/agent-authority-benchmark/tests/test_freeze.py`

- [ ] Write a failing test that stages benchmark runtime source, generated Final config, and the
  implementation runtime allow-list into a new root and excludes `.venv`, caches, Pilot output,
  secrets, and unrelated evidence.
- [ ] Run the focused test and confirm the staging API is missing.
- [ ] Implement `stage_final_freeze` with safe relative allow-lists, create-only destinations,
  failure-marker preservation, runtime metadata, and `write_frozen_manifest`.
- [ ] Add and satisfy tests for missing required inputs, existing output, manifest tamper detection,
  and absence of secret material.
- [ ] Run `pytest tests/test_freeze.py -q` and commit the task.

### Task 3: Enforce the freeze at the Final execution boundary

**Files:**
- Modify: `source/agent-authority-benchmark/auto_decte_agent_benchmark/runner.py`
- Modify: `source/agent-authority-benchmark/tests/test_runner.py`

- [ ] Write failing parser/dispatch tests showing that a live Final without `--frozen-root`, or with
  a tampered freeze, fails before the injected live runner records a call.
- [ ] Run the focused tests and confirm the missing enforcement causes the expected failures.
- [ ] Add `--frozen-root`; require it only for live Final; verify its path is the active revision
  root and call `verify_frozen_manifest` immediately before and after live dispatch.
- [ ] Add a passing test for a verified freeze and confirm Pilot plus dry-run semantics are unchanged.
- [ ] Run `pytest tests/test_runner.py tests/test_freeze.py -q` and commit the task.

### Task 4: Add stable commands and run the deterministic gate

**Files:**
- Modify: `source/agent-authority-benchmark/README_REPRODUCE.md`
- Modify: `revisions/2026-08-27-jss-r21-live-agent-performance/task_plan.md`
- Modify: `revisions/2026-08-27-jss-r21-live-agent-performance/progress.md`
- Modify: `revisions/2026-08-27-jss-r21-live-agent-performance/findings.md`

- [ ] Add exact post-Pilot gate, freeze, verify, Final dry-run, first-run, and resume commands. State
  that a blocked gate writes no Final config and no Final execution is authorized.
- [ ] Run the full package tests and require zero failures.
- [ ] Run Ruff and require zero diagnostics.
- [ ] Run the locked Pilot dry run and require 112 executions, four configurations, zero calls, and
  zero writes; exercise the post-Pilot tests rather than fabricating a real Pilot-3 result.
- [ ] Review the diff for historical evidence mutations, then commit only the new source/tests/docs.
