"""Canonical logical tool surface and provider schema translations."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


def canonical_tool_surface() -> dict[str, Any]:
    return {
        "schema_version": "auto-decte.logical-tool-surface.v2",
        "tools": [
            {
                "name": "auto_decte_propose",
                "description": (
                    "Persist an AI suggestion as a parent-linked candidate; never commits a fact."
                ),
                "authority_effect": "candidate_only",
                "input_schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "form_id": {"type": "string"},
                        "field_id": {"type": "string"},
                        "parent_certificate_id": {"type": "string"},
                        "value": {},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "session_id": {"type": "string"},
                        "execution_id": {"type": "string"},
                    },
                    "required": [
                        "form_id",
                        "field_id",
                        "parent_certificate_id",
                        "value",
                        "confidence",
                        "session_id",
                        "execution_id",
                    ],
                },
            },
            {
                "name": "auto_decte_verify",
                "description": "Read and hash-check a persisted candidate and its evidence.",
                "authority_effect": "read_only",
                "input_schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"certificate_id": {"type": "string"}},
                    "required": ["certificate_id"],
                },
            },
        ],
    }


def openai_tool_schemas(surface: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "name": tool["name"],
            "description": tool["description"],
            "inputSchema": deepcopy(tool["input_schema"]),
        }
        for tool in surface["tools"]
    ]


def deepseek_tool_schemas(surface: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "name": tool["name"],
            "description": tool["description"],
            "input_schema": deepcopy(tool["input_schema"]),
        }
        for tool in surface["tools"]
    ]


def assert_logical_tool_equivalence(
    surface: Mapping[str, Any],
    provider_schemas: Mapping[str, list[dict[str, Any]]],
) -> None:
    expected = {tool["name"]: tool["input_schema"] for tool in surface["tools"]}
    for provider, tools in provider_schemas.items():
        actual_names = {str(tool.get("name", "")) for tool in tools}
        if actual_names != set(expected):
            raise ValueError(f"{provider} tool set is not logically equivalent")
        for tool in tools:
            name = str(tool["name"])
            schema = tool.get("inputSchema", tool.get("input_schema"))
            if schema != expected[name]:
                raise ValueError(f"{provider} schema differs for {name}")
