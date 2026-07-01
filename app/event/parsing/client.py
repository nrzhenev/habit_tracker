from app.config import settings
from app.core.llm_client import LLMClient, groq_client
from app.user.schema import UserSettingsSchema
from app.event.parsing.parser import parse_event_response
from app.event.parsing.prompts import build_event_parsing_prompt
from app.event.schema import EventParsed


class LLMEventParser:
    def __init__(self, client: LLMClient | None = None):
        self._client = client or groq_client

    async def parse(
        self, user_content: str, user_settings: UserSettingsSchema
    ) -> EventParsed:
        system_prompt = build_event_parsing_prompt(user_settings)
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
        return parse_event_response(response.choices[0].message.content.strip())


event_parser = LLMEventParser()
