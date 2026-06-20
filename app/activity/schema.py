import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ActivityCreate(BaseModel):
    entry_id: int
    started_at: datetime.datetime | None = None
    ended_at: datetime.datetime | None = None
    category: str | None = None


class ActivityUpdate(BaseModel):
    started_at: datetime.datetime | None = None
    ended_at: datetime.datetime | None = None
    category: str | None = None


class ActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entry_id: int
    started_at: datetime.datetime | None
    ended_at: datetime.datetime | None
    category: str | None


class ActivityDetail(ActivityRead):
    type: Literal["activity"] = "activity"


class ActivityParsed(BaseModel):
    started_at: datetime.datetime | None = None
    ended_at: datetime.datetime | None = None
    category: str | None = None
