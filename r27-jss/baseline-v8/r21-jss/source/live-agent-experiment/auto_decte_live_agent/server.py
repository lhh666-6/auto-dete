"""Expose the existing AUTO-DECTE bridge as two stdio MCP tools."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

BRIDGE_VERSION = "auto-decte.dsh-bridge.v1"


@dataclass(frozen=True, slots=True)
class BridgeConfig:
    data_root: Path
    implementation_root: Path
    python_executable: Path
    timeout_seconds: float = 20.0


class BridgeClient:
    def __init__(self, config: BridgeConfig) -> None:
        self._config = config

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
        environment["PYTHONPATH"] = str(self._config.implementation_root.resolve())
        completed = subprocess.run(
            [
                str(self._config.python_executable.resolve()),
                "-m",
                "app.integrations.dsh_bridge",
            ],
            cwd=self._config.implementation_root,
            env=environment,
            input=json.dumps(request),
            text=True,
            capture_output=True,
            timeout=self._config.timeout_seconds,
            check=False,
        )
        try:
            envelope = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise RuntimeError("AUTO_DECTE_BRIDGE_INVALID_JSON") from error
        if (
            completed.returncode != 0
            or not isinstance(envelope, dict)
            or envelope.get("ok") is not True
            or envelope.get("bridge_version") != BRIDGE_VERSION
        ):
            detail = envelope.get("error", {}) if isinstance(envelope, dict) else {}
            message = detail.get("message", "bridge request rejected")
            raise RuntimeError(f"AUTO_DECTE_BRIDGE_REJECTED: {message}")
        result = envelope.get("result")
        if not isinstance(result, dict):
            raise RuntimeError("AUTO_DECTE_BRIDGE_RESULT_INVALID")
        return result


def create_server(bridge: BridgeClient) -> FastMCP:
    server = FastMCP(
        "auto-decte-live-agent",
        instructions=(
            "Candidate-only AUTO-DECTE surface. Proposal and verification never confirm or write "
            "an authoritative fact. No confirmation tool exists."
        ),
        log_level="ERROR",
    )

    @server.tool(
        name="auto_decte_propose",
        description="Persist an AI suggestion as a parent-linked candidate; never commits a fact.",
        structured_output=True,
    )
    def propose(
        form_id: str,
        field_id: str,
        parent_certificate_id: str,
        value: float,
        confidence: float,
        session_id: str,
        execution_id: str,
    ) -> dict[str, Any]:
        return bridge.model(
            "propose",
            form_id=form_id,
            field_id=field_id,
            parent_certificate_id=parent_certificate_id,
            value=value,
            confidence=confidence,
            session_id=session_id,
            execution_id=execution_id,
        )

    @server.tool(
        name="auto_decte_verify",
        description="Read and hash-check a persisted AUTO-DECTE candidate and its evidence.",
        structured_output=True,
    )
    def verify(certificate_id: str) -> dict[str, Any]:
        return bridge.model("verify", certificate_id=certificate_id)

    return server


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--implementation-root", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    bridge = BridgeClient(
        BridgeConfig(
            data_root=args.data_root,
            implementation_root=args.implementation_root,
            python_executable=args.python,
        )
    )
    create_server(bridge).run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

