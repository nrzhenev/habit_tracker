import json

from app.config import settings
from app.core.groq_client import groq_client, GroqClient
from app.schemas.parsing import ActivityParsed, EventParsed, ExpenseParsed
from app.schemas.user_settings import UserSettingsSchema


class ParsingService:
    def __init__(self, client: GroqClient | None = None):
        self._client = client or groq_client

    async def classify(
        self, user_content: str, user_settings: UserSettingsSchema
    ) -> str:
        system_prompt = self._build_system_prompt(user_settings)
        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]
        response = await self._client.chat_completion(
            messages=messages,
            model=settings.GROQ_MODEL,
            temperature=settings.GROQ_TEMPERATURE,
            max_tokens=settings.GROQ_MAX_TOKENS,
        )
        return response.choices[0].message.content.strip()


parsing_service = ParsingService()
