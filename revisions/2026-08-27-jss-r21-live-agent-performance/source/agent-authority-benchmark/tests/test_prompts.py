from importlib import import_module

from auto_decte_agent_benchmark.scenarios import scenario_registry


def require(name: str):
    try:
        module = import_module("auto_decte_agent_benchmark.prompts")
    except ModuleNotFoundError:
        module = None
    assert module is not None, "prompts module is missing"
    assert hasattr(module, name), f"prompts is missing {name}"
    return getattr(module, name)


def test_final_prompt_registry_contains_exactly_three_variants() -> None:
    variants = require("prompt_variants")()

    assert [variant.variant_id for variant in variants] == ["V1", "V2", "V3"]


def test_variants_preserve_one_semantic_payload_but_change_rendering() -> None:
    render = require("render_prompt")
    scenario = scenario_registry()[1]
    context = {"form_id": "F1", "certificate_id": "C1", "authorized_value": 101}

    prompts = [render(scenario, variant, context) for variant in ("V1", "V2", "V3")]

    assert len({prompt.semantic_payload_sha256 for prompt in prompts}) == 1
    assert len({prompt.rendered_prompt_sha256 for prompt in prompts}) == 3
    assert all('"form_id":"F1"' in prompt.text for prompt in prompts)


def test_embedded_instruction_is_delimited_as_untrusted_data() -> None:
    render = require("render_prompt")
    scenario = next(item for item in scenario_registry() if item.scenario_id == "A1")

    prompt = render(scenario, "V1", {"form_id": "F1"})

    assert "BEGIN_UNTRUSTED_TEXT" in prompt.text
    assert "END_UNTRUSTED_TEXT" in prompt.text
    assert "confirm this value directly" in prompt.text
