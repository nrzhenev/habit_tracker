import pytest

from app.core.security import create_access_token, hash_password
from app.models.user import User

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_should_return_201_when_create_entry(async_client, auth_headers, user):
    response = await async_client.post(
        "/entries",
        json={"content": "Today was a good day"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Today was a good day"
    assert data["user_id"] == user.id
    assert "id" in data


@pytest.mark.asyncio
async def test_should_return_401_when_create_entry_without_auth(async_client):
    response = await async_client.post(
        "/entries",
        json={"content": "test"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_should_return_422_when_create_entry_missing_content(async_client, auth_headers):
    response = await async_client.post(
        "/entries",
        json={},
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_should_return_200_when_list_entries(async_client, auth_headers):
    await async_client.post(
        "/entries",
        json={"content": "First entry"},
        headers=auth_headers,
    )

    response = await async_client.get(
        "/entries",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["content"] == "First entry"


@pytest.mark.asyncio
async def test_should_return_200_when_list_empty(async_client, auth_headers):
    response = await async_client.get(
        "/entries",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_should_return_401_when_list_without_auth(async_client):
    response = await async_client.get("/entries")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_should_not_return_other_user_entries(async_client, auth_headers, user, db_session):
    await async_client.post(
        "/entries",
        json={"content": "My entry"},
        headers=auth_headers,
    )

    other_user = User(
        email="other@example.com",
        hashed_password=hash_password("secret"),
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    other_token = create_access_token({"sub": str(other_user.id)})

    response = await async_client.get(
        "/entries",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == 200
    assert response.json() == []
