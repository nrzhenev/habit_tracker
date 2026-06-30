from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.model import User, UserSettings
from app.user.schema import UserSettingsSchema


async def load_user_settings(db: AsyncSession, user: User) -> UserSettingsSchema:
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user.id)
    )
    row = result.scalar_one_or_none()
    if row:
        return UserSettingsSchema.model_validate(row)
    return UserSettingsSchema()
