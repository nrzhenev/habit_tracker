from fastapi import APIRouter, Body, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.activity.service import create_activity as create_activity_service
from app.activity.service import update_activity as update_activity_service
from app.activity.deps import get_activity_parser, get_owned_activity
from app.activity.model import Activity
from app.activity.parsing.client import LLMActivityParser
from app.activity.schema import ActivityRead, ActivityUpdate
from app.core.deps import get_current_user
from app.db.session import get_db
from app.entry.model import Entry
from app.user.model import User

router = APIRouter(prefix="/activities", tags=["activities"])


@router.post("", response_model=ActivityRead, status_code=status.HTTP_201_CREATED)
async def create_activity(
    content: str = Body(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    parser: LLMActivityParser = Depends(get_activity_parser),
):
    return await create_activity_service(content, user, db, parser=parser)


@router.get("", response_model=list[ActivityRead])
async def list_activities(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Activity).join(Entry).where(Entry.user_id == user.id)
    )
    return result.scalars().all()


@router.get("/{activity_id}", response_model=ActivityRead)
async def get_activity(activity: Activity = Depends(get_owned_activity)):
    return activity


@router.patch("/{activity_id}", response_model=ActivityRead)
async def update_activity(
    activity_data: ActivityUpdate,
    activity: Activity = Depends(get_owned_activity),
    db: AsyncSession = Depends(get_db),
):
    return await update_activity_service(activity, activity_data, db)


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity: Activity = Depends(get_owned_activity),
    db: AsyncSession = Depends(get_db),
):
    await db.delete(activity)
    await db.commit()
