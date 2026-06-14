import pytest

from app.core.groq_client import (
    ChatCompletionChoice,
    ChatCompletionResponse,
    ChatCompletionUsage,
    ChatMessage,
    GroqApiError,
)
from app.schemas.parsing import ClassificationResponse
from app.schemas.user_settings import UserSettingsSchema
from app.services.entry_classification.client import LLMClassifier

pytestmark = pytest.mark.unit


class StubGroqClient:
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


class TestClassify:
    async def test_should_classify_as_expense(self, user_settings):
        stub = StubGroqClient(
            return_json='{"type":"expense","occurred_at":null,"currency":"RUB","items":["bread"],'
            '"amount":100,"category":"food","place":null}'
        )
        service = LLMClassifier(client=stub)
        result = await service.classify("Spent 100", user_settings)
        assert result == ClassificationResponse(type="expense")

    async def test_should_classify_as_activity(self, user_settings):
        stub = StubGroqClient(
            return_json='{"type":"activity","started_at":"2025-01-01T10:00:00+03:00",'
            '"ended_at":"2025-01-01T10:30:00+03:00","category":"sport"}'
        )
        service = LLMClassifier(client=stub)
        result = await service.classify("Ran for 30 minutes", user_settings)
        assert result == ClassificationResponse(type="activity")

    async def test_should_classify_as_event(self, user_settings):
        stub = StubGroqClient(
            return_json='{"type":"event","action":"woke_up","occurred_at":"2025-01-01T07:00:00+03:00"}'
        )
        service = LLMClassifier(client=stub)
        result = await service.classify("Woke up", user_settings)
        assert result == ClassificationResponse(type="event")

    async def test_should_raise_groq_api_error(self, user_settings):
        stub = StubGroqClient(raise_error=GroqApiError(500, "Internal error"))
        service = LLMClassifier(client=stub)
        with pytest.raises(GroqApiError):
            await service.classify("test", user_settings)
