import pytest

from app.core.security import create_access_token, hash_password
from app.models.user import User

pytestmark = pytest.mark.integration


async def test_should_return_201_when_create_rule(async_client, auth_headers):
    response = await async_client.post(
        "/rules/create",
        json={"question": "How was your mood?", "choices": ["good", "ok", "bad"]},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["question"] == "How was your mood?"
    assert data["choices"] == ["good", "ok", "bad"]
    assert "id" in data


async def test_should_return_401_when_create_rule_without_auth(async_client):
    response = await async_client.post(
        "/rules/create",
        json={"question": "Test", "choices": ["a", "b"]},
    )
    assert response.status_code == 401


async def test_should_return_422_when_create_rule_missing_question(async_client, auth_headers):
    response = await async_client.post(
        "/rules/create",
        json={"choices": ["good", "ok"]},
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_should_return_422_when_create_rule_empty_choices(async_client, auth_headers):
    response = await async_client.post(
        "/rules/create",
        json={"question": "Test", "choices": []},
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_should_return_200_when_list_rules(async_client, auth_headers):
    await async_client.post(
        "/rules/create",
        json={"question": "Mood?", "choices": ["good", "ok"]},
        headers=auth_headers,
    )

    response = await async_client.get("/rules", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["question"] == "Mood?"


async def test_should_return_200_when_list_rules_empty(async_client, auth_headers):
    response = await async_client.get("/rules", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


async def test_should_not_return_other_user_rules(async_client, auth_headers, db_session):
    await async_client.post(
        "/rules/create",
        json={"question": "My rule", "choices": ["a"]},
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
        "/rules",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == 200
    assert response.json() == []
