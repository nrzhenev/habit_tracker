from datetime import datetime
from zoneinfo import ZoneInfo

from app.schemas.user_settings import UserSettingsSchema


def _current_time(user_settings: UserSettingsSchema) -> str:
    tz = ZoneInfo(user_settings.timezone)
    return datetime.now(tz).isoformat()


def build_classification_prompt(user_settings: UserSettingsSchema) -> str:
    lines = [
        "You are a personal log classifier. Classify the user message into one of three types.",
        "",
        "## Types",
        "- expense: user spent or bought something.",
        "- activity: user did something that explicitly lasted a period of time (duration is mentioned).",
        "- event: anything else.",
        "",
        "## Rules",
        f"- Current time: {_current_time(user_settings)}",
        f"- Default currency: {user_settings.default_currency}.",
        '- Return ONLY: {"type": "<expense|activity|event>"}',
        "- No other fields, no explanation.",
        "",
        "## Examples",
        'Input: "Spent 1500"',
        'Output: {"type": "expense"}',
        "",
        'Input: "Ran for 30 minutes"',
        'Output: {"type": "activity"}',
        "",
        'Input: "Woke up 15 minutes ago"',
        'Output: {"type": "event"}',
    ]
    return "\n".join(lines)
