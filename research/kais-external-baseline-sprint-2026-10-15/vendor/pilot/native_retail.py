"""Offline bridge to exact, pinned upstream RetailDB/RetailTools.

The tau2 package initializer starts broad runner imports. We provide only its
package namespace and import the unchanged Retail implementation underneath it.
No tool methods, tool decorators, data models, or state semantics are patched.
This is reference-path replay, not an official end-to-end tau evaluation.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib
import importlib.machinery
import json
import os
from pathlib import Path
import sys
import types
from typing import Any

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
UPSTREAM = SOURCE / "tau2-bench"
DATA = UPSTREAM / "data" / "tau2" / "domains" / "retail"
TARGET_TOOL = "modify_pending_order_address"
_native = None


def verify_source() -> dict:
    manifest = json.loads((SOURCE / "manifest.json").read_text(encoding="utf-8"))
    for item in manifest["artifacts"]:
        path = ROOT / item["path"]
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != item["sha256"]:
            raise ValueError(f"Pinned source changed: {path}")
    return {"commit": manifest["commit"], "verified_files": len(manifest["artifacts"])}


def _load_native():
    global _native
    if _native is not None:
        return _native
    verify_source()
    # Supported python-dotenv >= 1.1 switch prevents any .env discovery/read.
    os.environ["PYTHON_DOTENV_DISABLED"] = "1"
    os.environ["TAU2_DATA_DIR"] = str(UPSTREAM / "data")
    sys.dont_write_bytecode = True
    native_package = UPSTREAM / "src" / "tau2"
    if "tau2" in sys.modules:
        existing_paths = {str(Path(p).resolve()) for p in getattr(sys.modules["tau2"], "__path__", [])}
        if str(native_package.resolve()) not in existing_paths:
            raise RuntimeError("Another tau2 installation is already imported; use a fresh process.")
    else:
        package = types.ModuleType("tau2")
        package.__path__ = [str(native_package)]
        package.__package__ = "tau2"
        package.__spec__ = importlib.machinery.ModuleSpec("tau2", loader=None, is_package=True)
        sys.modules["tau2"] = package
    model_module = importlib.import_module("tau2.domains.retail.data_model")
    tools_module = importlib.import_module("tau2.domains.retail.tools")
    _native = (model_module.RetailDB, tools_module.RetailTools)
    return _native


def load_tasks() -> list[dict]:
    return json.loads((DATA / "tasks.json").read_text(encoding="utf-8"))


def load_task(task_id: str) -> dict:
    matches = [task for task in load_tasks() if str(task["id"]) == str(task_id)]
    if len(matches) != 1:
        raise ValueError(f"Expected one task {task_id}, found {len(matches)}")
    return matches[0]


def _json_value(value):
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {k: _json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(v) for v in value]
    return deepcopy(value)


class NativeRetail:
    def __init__(self, task: dict | None = None, snapshot: dict | None = None):
        RetailDB, RetailTools = _load_native()
        if task is not None and task.get("initial_state") is not None:
            raise ValueError("This minimal bridge does not silently apply custom task initial_state.")
        raw = deepcopy(snapshot) if snapshot is not None else json.loads((DATA / "db.json").read_text(encoding="utf-8"))
        self.db = RetailDB.model_validate(raw)
        self.toolkit = RetailTools(self.db)
        self.task_id = str(task["id"]) if task is not None else None

    def snapshot(self) -> dict:
        """Independent serializable copy of actual native DB state."""
        return self.db.model_dump(mode="json")

    def order(self, order_id: str) -> dict:
        return self.db.orders[order_id].model_dump(mode="json")

    def execute(self, tool_name: str, arguments: dict) -> Any:
        """Call the unmodified native method through upstream use_tool."""
        return _json_value(self.toolkit.use_tool(tool_name, **deepcopy(arguments)))

    def is_write(self, tool_name: str) -> bool:
        if tool_name not in self.toolkit.tools:
            raise KeyError(tool_name)
        return bool(getattr(self.toolkit.tools[tool_name], "__mutates_state__", False))

    def replay(self, actions: list[dict]) -> list[dict]:
        records = []
        for action in actions:
            result = self.execute(action["name"], action["arguments"])
            records.append({"action_id": action.get("action_id"), "name": action["name"],
                            "arguments": deepcopy(action["arguments"]), "result": result})
        return records


def replay_reference(task: dict) -> tuple[NativeRetail, list[dict]]:
    environment = NativeRetail(task)
    records = environment.replay(task["evaluation_criteria"]["actions"])
    return environment, records


def address_task_inventory() -> list[dict]:
    """Structural eligibility only; no execution outcomes are inspected."""
    probe = NativeRetail()
    rows = []
    for task in sorted(load_tasks(), key=lambda item: int(item["id"])):
        actions = task["evaluation_criteria"]["actions"]
        addresses = [a for a in actions if a["name"] == TARGET_TOOL]
        writes = [a for a in actions if probe.is_write(a["name"])]
        if not addresses:
            continue
        rows.append({"task_id": task["id"], "address_action_count": len(addresses),
                     "write_action_count": len(writes), "write_tool_names": [a["name"] for a in writes],
                     "initial_state_is_null": task.get("initial_state") is None,
                     "eligible_single_write": len(addresses) == 1 and len(writes) == 1 and task.get("initial_state") is None,
                     "eligible_one_target_with_reference_context": len(addresses) == 1 and task.get("initial_state") is None})
    return rows


if __name__ == "__main__":
    print(json.dumps({"source": verify_source(), "address_tasks": address_task_inventory()}, indent=2))
