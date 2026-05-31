import pytest_asyncio

from app.models.message_type import MessageType


@pytest_asyncio.fixture
async def message_type(db_session, user):
    mt = MessageType(name="Daily Check-in", user_id=user.id)
    db_session.add(mt)
    await db_session.commit()
    await db_session.refresh(mt)
    return mt
