from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    default_currency: Mapped[str] = mapped_column(
        String(3), default="USD", nullable=False
    )
    timezone: Mapped[str] = mapped_column(
        String(64), default="UTC", nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="settings")
