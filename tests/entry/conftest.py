import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.entry.deps import get_classifier
from app.entry.schema import ClassificationResponse


@pytest_asyncio.fixture
async def async_client(app):
    async def override_get_classifier():
        from app.entry.entry_classification.client import LLMClassifier

        class _Stub(LLMClassifier):
            async def run(self, uc, us):
                return ClassificationResponse(type="activity")

        yield _Stub()

    app.dependency_overrides[get_classifier] = override_get_classifier
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()
