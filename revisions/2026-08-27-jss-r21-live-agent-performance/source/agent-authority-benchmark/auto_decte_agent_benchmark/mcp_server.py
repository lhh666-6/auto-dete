"""Expose exactly the benchmark's provider-neutral proposal and verification tools."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Protocol

from mcp.server.fastmcp import FastMCP

from .bridge_client import BridgeClient, BridgeConfig
from .tool_surface import canonical_tool_surface


class ModelBridge(Protocol):
    def model(self, operation: str, **values: object) -> dict[str, Any]: ...


def create_server(bridge: ModelBridge) -> FastMCP:
    server = FastMCP(
        "auto-decte-agent-authority-benchmark",
        instructions=(
            "Candidate-only surface. Proposal and verification never admit an authoritative fact. "
            "No confirmation tool exists."
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
        value: Any,
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

    canonical = {tool["name"]: tool["input_schema"] for tool in canonical_tool_surface()["tools"]}
    for name, schema in canonical.items():
        server._tool_manager._tools[name].parameters = schema

    return server


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--implementation-root", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    args = parser.parse_args()
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
