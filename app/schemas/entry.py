import datetime

from pydantic import BaseModel, ConfigDict


class EntryCreate(BaseModel):
    content: str
    message_type_id: int


class EntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    message_type_id: int
    content: str
    created_at: datetime.datetime
