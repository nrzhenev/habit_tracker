import asyncpg
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.deps import get_classifier
from app.config import settings
from app.core.security import hash_password, create_access_token
from app.schemas.parsing import ClassificationResponse
from app.db.session import get_db
from app.main import get_app
from app.models import User
from app.db.base import Base
from app.entry.model import Entry

TEST_DB_NAME = f"{settings.POSTGRES_DB}_test"
TEST_USER_PASSWORD = "secret"


def _test_db_url() -> str:
    return (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{TEST_DB_NAME}"
    )


async def _ensure_test_db() -> None:
    sys_conn = await asyncpg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database="postgres",
    )
    try:
        await sys_conn.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
    except asyncpg.exceptions.DuplicateDatabaseError:
        pass
    await sys_conn.close()


@pytest_asyncio.fixture
async def engine():
    await _ensure_test_db()
    engine = create_async_engine(_test_db_url())
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest_asyncio.fixture
async def user(db_session):
    user = User(
        email="test@example.com",
        hashed_password=hash_password(TEST_USER_PASSWORD),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def async_client(db_session):
    async def override_get_db():
        yield db_session

    async def override_get_classifier():
        from app.entry.entry_classification.client import LLMClassifier

        class _Stub(LLMClassifier):
            async def classify(self, uc, us):
                return ClassificationResponse(type="activity")

        yield _Stub()

    app = get_app()
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_classifier] = override_get_classifier

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
def auth_headers(user):
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


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
