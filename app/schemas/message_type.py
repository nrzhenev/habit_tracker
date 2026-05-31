import datetime

from pydantic import BaseModel, ConfigDict


class MessageTypeCreate(BaseModel):
    name: str


class MessageTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    is_active: bool
    created_at: datetime.datetime
