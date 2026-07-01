from app.activity.parsing.parser import parse_activity_response
from app.activity.parsing.prompts import build_activity_parsing_prompt
from app.activity.schema import ActivityParsed
from app.core.llm_client import LLMClient
from app.core.structured_llm_task import StructuredLLMTask


class LLMActivityParser(StructuredLLMTask[ActivityParsed]):
    def __init__(self, client: LLMClient | None = None):
        super().__init__(build_activity_parsing_prompt, parse_activity_response, client)


activity_parser = LLMActivityParser()
