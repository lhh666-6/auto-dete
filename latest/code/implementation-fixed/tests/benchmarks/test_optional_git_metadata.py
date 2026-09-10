"""Source exports must not require a Git checkout to run benchmarks."""
import subprocess

import pytest

from benchmarks import pipeline_authority_benchmark, run_all


@pytest.mark.parametrize("module", [run_all, pipeline_authority_benchmark])
@pytest.mark.parametrize("error", [
    FileNotFoundError("git unavailable"),
    subprocess.CalledProcessError(128, ["git"]),
    subprocess.TimeoutExpired(["git"], 30),
])
def test_missing_git_metadata_is_unknown(module, error, monkeypatch):
    def unavailable(*args, **kwargs):
        raise error
    monkeypatch.setattr(module.subprocess, "run", unavailable)
    assert module._git("rev-parse", "HEAD") is None


@pytest.mark.parametrize("module", [run_all, pipeline_authority_benchmark])
@pytest.mark.parametrize("output", ["", "abc123\n"])
def test_available_git_metadata_is_preserved(module, output, monkeypatch):
    def available(*args, **kwargs):
        return subprocess.CompletedProcess(["git"], 0, output, "")
    monkeypatch.setattr(module.subprocess, "run", available)
    assert module._git("status", "--porcelain") == output.strip()
