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
from app.activity.parsing.client import LLMActivityParser
from app.activity.schema import ActivityParsed

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
        return_json='{"started_at":"2025-01-01T10:00:00+00:00",'
        '"ended_at":"2025-01-01T10:30:00+00:00","category":"running"}'
    )
    parser = LLMActivityParser(client=stub)
    result = await parser.parse("Ran for 30 minutes", user_settings)
    assert result == ActivityParsed(
        started_at=datetime.datetime(2025, 1, 1, 10, tzinfo=datetime.timezone.utc),
        ended_at=datetime.datetime(2025, 1, 1, 10, 30, tzinfo=datetime.timezone.utc),
        category="running",
    )


async def test_should_raise_groq_api_error(user_settings):
    stub = StubGroqClient(raise_error=GroqApiError(500, "Internal error"))
    parser = LLMActivityParser(client=stub)
    with pytest.raises(GroqApiError):
        await parser.parse("test", user_settings)
