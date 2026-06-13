import datetime
from typing import Literal

from pydantic import BaseModel


class ClassificationResponse(BaseModel):
    type: Literal["expense", "activity", "event"]


class ExpenseParsed(BaseModel):
    occurred_at: datetime.datetime
    currency: str
    items: list[str]
    amount: float | None = None
    category: str | None = None
    place: str | None = None


class ActivityParsed(BaseModel):
    started_at: datetime.datetime | None = None
    ended_at: datetime.datetime | None = None
    category: str | None = None


class EventParsed(BaseModel):
    action: str
    occurred_at: datetime.datetime | None = None
