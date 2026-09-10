import pytest

from app.ui.pages.ai_vector import ContextError, parse_context


def test_parse_context_accepts_json_object() -> None:
    assert parse_context('{"total_quantity": 10}') == {"total_quantity": 10}


@pytest.mark.parametrize("raw", ["[]", "bad"])
def test_parse_context_rejects_invalid_input(raw: str) -> None:
    with pytest.raises(ContextError):
        parse_context(raw)
