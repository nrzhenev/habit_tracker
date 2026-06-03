import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(String(10000), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="entries")
    expense: Mapped[Optional["Expense"]] = relationship(
        "Expense", back_populates="entry", uselist=False
    )
