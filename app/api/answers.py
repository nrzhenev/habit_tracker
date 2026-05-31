from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.entry import Entry
from app.models.parsed_answer import ParsedAnswer
from app.models.parsed_answer_log import ParsedAnswerLog
from app.models.user import User
from app.schemas.parsed_answer import ParsedAnswerCreate, ParsedAnswerRead

router = APIRouter(prefix="/entries/{entry_id}/answers", tags=["answers"])


async def _get_entry_or_404(entry_id: int, user: User, db: AsyncSession) -> Entry:
    result = await db.execute(
        select(Entry).where(Entry.id == entry_id, Entry.user_id == user.id)
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return entry


async def _get_answer_or_404(answer_id: int, entry_id: int, db: AsyncSession) -> ParsedAnswer:
    result = await db.execute(
        select(ParsedAnswer).where(
            ParsedAnswer.id == answer_id,
            ParsedAnswer.entry_id == entry_id,
        )
    )
    answer = result.scalar_one_or_none()
    if answer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return answer


@router.post("", response_model=ParsedAnswerRead, status_code=status.HTTP_201_CREATED)
async def create_answer(
    entry_id: int,
    body: ParsedAnswerCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_entry_or_404(entry_id, user, db)

    existing = await db.execute(
        select(ParsedAnswer).where(
            ParsedAnswer.entry_id == entry_id,
            ParsedAnswer.parsing_rule_id == body.parsing_rule_id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Answer already exists for this rule",
        )

    answer = ParsedAnswer(
        entry_id=entry_id,
        parsing_rule_id=body.parsing_rule_id,
        answer=body.answer,
    )
    db.add(answer)
    await db.commit()
    await db.refresh(answer)

    db.add(
        ParsedAnswerLog(
            entry_id=entry_id,
            parsing_rule_id=body.parsing_rule_id,
            answer=body.answer,
        )
    )
    await db.commit()

    return answer


@router.get("", response_model=list[ParsedAnswerRead])
async def list_answers(
    entry_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_entry_or_404(entry_id, user, db)

    result = await db.execute(
        select(ParsedAnswer).where(ParsedAnswer.entry_id == entry_id)
    )
    return result.scalars().all()


@router.put("/{answer_id}", response_model=ParsedAnswerRead)
async def update_answer(
    entry_id: int,
    answer_id: int,
    body: ParsedAnswerCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_entry_or_404(entry_id, user, db)
    answer = await _get_answer_or_404(answer_id, entry_id, db)

    answer.answer = body.answer
    await db.commit()
    await db.refresh(answer)

    db.add(
        ParsedAnswerLog(
            entry_id=entry_id,
            parsing_rule_id=body.parsing_rule_id,
            answer=body.answer,
        )
    )
    await db.commit()

    return answer


@router.delete("/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(
    entry_id: int,
    answer_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_entry_or_404(entry_id, user, db)
    answer = await _get_answer_or_404(answer_id, entry_id, db)

    await db.delete(answer)
    await db.commit()
