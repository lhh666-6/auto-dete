"""Subprocess client for the benchmark-specific trusted bridge."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
from typing import Any, Callable


BRIDGE_VERSION = "auto-decte.agent-benchmark-bridge.v2"


@dataclass(frozen=True, slots=True)
class BridgeConfig:
    data_root: Path
    implementation_root: Path
    python_executable: Path
    timeout_seconds: float = 30.0


class BridgeClient:
    def __init__(
        self,
        config: BridgeConfig,
        *,
        command_runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    ) -> None:
        self._config = config
        self._command_runner = command_runner

    def model(self, operation: str, **values: object) -> dict[str, Any]:
        return self._call("model", operation, **values)

    def host(self, operation: str, **values: object) -> dict[str, Any]:
        return self._call("host", operation, **values)

    def _call(self, surface: str, operation: str, **values: object) -> dict[str, Any]:
        request = {
            "bridge_version": BRIDGE_VERSION,
            "surface": surface,
            "operation": operation,
            "data_root": str(self._config.data_root.resolve()),
            **values,
        }
        environment = os.environ.copy()
        for credential_name in (
            "ANTHROPIC_AUTH_TOKEN",
            "OPENAI_API_KEY",
            "DEEPSEEK_API_KEY",
            "DS_API_KEY",
        ):
            environment.pop(credential_name, None)
        benchmark_source = Path(__file__).resolve().parents[1]
        environment["PYTHONPATH"] = os.pathsep.join(
            (str(benchmark_source), str(self._config.implementation_root.resolve()))
        )
        completed = self._command_runner(
            [
                str(self._config.python_executable.resolve()),
                "-m",
                "auto_decte_agent_benchmark.benchmark_bridge",
            ],
            cwd=self._config.implementation_root,
            env=environment,
            input=json.dumps(request, separators=(",", ":")),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=self._config.timeout_seconds,
            check=False,
        )
        try:
            envelope = json.loads(completed.stdout)
        except json.JSONDecodeError:
            raise RuntimeError("BENCHMARK_BRIDGE_INVALID_JSON") from None
        if (
            completed.returncode != 0
            or not isinstance(envelope, dict)
            or envelope.get("ok") is not True
            or envelope.get("bridge_version") != BRIDGE_VERSION
        ):
            raise RuntimeError("BENCHMARK_BRIDGE_REJECTED")
        result = envelope.get("result")
        if not isinstance(result, dict):
            raise RuntimeError("BENCHMARK_BRIDGE_RESULT_INVALID")
        return result
