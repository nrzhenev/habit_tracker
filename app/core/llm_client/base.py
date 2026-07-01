from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel


class LLMError(Exception):
    pass


class LLMApiError(LLMError):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"LLM API error {status_code}: {message}")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str


class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    model: str
    choices: list[ChatCompletionChoice]
    usage: ChatCompletionUsage


@runtime_checkable
class LLMClient(Protocol):
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        response_format: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> ChatCompletionResponse: ...

    async def close(self) -> None: ...
