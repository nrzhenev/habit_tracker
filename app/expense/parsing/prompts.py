from app.core.time_utils import current_time
from app.user.schema import UserSettingsSchema


def build_expense_parsing_prompt(user_settings: UserSettingsSchema) -> str:
    lines = [
        "You are an expense parser. Extract structured fields from the user's message.",
        "",
        "## Fields",
        "- occurred_at: ISO 8601 datetime (use current time if not specified).",
        "- amount: float or null (total spent).",
        "- currency: 3-letter code.",
        "- category: short label or null (food, transport, entertainment, etc.).",
        "- place: store/venue name or null.",
        "- items: list of strings (what was bought).",
        "",
        "## Rules",
        f"- Current time: {current_time(user_settings)}",
        f"- Default currency: {user_settings.default_currency}.",
        "- If no currency mentioned, use the default.",
        "- Always return items as a list, even for a single item.",
        "- Return ONLY a JSON object, no explanation.",
        "",
        "## Examples",
        'Input: "Spent 15.50 on coffee and a croissant at Starbucks"',
        'Output: {"occurred_at": "2025-01-01T12:00:00+00:00", "amount": 15.50, "currency": "USD", "category": "food", "place": "Starbucks", "items": ["coffee", "croissant"]}',
        "",
        'Input: "Filled up the car for 3000"',
        'Output: {"occurred_at": "2025-01-01T15:00:00+00:00", "amount": 3000.0, "currency": "USD", "category": "transport", "place": null, "items": ["fuel"]}',
    ]
    return "\n".join(lines)
