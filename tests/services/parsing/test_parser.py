import json

import pytest

from app.services.parsing.parser import parse_llm_response
from app.schemas.parsing import ClassificationResponse

pytestmark = pytest.mark.unit


def test_should_classify_as_expense():
    result = parse_llm_response(
        '{"type":"expense","occurred_at":null,"currency":"RUB","items":["bread"],'
        '"amount":100,"category":"food","place":null}'
    )
    assert result == ClassificationResponse(type="expense")


def test_should_classify_as_activity():
    result = parse_llm_response(
        '{"type":"activity","started_at":"2025-01-01T10:00:00+03:00",'
        '"ended_at":"2025-01-01T10:30:00+03:00","category":"sport"}'
    )
    assert result == ClassificationResponse(type="activity")


def test_should_classify_as_event():
    result = parse_llm_response(
        '{"type":"event","action":"woke_up","occurred_at":"2025-01-01T07:00:00+03:00"}'
    )
    assert result == ClassificationResponse(type="event")


def test_should_raise_on_unknown_type():
    with pytest.raises(ValueError, match="Unknown type"):
        parse_llm_response('{"type":"unknown"}')


def test_should_raise_on_missing_type():
    with pytest.raises(KeyError):
        parse_llm_response('{"amount":100}')


def test_should_raise_on_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        parse_llm_response("not json")
