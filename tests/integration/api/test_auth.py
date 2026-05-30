import pytest

from tests.conftest import TEST_USER_PASSWORD


pytestmark = pytest.mark.integration


async def test_should_return_201_when_valid_register(async_client):
    response = await async_client.post(
        "/register",
        json={
            "email": "new@example.com",
            "password": "securepass",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "id" in data


async def test_should_return_409_when_duplicate_email(async_client, user):
    response = await async_client.post(
        "/register",
        json={
            "email": user.email,
            "password": "securepass",
        },
    )
    assert response.status_code == 409


async def test_should_return_422_when_invalid_email(async_client):
    response = await async_client.post(
        "/register",
        json={
            "email": "not-an-email",
            "password": "securepass",
        },
    )
    assert response.status_code == 422


async def test_should_return_200_when_valid_login(async_client, user):
    response = await async_client.post(
        "/login",
        json={
            "email": user.email,
            "password": TEST_USER_PASSWORD,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_should_return_401_when_wrong_password(async_client, user):
    response = await async_client.post(
        "/login",
        json={
            "email": user.email,
            "password": "wrong",
        },
    )
    assert response.status_code == 401


async def test_should_return_401_when_nonexistent_email(async_client):
    response = await async_client.post(
        "/login",
        json={
            "email": "noone@example.com",
            "password": TEST_USER_PASSWORD,
        },
    )
    assert response.status_code == 401
