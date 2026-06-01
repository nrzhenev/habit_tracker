import datetime

from pydantic import BaseModel, ConfigDict, Field


class ParsingRuleCreate(BaseModel):
    question: str
    choices: list[str] = Field(min_length=1)


class ParsingRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    order: int
    question: str
    choices: list[str]
    is_active: bool
    created_at: datetime.datetime
