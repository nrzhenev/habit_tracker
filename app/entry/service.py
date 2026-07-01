from sqlalchemy import select

from app.entry.model import Entry
from app.user.model import User
from app.user.model import UserSettings
from app.user.schema import UserSettingsSchema


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

        classification = await classifier.run(user_content, settings)
        entry.entry_type = classification.type

        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return entry
