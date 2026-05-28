import datetime

from sqlalchemy import Date, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Completion(Base):
    __tablename__ = "completions"
    __table_args__ = (
        UniqueConstraint("habit_id", "completed_date", name="uq_habit_completion_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    completed_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    habit: Mapped["Habit"] = relationship("Habit", back_populates="completions")
    user: Mapped["User"] = relationship("User", back_populates="completions")
