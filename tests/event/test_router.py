import pytest
import datetime

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.event.schema import EventParsed
from app.event.deps import get_event_parser
from app.db.session import get_db


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def async_client(app, db_session):
    async def override_get_db():
        yield db_session

    async def override_get_event_parser():
        from app.event.parsing.client import LLMEventParser

        class _Stub(LLMEventParser):
            async def parse(self, content, settings):
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


async def test_should_return_201_when_create_event(async_client, auth_headers):
    response = await async_client.post(
        "/events",
        json="Had a meeting with the team",
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["action"] == "meeting"
    assert "id" in data
    assert "entry_id" in data
    assert data["occurred_at"] is not None


async def test_should_return_401_when_create_event_without_auth(
    async_client,
):
    response = await async_client.post(
        "/events",
        json="Had a meeting",
    )
    assert response.status_code == 401


async def test_should_return_422_when_create_event_missing_content(
    async_client, auth_headers
):
    response = await async_client.post(
        "/events",
        json=42,
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_should_return_200_when_list_events(async_client, auth_headers, event):
    response = await async_client.get("/events", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == event.id


async def test_should_return_200_when_list_empty(async_client, auth_headers):
    response = await async_client.get("/events", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


async def test_should_return_401_when_list_without_auth(async_client):
    response = await async_client.get("/events")
    assert response.status_code == 401


async def test_should_not_return_other_user_events(
    async_client, event, other_auth_headers
):
    response = await async_client.get(
        "/events",
        headers=other_auth_headers,
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_should_return_200_when_get_event(async_client, auth_headers, event):
    response = await async_client.get(f"/events/{event.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == event.id


async def test_should_return_401_when_get_event_without_auth(async_client, event):
    response = await async_client.get(f"/events/{event.id}")
    assert response.status_code == 401


async def test_should_return_404_when_get_event_not_found(async_client, auth_headers):
    response = await async_client.get("/events/99999", headers=auth_headers)
    assert response.status_code == 404


async def test_should_return_404_when_get_event_not_owned(
    async_client, event, other_auth_headers
):
    response = await async_client.get(
        f"/events/{event.id}",
        headers=other_auth_headers,
    )
    assert response.status_code == 404


async def test_should_return_200_when_update_event(async_client, auth_headers, event):
    response = await async_client.patch(
        f"/events/{event.id}",
        json={"action": "workshop"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "workshop"


async def test_should_return_401_when_update_event_without_auth(async_client, event):
    response = await async_client.patch(
        f"/events/{event.id}",
        json={"action": "workshop"},
    )
    assert response.status_code == 401


async def test_should_return_404_when_update_event_not_found(
    async_client, auth_headers
):
    response = await async_client.patch(
        "/events/99999",
        json={"action": "workshop"},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_should_return_404_when_update_event_not_owned(
    async_client, event, other_auth_headers
):
    response = await async_client.patch(
        f"/events/{event.id}",
        json={"action": "workshop"},
        headers=other_auth_headers,
    )
    assert response.status_code == 404


async def test_should_return_204_when_delete_event(async_client, auth_headers, event):
    response = await async_client.delete(f"/events/{event.id}", headers=auth_headers)
    assert response.status_code == 204

    get_response = await async_client.get(f"/events/{event.id}", headers=auth_headers)
    assert get_response.status_code == 404


async def test_should_return_401_when_delete_event_without_auth(async_client, event):
    response = await async_client.delete(f"/events/{event.id}")
    assert response.status_code == 401


async def test_should_return_404_when_delete_event_not_found(
    async_client, auth_headers
):
    response = await async_client.delete("/events/99999", headers=auth_headers)
    assert response.status_code == 404


async def test_should_return_404_when_delete_event_not_owned(
    async_client, event, other_auth_headers
):
    response = await async_client.delete(
        f"/events/{event.id}",
        headers=other_auth_headers,
    )
    assert response.status_code == 404
