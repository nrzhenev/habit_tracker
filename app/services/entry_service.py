from sqlalchemy import select

from app.models.entry import Entry
from app.models.user import User
from app.models.user_settings import UserSettings
from app.schemas.user_settings import UserSettingsSchema


async def process_entry(user_content: str, user: User, db, *, classifier) -> Entry:
    entry = Entry(user_id=user.id, content=user_content)
    db.add(entry)
    await db.flush()

    try:
        result = await db.execute(
            select(UserSettings).where(UserSettings.user_id == user.id)
        )
        user_settings_row = result.scalar_one_or_none()
        settings = (
            UserSettingsSchema.model_validate(user_settings_row)
            if user_settings_row
            else UserSettingsSchema()
        )

        classification = await classifier.classify(user_content, settings)
        entry.entry_type = classification.type

        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return entry
