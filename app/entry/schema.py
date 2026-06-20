import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class EntryCreate(BaseModel):
    content: str


class EntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    content: str
    created_at: datetime.datetime
    entry_type: str | None = None


class ClassificationResponse(BaseModel):
    type: Literal["expense", "activity", "event"]
