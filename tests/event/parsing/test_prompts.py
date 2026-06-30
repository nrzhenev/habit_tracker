import pytest

from app.user.schema import UserSettingsSchema
from app.event.parsing.prompts import build_event_parsing_prompt

pytestmark = pytest.mark.unit


def test_should_include_current_time_context():
    prompt = build_event_parsing_prompt(UserSettingsSchema(timezone="UTC"))
    assert "Current time" in prompt
