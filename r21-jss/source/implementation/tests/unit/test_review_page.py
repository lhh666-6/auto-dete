import pytest

from app.ui.pages.review import ReviewValuesError, parse_review_values


def test_parse_review_values_accepts_a_json_object() -> None:
    assert parse_review_values('{"employee_id": "E001", "total_quantity": 25}') == {
        "employee_id": "E001",
        "total_quantity": 25,
    }


@pytest.mark.parametrize("raw", ["[]", '"text"', "{bad json}"])
def test_parse_review_values_rejects_non_object_or_invalid_json(raw: str) -> None:
    with pytest.raises(ReviewValuesError):
        parse_review_values(raw)
