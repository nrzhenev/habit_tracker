import pytest

from app.core.security import create_access_token, hash_password
from app.models.user import User

pytestmark = pytest.mark.integration


async def test_should_return_201_when_create_answer(
    async_client, auth_headers, entry, parsing_rule
):
    response = await async_client.post(
        f"/entries/{entry.id}/answers",
        json={"parsing_rule_id": parsing_rule.id, "answer": "good"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["answer"] == "good"
    assert data["parsing_rule_id"] == parsing_rule.id
    assert data["entry_id"] == entry.id


async def test_should_return_401_when_create_answer_without_auth(
    async_client, entry, parsing_rule
):
    response = await async_client.post(
        f"/entries/{entry.id}/answers",
        json={"parsing_rule_id": parsing_rule.id, "answer": "good"},
    )
    assert response.status_code == 401


async def test_should_return_404_when_create_answer_for_nonexistent_entry(
    async_client, auth_headers, parsing_rule
):
    response = await async_client.post(
        "/entries/99999/answers",
        json={"parsing_rule_id": parsing_rule.id, "answer": "good"},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_should_return_409_when_create_duplicate_answer(
    async_client, auth_headers, entry, parsing_rule
):
    await async_client.post(
        f"/entries/{entry.id}/answers",
        json={"parsing_rule_id": parsing_rule.id, "answer": "good"},
        headers=auth_headers,
    )

    response = await async_client.post(
        f"/entries/{entry.id}/answers",
        json={"parsing_rule_id": parsing_rule.id, "answer": "ok"},
        headers=auth_headers,
    )
    assert response.status_code == 409


async def test_should_return_422_when_create_answer_missing_fields(
    async_client, auth_headers, entry
):
    response = await async_client.post(
        f"/entries/{entry.id}/answers",
        json={"answer": "good"},
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_should_return_200_when_list_answers(
    async_client, auth_headers, entry, parsing_rule
):
    await async_client.post(
        f"/entries/{entry.id}/answers",
        json={"parsing_rule_id": parsing_rule.id, "answer": "good"},
        headers=auth_headers,
    )

    response = await async_client.get(
        f"/entries/{entry.id}/answers",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["answer"] == "good"


async def test_should_return_200_when_list_empty(async_client, auth_headers, entry):
    response = await async_client.get(
        f"/entries/{entry.id}/answers",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


async def test_should_return_401_when_list_answers_without_auth(async_client, entry):
    response = await async_client.get(f"/entries/{entry.id}/answers")
    assert response.status_code == 401


async def test_should_not_return_other_user_answers(
    async_client, entry, parsing_rule, db_session, auth_headers
):
    await async_client.post(
        f"/entries/{entry.id}/answers",
        json={"parsing_rule_id": parsing_rule.id, "answer": "good"},
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
        f"/entries/{entry.id}/answers",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 404


async def test_should_return_200_when_update_answer(
    async_client, auth_headers, entry, parsing_rule
):
    answer_resp = await async_client.post(
        f"/entries/{entry.id}/answers",
        json={"parsing_rule_id": parsing_rule.id, "answer": "good"},
        headers=auth_headers,
    )
    answer_id = answer_resp.json()["id"]

    response = await async_client.put(
        f"/entries/{entry.id}/answers/{answer_id}",
        json={"parsing_rule_id": parsing_rule.id, "answer": "bad"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "bad"


async def test_should_return_401_when_update_answer_without_auth(
    async_client, auth_headers, entry, parsing_rule
):
    answer_resp = await async_client.post(
        f"/entries/{entry.id}/answers",
        json={"parsing_rule_id": parsing_rule.id, "answer": "good"},
        headers=auth_headers,
    )
    answer_id = answer_resp.json()["id"]

    response = await async_client.put(
        f"/entries/{entry.id}/answers/{answer_id}",
        json={"parsing_rule_id": parsing_rule.id, "answer": "bad"},
    )
    assert response.status_code == 401


async def test_should_return_404_when_update_nonexistent_answer(
    async_client, auth_headers, entry, parsing_rule
):
    response = await async_client.put(
        f"/entries/{entry.id}/answers/99999",
        json={"parsing_rule_id": parsing_rule.id, "answer": "bad"},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_should_return_204_when_delete_answer(
    async_client, auth_headers, entry, parsing_rule
):
    answer_resp = await async_client.post(
        f"/entries/{entry.id}/answers",
        json={"parsing_rule_id": parsing_rule.id, "answer": "good"},
        headers=auth_headers,
    )
    answer_id = answer_resp.json()["id"]

    response = await async_client.delete(
        f"/entries/{entry.id}/answers/{answer_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204


async def test_should_return_401_when_delete_answer_without_auth(
    async_client, auth_headers, entry, parsing_rule
):
    answer_resp = await async_client.post(
        f"/entries/{entry.id}/answers",
        json={"parsing_rule_id": parsing_rule.id, "answer": "good"},
        headers=auth_headers,
    )
    answer_id = answer_resp.json()["id"]

    response = await async_client.delete(f"/entries/{entry.id}/answers/{answer_id}")
    assert response.status_code == 401


async def test_should_return_404_when_delete_nonexistent_answer(
    async_client, auth_headers, entry
):
    response = await async_client.delete(
        f"/entries/{entry.id}/answers/99999",
        headers=auth_headers,
    )
    assert response.status_code == 404
