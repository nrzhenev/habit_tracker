import datetime

import pytest

from app.core.llm_client.base import (
    ChatCompletionChoice,
    ChatCompletionResponse,
    ChatCompletionUsage,
    ChatMessage,
    LLMClient,
)
from app.core.llm_client.groq import GroqApiError
from app.user.schema import UserSettingsSchema
from app.expense.parsing.client import LLMExpenseParser
from app.expense.schema import ExpenseParsed

pytestmark = pytest.mark.unit


class StubGroqClient(LLMClient):
    def __init__(
        self,
        *,
        return_json: str | None = None,
        raise_error: Exception | None = None,
    ):
        self._return_json = return_json
        self._raise_error = raise_error

    async def chat_completion(self, *args, **kwargs) -> ChatCompletionResponse:
        if self._raise_error is not None:
            raise self._raise_error
        return ChatCompletionResponse(
            id="test",
            model="test-model",
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=self._return_json),
                    finish_reason="stop",
                )
            ],
            usage=ChatCompletionUsage(
                prompt_tokens=100, completion_tokens=50, total_tokens=150
            ),
        )


@pytest.fixture
def user_settings():
    return UserSettingsSchema(default_currency="RUB", timezone="UTC")


async def test_parser_should_call_llm(user_settings):
    stub = StubGroqClient(
        return_json='{"occurred_at":"2025-01-01T00:00:00+00:00","amount":500.0,'
        '"currency":"RUB","category":"food","place":"Perekrestok",'
        '"items":["bread","milk"]}'
    )
    parser = LLMExpenseParser(client=stub)
    result = await parser.run("Test Message", user_settings)
    assert result == ExpenseParsed(
        occurred_at=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
        amount=500.0,
        currency="RUB",
        category="food",
        place="Perekrestok",
        items=["bread", "milk"],
    )


async def test_should_raise_groq_api_error(user_settings):
    stub = StubGroqClient(raise_error=GroqApiError(500, "Internal error"))
    parser = LLMExpenseParser(client=stub)
    with pytest.raises(GroqApiError):
        await parser.run("test", user_settings)
