import datetime

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.activity.deps import get_activity_parser
from app.activity.model import Activity
from app.activity.schema import ActivityParsed
from app.db.session import get_db


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
async def async_client(app, db_session):
    async def override_get_db():
        yield db_session

    async def override_get_activity_parser():
        from app.activity.parsing.client import LLMActivityParser

        class _Stub(LLMActivityParser):
            async def run(self, content, settings):
                return ActivityParsed(
                    started_at=datetime.datetime(
                        2025, 1, 1, 10, tzinfo=datetime.timezone.utc
                    ),
                    ended_at=datetime.datetime(
                        2025, 1, 1, 10, 30, tzinfo=datetime.timezone.utc
                    ),
                    category="running",
                )

        yield _Stub()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_activity_parser] = override_get_activity_parser

    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()
