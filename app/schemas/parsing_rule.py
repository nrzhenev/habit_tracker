import datetime

from pydantic import BaseModel, ConfigDict


class ParsingRuleCreate(BaseModel):
    question: str
    choices: list[str]


class ParsingRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order: int
    question: str
    choices: list[str]
    is_active: bool
    created_at: datetime.datetime
