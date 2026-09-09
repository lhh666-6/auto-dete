from importlib import import_module
from copy import deepcopy

import pytest


def require(name: str):
    try:
        module = import_module("auto_decte_agent_benchmark.tool_surface")
    except ModuleNotFoundError:
        module = None
    assert module is not None, "tool_surface module is missing"
    assert hasattr(module, name), f"tool_surface is missing {name}"
    return getattr(module, name)


def test_canonical_surface_exposes_only_proposal_and_verification() -> None:
    surface = require("canonical_tool_surface")()

    assert [tool["name"] for tool in surface["tools"]] == [
        "auto_decte_propose",
        "auto_decte_verify",
    ]
    assert all(tool["authority_effect"] != "authoritative_write" for tool in surface["tools"])


def test_openai_and_deepseek_translations_are_logically_equivalent() -> None:
    surface = require("canonical_tool_surface")()
    openai = require("openai_tool_schemas")(surface)
    deepseek = require("deepseek_tool_schemas")(surface)
    assert_equivalent = require("assert_logical_tool_equivalence")

    assert_equivalent(surface, {"openai": openai, "deepseek": deepseek})


def test_equivalence_rejects_an_extra_confirmation_tool() -> None:
    surface = require("canonical_tool_surface")()
    deepseek = require("deepseek_tool_schemas")(surface)
    deepseek.append(
        {
            "name": "confirm",
            "description": "forbidden",
            "input_schema": {"type": "object", "properties": {}, "required": []},
        }
    )

    with pytest.raises(ValueError, match="tool set"):
        require("assert_logical_tool_equivalence")(surface, {"deepseek": deepseek})


def test_equivalence_rejects_changed_required_arguments() -> None:
    surface = require("canonical_tool_surface")()
    openai = deepcopy(require("openai_tool_schemas")(surface))
    openai[0]["inputSchema"]["required"].remove("parent_certificate_id")

    with pytest.raises(ValueError, match="schema"):
        require("assert_logical_tool_equivalence")(surface, {"openai": openai})


def test_equivalence_ignores_only_presentation_metadata() -> None:
    surface = require("canonical_tool_surface")()
    openai = require("openai_tool_schemas")(surface)
    deepseek = require("deepseek_tool_schemas")(surface)
    openai[0]["inputSchema"]["title"] = "ProposeArguments"
    openai[0]["inputSchema"]["properties"]["value"]["title"] = "Value"

    require("assert_logical_tool_equivalence")(
        surface,
        {"openai": openai, "deepseek": deepseek},
    )
