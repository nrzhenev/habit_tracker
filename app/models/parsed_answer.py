import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ParsedAnswer(Base):
    __tablename__ = "parsed_answers"
    __table_args__ = (
        UniqueConstraint("entry_id", "parsing_rule_id", name="uq_entry_parsing_rule"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("entries.id", ondelete="CASCADE"), nullable=False)
    parsing_rule_id: Mapped[int] = mapped_column(ForeignKey("parsing_rules.id", ondelete="CASCADE"), nullable=False)
    answer: Mapped[str] = mapped_column(String(5000), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    entry: Mapped["Entry"] = relationship("Entry", back_populates="parsed_answers")
    parsing_rule: Mapped["ParsingRule"] = relationship("ParsingRule", back_populates="parsed_answers")
