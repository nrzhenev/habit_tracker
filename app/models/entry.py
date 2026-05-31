import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message_type_id: Mapped[int] = mapped_column(ForeignKey("message_types.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(String(10000), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="entries")
    message_type: Mapped["MessageType"] = relationship("MessageType", back_populates="entries")
    parsed_answers: Mapped[list["ParsedAnswer"]] = relationship(
        "ParsedAnswer", back_populates="entry", cascade="all, delete-orphan"
    )
