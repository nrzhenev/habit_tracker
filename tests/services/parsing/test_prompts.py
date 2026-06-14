import pytest

from app.schemas.user_settings import UserSettingsSchema
from app.services.parsing.prompts import build_classification_prompt

pytestmark = pytest.mark.unit


def test_should_include_default_currency():
    prompt = build_classification_prompt(UserSettingsSchema(default_currency="RUB"))
    assert "RUB" in prompt
    assert "Default currency" in prompt
