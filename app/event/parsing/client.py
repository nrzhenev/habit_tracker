from app.core.llm_client import LLMClient
from app.core.structured_llm_task import StructuredLLMTask
from app.event.parsing.parser import parse_event_response
from app.event.parsing.prompts import build_event_parsing_prompt
from app.event.schema import EventParsed


class LLMEventParser(StructuredLLMTask[EventParsed]):
    def __init__(self, client: LLMClient | None = None):
        super().__init__(build_event_parsing_prompt, parse_event_response, client)


event_parser = LLMEventParser()
