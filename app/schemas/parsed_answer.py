import datetime

from pydantic import BaseModel, ConfigDict


class ParsedAnswerCreate(BaseModel):
    parsing_rule_id: int
    answer: str


class ParsedAnswerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entry_id: int
    parsing_rule_id: int
    answer: str
    created_at: datetime.datetime
    updated_at: datetime.datetime | None
