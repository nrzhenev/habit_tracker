from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.activity import Activity
from app.entry.model import Entry
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityUpdate

router = APIRouter(prefix="/activities", tags=["activities"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity_data: ActivityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = await db.get(Entry, activity_data.entry_id)
    if not entry or entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found"
        )

    existing = await db.scalar(
        select(Activity).where(Activity.entry_id == activity_data.entry_id)
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Activity already exists for this entry",
        )

    if (
        activity_data.started_at
        and activity_data.ended_at
        and activity_data.ended_at <= activity_data.started_at
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="ended_at must be after started_at",
        )

    activity = Activity(**activity_data.model_dump())
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


@router.get("")
async def list_activities(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Activity).join(Entry).where(Entry.user_id == current_user.id)
    )
    return result.scalars().all()


@router.get("/{activity_id}")
async def get_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activity = await db.get(Activity, activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found"
        )

    entry = await db.get(Entry, activity.entry_id)
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found"
        )

    return activity


@router.patch("/{activity_id}")
async def update_activity(
    activity_id: int,
    activity_data: ActivityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activity = await db.get(Activity, activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found"
        )

    entry = await db.get(Entry, activity.entry_id)
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found"
        )

    for field, value in activity_data.model_dump(exclude_unset=True).items():
        setattr(activity, field, value)

    if (
        activity.started_at
        and activity.ended_at
        and activity.ended_at <= activity.started_at
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="ended_at must be after started_at",
        )

    await db.commit()
    await db.refresh(activity)
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activity = await db.get(Activity, activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found"
        )

    entry = await db.get(Entry, activity.entry_id)
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found"
        )

    await db.delete(activity)
    await db.commit()
