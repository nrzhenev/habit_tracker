import datetime

import pytest
import pytest_asyncio

from app.core.security import create_access_token, hash_password
from app.models.activity import Activity
from app.models.entry import Entry
from app.models.expense import Expense
from app.models.user import User


@pytest_asyncio.fixture
async def entry(db_session, user):
    entry = Entry(
        user_id=user.id,
        content="Test entry content",
    )
    db_session.add(entry)
    await db_session.commit()
    await db_session.refresh(entry)
    return entry


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


@pytest.fixture
def auth_headers(user):
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def activity(db_session, entry):
    activity = Activity(
        entry_id=entry.id,
    )
    db_session.add(activity)
    await db_session.commit()
    await db_session.refresh(activity)
    return activity


@pytest_asyncio.fixture
async def other_auth_headers(db_session):
    other_user = User(
        email="other@example.com",
        hashed_password=hash_password("secret"),
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)
    token = create_access_token({"sub": str(other_user.id)})
    return {"Authorization": f"Bearer {token}"}
