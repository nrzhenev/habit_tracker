import pytest
import pytest_asyncio
from sqlalchemy import select

from app.entry.model import Entry
from app.user.model import UserSettings
from app.entry.schema import ClassificationResponse
from app.entry.entry_classification.client import LLMClassifier
from app.entry.entry_service import process_entry

pytestmark = pytest.mark.integration


class StubClassifier(LLMClassifier):
    def __init__(self, *, return_classification=None, raise_error=None):
        self._return_classification = return_classification
        self._raise_error = raise_error

    async def classify(self, user_content, user_settings):
        if self._raise_error:
            raise self._raise_error
        return self._return_classification


@pytest_asyncio.fixture
async def user_with_settings(db_session, user):
    settings = UserSettings(
        user_id=user.id, default_currency="RUB", timezone="Europe/Moscow"
    )
    db_session.add(settings)
    await db_session.commit()
    await db_session.refresh(user)
    return user


class TestProcessEntry:
    async def test_should_create_entry_with_expense_type(
        self, db_session, user_with_settings
    ):
        entry = await process_entry(
            "Spent 100 on food",
            user_with_settings,
            db_session,
            classifier=StubClassifier(
                return_classification=ClassificationResponse(type="expense"),
            ),
        )

        assert entry.content == "Spent 100 on food"
        assert entry.user_id == user_with_settings.id
        assert entry.entry_type == "expense"

    async def test_should_create_entry_with_activity_type(
        self, db_session, user_with_settings
    ):
        entry = await process_entry(
            "Ran for 30 minutes",
            user_with_settings,
            db_session,
            classifier=StubClassifier(
                return_classification=ClassificationResponse(type="activity"),
            ),
        )

        assert entry.user_id == user_with_settings.id
        assert entry.content == "Ran for 30 minutes"
        assert entry.entry_type == "activity"

    async def test_should_create_entry_with_event_type(
        self, db_session, user_with_settings
    ):
        entry = await process_entry(
            "Woke up",
            user_with_settings,
            db_session,
            classifier=StubClassifier(
                return_classification=ClassificationResponse(type="event"),
            ),
        )

        assert entry.content == "Woke up"
        assert entry.entry_type == "event"

    async def test_should_use_default_settings_when_user_has_none(
        self, db_session, user
    ):
        entry = await process_entry(
            "Ran for 30 minutes",
            user,
            db_session,
            classifier=StubClassifier(
                return_classification=ClassificationResponse(type="activity"),
            ),
        )

        assert entry.content == "Ran for 30 minutes"
        assert entry.user_id == user.id
        assert entry.entry_type == "activity"

    async def test_should_rollback_on_unexpected_error(
        self, db_session, user_with_settings
    ):
        with pytest.raises(RuntimeError, match="broken"):
            await process_entry(
                "test",
                user_with_settings,
                db_session,
                classifier=StubClassifier(raise_error=RuntimeError("broken")),
            )

        result = await db_session.scalar(select(Entry))
        assert result is None
