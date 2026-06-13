import json
from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import settings
from app.core.groq_client import groq_client, GroqClient
from app.schemas.parsing import ClassificationResponse
from app.schemas.user_settings import UserSettingsSchema


class ParsingService:
    def __init__(self, client: GroqClient | None = None):
        self._client = client or groq_client

    async def classify(
        self, user_content: str, user_settings: UserSettingsSchema
    ) -> ClassificationResponse:
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
        response_string = response.choices[0].message.content.strip()
        data = json.loads(response_string)
        type_ = data["type"]
        if type_ not in ("expense", "activity", "event"):
            raise ValueError(f"Unknown type: {type_}")
        return ClassificationResponse(type=type_)

    def _current_time(self, user_settings: UserSettingsSchema) -> str:
        tz = ZoneInfo(user_settings.timezone)
        return datetime.now(tz).isoformat()

    def _build_system_prompt(self, user_settings: UserSettingsSchema) -> str:
        lines = [
            "You are a personal log classifier. Classify the user message into one of three types.",
            "",
            "## Types",
            "- expense: user spent or bought something.",
            "- activity: user did something that explicitly lasted a period of time (duration is mentioned).",
            "- event: anything else.",
            "",
            "## Rules",
            f"- Current time: {self._current_time(user_settings)}",
            f"- Default currency: {user_settings.default_currency}.",
            '- Return ONLY: {"type": "<expense|activity|event>"}',
            "- No other fields, no explanation.",
            "",
            "## Examples",
            'Input: "Spent 1500"',
            'Output: {"type": "expense"}',
            "",
            'Input: "Ran for 30 minutes"',
            'Output: {"type": "activity"}',
            "",
            'Input: "Woke up 15 minutes ago"',
            'Output: {"type": "event"}',
        ]
        return "\n".join(lines)


parsing_service = ParsingService()
