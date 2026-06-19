import pytest_asyncio

from app.event.model import Event


@pytest_asyncio.fixture
async def event(db_session, entry):
    event = Event(
        entry_id=entry.id,
        action="meeting",
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)
    return event
