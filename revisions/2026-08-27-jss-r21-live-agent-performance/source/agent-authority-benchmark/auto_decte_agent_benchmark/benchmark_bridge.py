"""Versioned trusted bridge for benchmark model tools and host challenges."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Mapping

from app.integrations import dsh_bridge as production_bridge

from .bridge_client import BRIDGE_VERSION
from .host_challenges import execute_challenge, prepare_scenario, self_test_scenario


MODEL_OPERATIONS = frozenset({"propose", "verify"})
HOST_OPERATIONS = frozenset(
    {
        "init-fixture",
        "export-receipt",
        "prepare-scenario",
        "execute-challenge",
        "self-test-scenario",
    }
)


def _require_text(request: dict[str, Any], key: str) -> str:
    value = request.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def handle_request(request: dict[str, Any]) -> dict[str, Any]:
    if request.get("bridge_version") != BRIDGE_VERSION:
        raise ValueError(f"bridge_version must equal {BRIDGE_VERSION}")
    surface = _require_text(request, "surface")
    operation = _require_text(request, "operation")
    allowed = MODEL_OPERATIONS if surface == "model" else HOST_OPERATIONS if surface == "host" else ()
    if operation not in allowed:
        raise PermissionError(f"operation {operation!r} is not exposed on {surface!r}")
    if surface == "host" and operation in {
        "prepare-scenario",
        "execute-challenge",
        "self-test-scenario",
    }:
        data_root = Path(_require_text(request, "data_root"))
        scenario_id = _require_text(request, "scenario_id")
        if operation == "prepare-scenario":
            result = prepare_scenario(data_root, scenario_id)
        elif operation == "execute-challenge":
            prepared = request.get("prepared")
            agent_evidence = request.get("agent_evidence")
            if not isinstance(prepared, Mapping) or not isinstance(agent_evidence, Mapping):
                raise ValueError("prepared and agent_evidence must be objects")
            result = execute_challenge(
                data_root,
                scenario_id,
                prepared,
                agent_evidence,
            )
        else:
            result = self_test_scenario(data_root, scenario_id)
        return {
            "ok": True,
            "bridge_version": BRIDGE_VERSION,
            "operation": operation,
            "result": result,
        }
    delegated = {**request, "bridge_version": production_bridge.BRIDGE_VERSION}
    envelope = production_bridge.handle_request(delegated)
    return {
        "ok": True,
        "bridge_version": BRIDGE_VERSION,
        "operation": operation,
        "result": envelope["result"],
    }


def main() -> int:
    try:
        raw = sys.stdin.buffer.read()
        if not raw:
            raise ValueError("stdin request is empty")
        request = json.loads(raw)
        if not isinstance(request, dict):
            raise ValueError("request must be a JSON object")
        response = handle_request(request)
    except Exception as error:
        response = {
            "ok": False,
            "bridge_version": BRIDGE_VERSION,
            "error": {"type": type(error).__name__, "message": str(error)},
        }
        sys.stdout.write(json.dumps(response, sort_keys=True, separators=(",", ":")))
        return 1
    sys.stdout.write(json.dumps(response, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
