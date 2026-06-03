from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.entry import Entry
from app.models.user import User
from app.schemas.entry import EntryCreate, EntryRead

router = APIRouter(prefix="/entries", tags=["entries"])


@router.post("", response_model=EntryRead, status_code=status.HTTP_201_CREATED)
async def create_entry(
    body: EntryCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    entry = Entry(
        user_id=user.id,
        content=body.content,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.get("", response_model=list[EntryRead])
async def list_entries(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Entry).where(Entry.user_id == user.id).order_by(Entry.created_at.desc())
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")

    if entry.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")

    await db.delete(entry)
    await db.commit()
