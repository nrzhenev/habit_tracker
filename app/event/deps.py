from app.event.parsing.client import LLMEventParser


def get_event_parser() -> LLMEventParser:
    return LLMEventParser()
