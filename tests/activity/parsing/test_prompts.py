import pytest

from app.user.schema import UserSettingsSchema
from app.activity.parsing.prompts import build_activity_parsing_prompt

pytestmark = pytest.mark.unit


def test_should_include_current_time_context():
    prompt = build_activity_parsing_prompt(UserSettingsSchema(timezone="UTC"))
    assert "Current time" in prompt
