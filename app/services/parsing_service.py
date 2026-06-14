import json

from app.config import settings
from app.core.groq_client import groq_client, GroqClient
from app.schemas.parsing import ClassificationResponse
from app.schemas.user_settings import UserSettingsSchema
from app.services.parsing.prompts import build_classification_prompt


class ParsingService:
    def __init__(self, client: GroqClient | None = None):
        self._client = client or groq_client

    async def classify(
        self, user_content: str, user_settings: UserSettingsSchema
    ) -> ClassificationResponse:
        system_prompt = build_classification_prompt(user_settings)
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
        response_string = response.choices[0].message.content.strip()
        data = json.loads(response_string)
        type_ = data["type"]
        if type_ not in ("expense", "activity", "event"):
            raise ValueError(f"Unknown type: {type_}")
        return ClassificationResponse(type=type_)


parsing_service = ParsingService()
