from collections.abc import Callable
from typing import Generic, TypeVar

from app.config import settings
from app.core.llm_client import LLMClient, groq_client
from app.user.schema import UserSettingsSchema

T = TypeVar("T")

JSON_OBJECT_FORMAT = {"type": "json_object"}


class StructuredLLMTask(Generic[T]):
    """Generic single-turn LLM task returning a structured result.

    Builds a system prompt from user settings, sends the user content to the
    LLM, and hands the raw response string to a parser callable.
    """

    def __init__(
        self,
        prompt_builder: Callable[[UserSettingsSchema], str],
        response_parser: Callable[[str], T],
        client: LLMClient | None = None,
        response_format: dict[str, str] | None = JSON_OBJECT_FORMAT,
    ):
        self._prompt_builder = prompt_builder
        self._response_parser = response_parser
        self._client = client or groq_client
        self._response_format = response_format

    async def run(self, user_content: str, user_settings: UserSettingsSchema) -> T:
        system_prompt = self._prompt_builder(user_settings)
        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]
        response = await self._client.chat_completion(
            messages=messages,
            model=settings.GROQ_MODEL,
            temperature=settings.GROQ_TEMPERATURE,
            max_tokens=settings.GROQ_MAX_TOKENS,
            response_format=self._response_format,
        )
        return self._response_parser(response.choices[0].message.content.strip())
