from typing import Literal

from pydantic import BaseModel


class ClassificationResponse(BaseModel):
    type: Literal["expense", "activity", "event"]
