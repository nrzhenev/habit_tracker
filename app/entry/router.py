from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.entry.deps import get_classifier
from app.user.model import User
from app.activity.model import Activity
from app.entry.model import Entry
from app.activity.schema import ActivityDetail
from app.entry.schema import EntryCreate, EntryRead
from app.entry.entry_classification.client import LLMClassifier
from app.entry.entry_service import process_entry

router = APIRouter(prefix="/entries", tags=["entries"])


@router.post("", response_model=EntryRead, status_code=status.HTTP_201_CREATED)
async def create_entry(
    body: EntryCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    classifier: LLMClassifier = Depends(get_classifier),
):
    entry = await process_entry(body.content, user, db, classifier=classifier)
    return entry


@router.get("", response_model=list[EntryRead])
async def list_entries(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Entry)
        .where(Entry.user_id == user.id)
        .order_by(Entry.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    entry_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    entry = await db.get(Entry, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found"
        )

    if entry.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found"
        )

    await db.delete(entry)
    await db.commit()


@router.get("/{entry_id}/details")
async def get_entry_details(
    entry_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    entry = await db.get(Entry, entry_id)
    if not entry or entry.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found"
        )

    if not entry.entry_type:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # TODO hardcoded to Activity — replace with proper type dispatch
    orm_cls, detail_cls = (Activity, ActivityDetail)
    result = await db.execute(select(orm_cls).where(orm_cls.entry_id == entry.id))
    child = result.scalar_one_or_none()
    if not child:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return detail_cls.model_validate(child)
