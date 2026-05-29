import datetime

from pydantic import BaseModel, ConfigDict


class CompletionCreate(BaseModel):
    completed_date: datetime.date


class CompletionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    habit_id: int
    completed_date: datetime.date
    created_at: datetime.datetime
