from app.config import settings
from app.core.groq_client import GroqClient, groq_client
from app.user.schema import UserSettingsSchema
from app.activity.parsing.parser import parse_activity_response
from app.activity.parsing.prompts import build_activity_parsing_prompt
from app.activity.schema import ActivityParsed


class LLMActivityParser:
    def __init__(self, client: GroqClient | None = None):
        self._client = client or groq_client

    async def parse(
        self, user_content: str, user_settings: UserSettingsSchema
    ) -> ActivityParsed:
        system_prompt = build_activity_parsing_prompt(user_settings)
        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]
        response = await self._client.chat_completion(
            messages=messages,
            model=settings.GROQ_MODEL,
            temperature=settings.GROQ_TEMPERATURE,
            max_tokens=settings.GROQ_MAX_TOKENS,
            response_format={"type": "json_object"},
        )
        return parse_activity_response(response.choices[0].message.content.strip())


activity_parser = LLMActivityParser()
