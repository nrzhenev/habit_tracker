from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.activity.model import Activity
from app.activity.parsing.client import LLMActivityParser
from app.core.deps import get_current_user
from app.db.session import get_db
from app.entry.model import Entry
from app.user.model import User


def get_activity_parser() -> LLMActivityParser:
    return LLMActivityParser()


async def get_owned_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Activity:
    result = await db.execute(
        select(Activity)
        .join(Entry)
        .where(Activity.id == activity_id, Entry.user_id == user.id)
    )
    activity = result.scalar_one_or_none()
    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found"
        )
    return activity
