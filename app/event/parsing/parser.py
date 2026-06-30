import json
from datetime import datetime

from app.event.schema import EventParsed


def parse_event_response(llm_response: str) -> EventParsed:
    data = json.loads(llm_response)
    if "action" not in data:
        raise ValueError("Missing required field: action")
    if "occurred_at" in data and isinstance(data["occurred_at"], str):
        data["occurred_at"] = datetime.fromisoformat(data["occurred_at"])
    return EventParsed(**data)
