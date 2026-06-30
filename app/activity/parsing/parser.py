import json
from datetime import datetime

from app.activity.schema import ActivityParsed


def parse_activity_response(llm_response: str) -> ActivityParsed:
    data = json.loads(llm_response)
    for field in ("started_at", "ended_at"):
        if field in data and isinstance(data[field], str):
            data[field] = datetime.fromisoformat(data[field])
    return ActivityParsed(**data)
