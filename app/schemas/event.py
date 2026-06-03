import datetime

from pydantic import BaseModel, ConfigDict


class EventCreate(BaseModel):
    entry_id: int
    action: str
    occurred_at: datetime.datetime | None = None


class EventUpdate(BaseModel):
    action: str | None = None
    occurred_at: datetime.datetime | None = None


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entry_id: int
    occurred_at: datetime.datetime
    action: str
