import datetime

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.session import get_db
from app.expense.deps import get_expense_parser
from app.expense.model import Expense
from app.expense.schema import ExpenseParsed


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


@pytest_asyncio.fixture
async def async_client(app, db_session):
    async def override_get_db():
        yield db_session

    async def override_get_expense_parser():
        from app.expense.parsing.client import LLMExpenseParser

        class _Stub(LLMExpenseParser):
            async def run(self, content, settings):
                return ExpenseParsed(
                    occurred_at=datetime.datetime(
                        2025, 1, 1, tzinfo=datetime.timezone.utc
                    ),
                    amount=500.0,
                    currency="RUB",
                    category="food",
                    place="Perekrestok",
                    items=["bread", "milk"],
                )

        yield _Stub()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_expense_parser] = override_get_expense_parser

    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()
