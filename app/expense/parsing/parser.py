import json
from datetime import datetime

from app.expense.schema import ExpenseParsed


def parse_expense_response(llm_response: str) -> ExpenseParsed:
    data = json.loads(llm_response)
    if "currency" not in data:
        raise ValueError("Missing required field: currency")
    if "items" not in data:
        raise ValueError("Missing required field: items")
    if "occurred_at" in data and isinstance(data["occurred_at"], str):
        data["occurred_at"] = datetime.fromisoformat(data["occurred_at"])
    return ExpenseParsed(**data)
