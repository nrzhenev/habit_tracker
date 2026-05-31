import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func, text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ParsingRule(Base):
    __tablename__ = "parsing_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    message_type_id: Mapped[int] = mapped_column(ForeignKey("message_types.id", ondelete="CASCADE"), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    question: Mapped[str] = mapped_column(String(1000), nullable=False)
    choices: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    message_type: Mapped["MessageType"] = relationship("MessageType", back_populates="parsing_rules")
