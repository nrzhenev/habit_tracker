import pytest

pytestmark = pytest.mark.integration


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


async def test_should_return_401_when_create_entry_without_auth(async_client):
    response = await async_client.post(
        "/entries",
        json={"content": "test"},
    )
    assert response.status_code == 401


async def test_should_return_422_when_create_entry_missing_content(
    async_client, auth_headers
):
    response = await async_client.post(
        "/entries",
        json={},
        headers=auth_headers,
    )
    assert response.status_code == 422


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


async def test_should_return_200_when_list_empty(async_client, auth_headers):
    response = await async_client.get(
        "/entries",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


async def test_should_return_401_when_list_without_auth(async_client):
    response = await async_client.get("/entries")
    assert response.status_code == 401


async def test_should_not_return_other_user_entries(
    async_client, auth_headers, user, other_auth_headers
):
    await async_client.post(
        "/entries",
        json={"content": "My entry"},
        headers=auth_headers,
    )

    response = await async_client.get(
        "/entries",
        headers=other_auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


async def test_should_return_204_when_delete_entry(
    async_client, auth_headers, entry
):
    response = await async_client.delete(
        f"/entries/{entry.id}", headers=auth_headers
    )
    assert response.status_code == 204

    get_response = await async_client.get(
        "/entries", headers=auth_headers
    )
    assert get_response.status_code == 200
    assert get_response.json() == []


async def test_should_return_401_when_delete_entry_without_auth(
    async_client, entry
):
    response = await async_client.delete(f"/entries/{entry.id}")
    assert response.status_code == 401


async def test_should_return_404_when_delete_entry_not_found(
    async_client, auth_headers
):
    response = await async_client.delete(
        "/entries/99999", headers=auth_headers
    )
    assert response.status_code == 404


async def test_should_return_404_when_delete_entry_not_owned(
    async_client, entry, other_auth_headers
):
    response = await async_client.delete(
        f"/entries/{entry.id}",
        headers=other_auth_headers,
    )
    assert response.status_code == 404
