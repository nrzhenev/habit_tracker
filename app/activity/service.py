from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.activity.model import Activity
from app.activity.parsing.client import LLMActivityParser
from app.activity.schema import ActivityUpdate
from app.core.time_utils import current_datetime
from app.entry.model import Entry
from app.user.model import User
from app.user.service import load_user_settings


def ensure_time_order(started_at, ended_at) -> None:
    if started_at and ended_at and ended_at <= started_at:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="ended_at must be after started_at",
        )


async def create_activity(
    content: str, user: User, db: AsyncSession, *, parser: LLMActivityParser
) -> Activity:
    entry = Entry(user_id=user.id, content=content, entry_type="activity")
    db.add(entry)
    await db.flush()

    settings = await load_user_settings(db, user)
    parsed = await parser.run(content, settings)

    if parsed.started_at is None:
        parsed.started_at = current_datetime(settings)

    ensure_time_order(parsed.started_at, parsed.ended_at)

    activity = Activity(
        entry_id=entry.id,
        started_at=parsed.started_at,
        ended_at=parsed.ended_at,
        category=parsed.category,
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


async def update_activity(
    activity: Activity, data: ActivityUpdate, db: AsyncSession
) -> Activity:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(activity, field, value)
    ensure_time_order(activity.started_at, activity.ended_at)
    await db.commit()
    await db.refresh(activity)
    return activity
