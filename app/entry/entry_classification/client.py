from app.core.llm_client import LLMClient
from app.core.structured_llm_task import StructuredLLMTask
from app.entry.entry_classification.parser import parse_llm_response
from app.entry.entry_classification.prompts import build_classification_prompt
from app.entry.schema import ClassificationResponse


class LLMClassifier(StructuredLLMTask[ClassificationResponse]):
    def __init__(self, client: LLMClient | None = None):
        super().__init__(
            build_classification_prompt,
            parse_llm_response,
            client,
            response_format=None,
        )


parsing_service = LLMClassifier()
