from app.core.time_utils import current_time
from app.user.schema import UserSettingsSchema


def build_activity_parsing_prompt(user_settings: UserSettingsSchema) -> str:
    lines = [
        "You are an activity parser. Extract structured fields from the user's message.",
        "",
        "## Fields",
        "- started_at: ISO 8601 datetime (use current time if not specified).",
        "- ended_at: ISO 8601 datetime or null.",
        "- category: short label or null (running, swimming, reading, etc.).",
        "",
        "## Rules",
        f"- Current time: {current_time(user_settings)}",
        "- If a duration is mentioned, calculate ended_at from started_at + duration.",
        "- Return ONLY a JSON object, no explanation.",
        "",
        "## Examples",
        'Input: "Ran for 30 minutes"',
        'Output: {"started_at": "2025-01-01T10:00:00+00:00", "ended_at": "2025-01-01T10:30:00+00:00", "category": "running"}',
        "",
        'Input: "Read a book"',
        'Output: {"started_at": "2025-01-01T14:00:00+00:00", "ended_at": null, "category": "reading"}',
    ]
    return "\n".join(lines)
