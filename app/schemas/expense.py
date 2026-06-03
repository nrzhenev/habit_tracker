import datetime

from pydantic import BaseModel, ConfigDict


class ExpenseCreate(BaseModel):
    entry_id: int
    occurred_at: datetime.datetime
    currency: str
    items: list[str]
    amount: float | None = None
    category: str | None = None
    place: str | None = None


class ExpenseUpdate(BaseModel):
    occurred_at: datetime.datetime | None = None
    currency: str | None = None
    items: list[str] | None = None
    amount: float | None = None
    category: str | None = None
    place: str | None = None


class ExpenseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entry_id: int
    occurred_at: datetime.datetime
    amount: float | None
    currency: str
    category: str | None
    place: str | None
    items: list[str]
