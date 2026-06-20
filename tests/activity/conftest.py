import pytest_asyncio

from app.activity.model import Activity


@pytest_asyncio.fixture
async def activity(db_session, entry):
    activity = Activity(
        entry_id=entry.id,
    )
    db_session.add(activity)
    await db_session.commit()
    await db_session.refresh(activity)
    return activity
