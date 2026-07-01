import datetime

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.session import get_db
from app.event.deps import get_event_parser
from app.event.model import Event
from app.event.schema import EventParsed


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


@pytest_asyncio.fixture
async def async_client(app, db_session):
    async def override_get_db():
        yield db_session

    async def override_get_event_parser():
        from app.event.parsing.client import LLMEventParser

        class _Stub(LLMEventParser):
            async def run(self, content, settings):
                return EventParsed(
                    action="meeting",
                    occurred_at=datetime.datetime(
                        2025, 1, 1, tzinfo=datetime.timezone.utc
                    ),
                )

        yield _Stub()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_event_parser] = override_get_event_parser

    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()
