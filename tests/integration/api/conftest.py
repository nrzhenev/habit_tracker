import pytest
import pytest_asyncio

from app.core.security import create_access_token
from app.models.entry import Entry


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


@pytest.fixture
def auth_headers(user):
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}
