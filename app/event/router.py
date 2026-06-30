from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.time_utils import current_datetime
from app.db.session import get_db
from app.entry.model import Entry
from app.event.deps import get_event_parser
from app.event.model import Event
from app.event.parsing.client import LLMEventParser
from app.event.schema import EventRead, EventUpdate
from app.user.model import User, UserSettings
from app.user.schema import UserSettingsSchema

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_event(
    content: str = Body(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    parser: LLMEventParser = Depends(get_event_parser),
):
    entry = Entry(user_id=user.id, content=content, entry_type="event")
    db.add(entry)
    await db.flush()

    try:
        user_settings = await _load_user_settings(db, user)
        parsed = await parser.parse(content, user_settings)

        if parsed.occurred_at is None:
            parsed.occurred_at = current_datetime(user_settings)

        event = Event(
            entry_id=entry.id,
            action=parsed.action,
            occurred_at=parsed.occurred_at,
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
    except Exception:
        await db.rollback()
        raise

    return event


@router.get("")
async def list_events(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Event).join(Entry).where(Entry.user_id == current_user.id)
    )
    return result.scalars().all()


@router.get("/{event_id}")
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    entry = await db.get(Entry, event.entry_id)
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    return event


@router.patch("/{event_id}")
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    entry = await db.get(Entry, event.entry_id)
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    for field, value in event_data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    await db.commit()
    await db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    entry = await db.get(Entry, event.entry_id)
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    await db.delete(event)
    await db.commit()


async def _load_user_settings(db, user):
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user.id)
    )
    row = result.scalar_one_or_none()
    if row:
        return UserSettingsSchema.model_validate(row)
    return UserSettingsSchema()
