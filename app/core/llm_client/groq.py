from typing import Any

import httpx

from app.config import settings
from app.core.llm_client.base import (
    ChatCompletionResponse,
    LLMApiError,
    LLMClient,
    LLMError,
)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class GroqError(LLMError):
    pass


class GroqApiError(GroqError, LLMApiError):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        LLMError.__init__(self, f"Groq API error {status_code}: {message}")


class GroqClient(LLMClient):
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
    ):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    def _build_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=GROQ_BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(self.timeout),
        )

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = self._build_client()
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        response_format: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> ChatCompletionResponse:
        payload: dict[str, Any] = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format is not None:
            payload["response_format"] = response_format
        payload.update(kwargs)

        client = await self._get_client()
        response = await client.post("/chat/completions", json=payload)

        if response.status_code != 200:
            error_msg = ""
            try:
                error_body = response.json()
                error_msg = error_body.get("error", {}).get("message", response.text)
            except Exception:
                error_msg = response.text
            raise GroqApiError(response.status_code, error_msg)

        return ChatCompletionResponse.model_validate(response.json())


groq_client = GroqClient()
