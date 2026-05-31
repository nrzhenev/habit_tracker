import pytest
import pytest_asyncio

from app.core.security import create_access_token
from app.models.entry import Entry
from app.models.message_type import MessageType
from app.models.parsing_rule import ParsingRule


@pytest_asyncio.fixture
async def message_type(db_session, user):
    mt = MessageType(name="Daily Check-in", user_id=user.id)
    db_session.add(mt)
    await db_session.commit()
    await db_session.refresh(mt)
    return mt


@pytest_asyncio.fixture
async def parsing_rule(db_session, message_type):
    rule = ParsingRule(
        message_type_id=message_type.id,
        order=1,
        question="How was your mood?",
        choices=["good", "ok", "bad"],
    )
    db_session.add(rule)
    await db_session.commit()
    await db_session.refresh(rule)
    return rule


@pytest_asyncio.fixture
async def entry(db_session, user, message_type):
    entry = Entry(
        user_id=user.id,
        message_type_id=message_type.id,
        content="Test entry content",
    )
    db_session.add(entry)
    await db_session.commit()
    await db_session.refresh(entry)
    return entry


@pytest.fixture
def auth_headers(user):
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}
