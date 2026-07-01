from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.time_utils import current_datetime
from app.db.session import get_db
from app.entry.model import Entry
from app.expense.deps import get_expense_parser
from app.expense.model import Expense
from app.expense.parsing.client import LLMExpenseParser
from app.expense.schema import ExpenseParsed, ExpenseRead, ExpenseUpdate
from app.user.model import User, UserSettings
from app.user.schema import UserSettingsSchema

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
async def create_expense(
    content: str = Body(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    parser: LLMExpenseParser = Depends(get_expense_parser),
):
    entry = Entry(user_id=user.id, content=content, entry_type="expense")
    db.add(entry)
    await db.flush()

    try:
        user_settings = await _load_user_settings(db, user)
        parsed = await parser.run(content, user_settings)

        if parsed.occurred_at is None:
            parsed.occurred_at = current_datetime(user_settings)

        expense = Expense(
            entry_id=entry.id,
            occurred_at=parsed.occurred_at,
            amount=parsed.amount,
            currency=parsed.currency,
            category=parsed.category,
            place=parsed.place,
            items=parsed.items,
        )
        db.add(expense)
        await db.commit()
        await db.refresh(expense)
    except Exception:
        await db.rollback()
        raise

    return expense


@router.get("")
async def list_expenses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Expense).join(Entry).where(Entry.user_id == current_user.id)
    )
    return result.scalars().all()


@router.get("/{expense_id}")
async def get_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = await db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )

    entry = await db.get(Entry, expense.entry_id)
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )

    return expense


@router.patch("/{expense_id}")
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = await db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )

    entry = await db.get(Entry, expense.entry_id)
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )

    for field, value in expense_data.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)

    await db.commit()
    await db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = await db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )

    entry = await db.get(Entry, expense.entry_id)
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )

    await db.delete(expense)
    await db.commit()


async def _load_user_settings(db, user):
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user.id)
    )
    row = result.scalar_one_or_none()
    if row:
        return UserSettingsSchema.model_validate(row)
    return UserSettingsSchema()


@router.post("/parse", response_model=ExpenseParsed)
async def parse_expense(
    content: str = Body(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    parser: LLMExpenseParser = Depends(get_expense_parser),
):
    user_settings = await _load_user_settings(db, user)
    return await parser.run(content, user_settings)
