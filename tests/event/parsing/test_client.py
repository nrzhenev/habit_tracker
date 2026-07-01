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
from app.event.parsing.client import LLMEventParser
from app.event.schema import EventParsed

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
    return UserSettingsSchema(default_currency="USD", timezone="UTC")


async def test_parser_should_call_llm(user_settings):
    stub = StubGroqClient(
        return_json='{"action":"woke up","occurred_at":"2025-01-01T07:00:00+00:00"}'
    )
    parser = LLMEventParser(client=stub)
    result = await parser.run("Woke up at 7am", user_settings)
    assert result == EventParsed(
        action="woke up",
        occurred_at=datetime.datetime(2025, 1, 1, 7, tzinfo=datetime.timezone.utc),
    )


async def test_should_raise_groq_api_error(user_settings):
    stub = StubGroqClient(raise_error=GroqApiError(500, "Internal error"))
    parser = LLMEventParser(client=stub)
    with pytest.raises(GroqApiError):
        await parser.run("test", user_settings)
