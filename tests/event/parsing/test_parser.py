import json
import datetime

import pytest

from app.event.schema import EventParsed
from app.event.parsing.parser import parse_event_response

pytestmark = pytest.mark.unit


def test_should_parse_full_event():
    result = parse_event_response(
        '{"action":"woke up","occurred_at":"2025-01-01T07:00:00+00:00"}'
    )
    assert result == EventParsed(
        action="woke up",
        occurred_at=datetime.datetime(2025, 1, 1, 7, tzinfo=datetime.timezone.utc),
    )


def test_should_parse_minimal_event():
    result = parse_event_response('{"action":"meeting"}')
    assert result == EventParsed(action="meeting", occurred_at=None)


def test_should_raise_on_missing_action():
    with pytest.raises(ValueError, match="action"):
        parse_event_response('{"occurred_at":"2025-01-01T07:00:00+00:00"}')


def test_should_raise_on_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        parse_event_response("not json")
