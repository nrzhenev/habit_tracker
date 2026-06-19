import datetime

import pytest_asyncio

from app.expense.model import Expense


@pytest_asyncio.fixture
async def expense(db_session, entry):
    expense = Expense(
        entry_id=entry.id,
        occurred_at=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
        currency="USD",
        items=["coffee", "lunch"],
    )
    db_session.add(expense)
    await db_session.commit()
    await db_session.refresh(expense)
    return expense
