import uuid

import pytest

from app.core.security import create_access_token


pytestmark = pytest.mark.integration


async def test_should_return_401_when_no_auth_header(async_client):
    response = await async_client.get("/me")

    assert response.status_code == 401


async def test_should_return_401_when_user_not_exists(async_client):
    token = create_access_token({"sub": str(uuid.uuid4())})

    response = await async_client.get(
        "/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401


async def test_should_return_200_with_current_user(async_client, user):
    token = create_access_token({"sub": str(user.id)})

    response = await async_client.get(
        "/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.id
    assert data["email"] == user.email
