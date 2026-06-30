import pytest

from app.user.schema import UserSettingsSchema
from app.expense.parsing.prompts import build_expense_parsing_prompt

pytestmark = pytest.mark.unit


def test_should_include_default_currency():
    prompt = build_expense_parsing_prompt(UserSettingsSchema(default_currency="RUB"))
    assert "RUB" in prompt
    assert "Default currency" in prompt


def test_should_include_current_time_context():
    prompt = build_expense_parsing_prompt(UserSettingsSchema(timezone="UTC"))
    assert "Current time" in prompt
