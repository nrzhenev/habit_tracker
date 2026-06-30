from app.core.time_utils import current_time
from app.user.schema import UserSettingsSchema


def build_event_parsing_prompt(user_settings: UserSettingsSchema) -> str:
    lines = [
        "You are an event parser. Extract structured fields from the user's message.",
        "",
        "## Fields",
        "- action: short description of what happened (lowercase, one line).",
        "- occurred_at: ISO 8601 datetime (use current time if not specified).",
        "",
        "## Rules",
        f"- Current time: {current_time(user_settings)}",
        "- Return ONLY a JSON object, no explanation.",
        "",
        "## Examples",
        'Input: "Woke up at 7am"',
        'Output: {"action": "woke up", "occurred_at": "2025-01-01T07:00:00+00:00"}',
        "",
        'Input: "Had a meeting with the team"',
        'Output: {"action": "meeting with team", "occurred_at": "2025-01-01T14:00:00+00:00"}',
    ]
    return "\n".join(lines)
