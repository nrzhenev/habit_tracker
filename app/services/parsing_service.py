from app.config import settings
from app.core.groq_client import groq_client, GroqClient


class ParsingService:
    def __init__(self, client: GroqClient | None = None):
        self._client = client or groq_client

    async def classify(self, system_prompt: str, user_content: str) -> str:
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
