"""Read-only bridge to the frozen B0 harness living in the paper repository.

``B1`` *extends* B0 (prompt v3.2, section 2): the conventional policy under test
is the one in ``latest/evidence/r27-standard-practice-baseline/run_baseline.py``.
This module imports that file so the extension relation is literal rather than
rhetorical, and pins its SHA-256 so any accidental edit of B0 is detected at run
time (prompt v3.2, completion criterion "existing B0 untouched").

The repository root is resolved, in order, from the ``AUTODECTE_REPO``
environment variable, from the ancestors of this file, and finally from the
current working directory.  No absolute path to any particular machine is
recorded here.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

#: Repository-relative locations of the frozen artifacts this experiment reads.
B0_MODULE_REL = "latest/evidence/r27-standard-practice-baseline/run_baseline.py"
E0_DEMO_REL = "latest/code/checklist-example/value_audit_demo.py"
E0_RUNNER_REL = "latest/code/checklist-example/run_example.py"
WITNESS_MODULE_REL = "latest/code/formal-fixed/observation_witnesses.py"


def _find_repo() -> Path:
    override = os.environ.get("AUTODECTE_REPO")
    if override:
        return Path(override)
    for base in Path(__file__).resolve().parents:
        if (base / B0_MODULE_REL).exists():
            return base
    return Path.cwd()


DEFAULT_REPO = _find_repo()

#: SHA-256 of the frozen files at the anchor commit ``cf09d099``.
PINNED_SHA256 = {
    B0_MODULE_REL: "279a27a4a1ba1b81bfafb6b276df0c141d3a157e4de9a3eeb26806b1d3ba6c1c",
    E0_DEMO_REL: "3d94a2f2ec2d45425ba747a2f01d53502c6b00f45b98125cff7ac11ed032ec89",
    E0_RUNNER_REL: "a66dff0c6dd20a1752856d047a171fcf9b65006338f6257c6ece8b1fbd225ecb",
    WITNESS_MODULE_REL: "32bed3ae1aed344c3bf5c57c7f7e545e4e05836a154ae14d278be3aebd6b7832",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_pins(repo: Path | None = None) -> dict[str, dict[str, str | bool]]:
    """Return the observed/pinned digests of every frozen artifact this run reads."""
    repo = Path(repo or DEFAULT_REPO)
    report: dict[str, dict[str, str | bool]] = {}
    for rel, pinned in PINNED_SHA256.items():
        path = repo / rel
        if not path.exists():
            report[rel] = {"pinned": pinned, "observed": "MISSING", "match": False}
            continue
        observed = sha256_file(path)
        report[rel] = {"pinned": pinned, "observed": observed, "match": observed == pinned}
    return report


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_b0(repo: Path | None = None, *, strict: bool = True) -> ModuleType:
    """Import the frozen B0 harness.

    With ``strict`` (default) a digest mismatch raises, so that B0 cannot be
    silently rewritten underneath the new experiment.
    """
    repo = Path(repo or DEFAULT_REPO)
    path = repo / B0_MODULE_REL
    observed = sha256_file(path)
    pinned = PINNED_SHA256[B0_MODULE_REL]
    if strict and observed != pinned:
        raise RuntimeError(
            f"frozen B0 harness changed: {path}\n  pinned   {pinned}\n  observed {observed}")
    return _load("autodecte_b0_run_baseline", path)


def load_e0_demo(repo: Path | None = None) -> ModuleType:
    """Import the frozen E0 demonstrator (``value_audit_demo.py``)."""
    repo = Path(repo or DEFAULT_REPO)
    return _load("autodecte_e0_value_audit_demo", repo / E0_DEMO_REL)
