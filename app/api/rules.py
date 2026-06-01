from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.parsing_rule import ParsingRule
from app.models.user import User
from app.schemas.parsing_rule import ParsingRuleCreate, ParsingRuleRead

router = APIRouter(prefix="/rules", tags=["rules"])


@router.post("/create", response_model=ParsingRuleRead, status_code=status.HTTP_201_CREATED)
async def create_rule(
    body: ParsingRuleCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rule = ParsingRule(
        user_id=user.id,
        question=body.question,
        choices=body.choices,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.get("", response_model=list[ParsingRuleRead])
async def list_rules(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ParsingRule)
        .where(ParsingRule.user_id == user.id)
        .order_by(ParsingRule.created_at.desc())
    )
    return result.scalars().all()
