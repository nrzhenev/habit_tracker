import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ParsedAnswerLog(Base):
    __tablename__ = "parsed_answer_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[int] = mapped_column(nullable=False)
    parsing_rule_id: Mapped[int] = mapped_column(nullable=False)
    answer: Mapped[str] = mapped_column(String(5000), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
