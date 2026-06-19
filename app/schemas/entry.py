import datetime

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
