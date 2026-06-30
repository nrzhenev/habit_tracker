import json
import datetime

import pytest

from app.activity.schema import ActivityParsed
from app.activity.parsing.parser import parse_activity_response

pytestmark = pytest.mark.unit


def test_should_parse_full_activity():
    result = parse_activity_response(
        '{"started_at":"2025-01-01T10:00:00+00:00",'
        '"ended_at":"2025-01-01T10:30:00+00:00","category":"running"}'
    )
    assert result == ActivityParsed(
        started_at=datetime.datetime(2025, 1, 1, 10, tzinfo=datetime.timezone.utc),
        ended_at=datetime.datetime(2025, 1, 1, 10, 30, tzinfo=datetime.timezone.utc),
        category="running",
    )


def test_should_parse_minimal_activity():
    result = parse_activity_response("{}")
    assert result == ActivityParsed(started_at=None, ended_at=None, category=None)


def test_should_raise_on_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        parse_activity_response("not json")
