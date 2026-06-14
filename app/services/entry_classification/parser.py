import json

from app.schemas.parsing import ClassificationResponse

ALLOWED_TYPES = frozenset({"expense", "activity", "event"})


def parse_llm_response(llm_response: str) -> ClassificationResponse:
    data = json.loads(llm_response)
    type_ = data["type"]
    if type_ not in ALLOWED_TYPES:
        raise ValueError(f"Unknown type: {type_}")
    return ClassificationResponse(type=type_)
