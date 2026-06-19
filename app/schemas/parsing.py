import datetime
from typing import Literal

from pydantic import BaseModel


class ClassificationResponse(BaseModel):
    type: Literal["expense", "activity", "event"]


class ActivityParsed(BaseModel):
    started_at: datetime.datetime | None = None
    ended_at: datetime.datetime | None = None
    category: str | None = None
