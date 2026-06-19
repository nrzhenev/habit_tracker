import pytest_asyncio

from app.entry.model import Entry


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
