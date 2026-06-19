import datetime

import pytest
import pytest_asyncio

from app.core.security import create_access_token, hash_password
from app.models.activity import Activity
from app.event.model import Event
from app.models.user import User


@pytest_asyncio.fixture
async def activity(db_session, entry):
    activity = Activity(
        entry_id=entry.id,
    )
    db_session.add(activity)
    await db_session.commit()
    await db_session.refresh(activity)
    return activity
