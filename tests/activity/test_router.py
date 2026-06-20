import pytest

pytestmark = pytest.mark.integration


@pytest.fixture
def activity_payload():
    return {
        "started_at": "2025-01-01T00:00:00Z",
        "ended_at": "2025-01-01T01:00:00Z",
        "category": "running",
    }


async def test_should_return_201_when_create_activity(
    async_client, auth_headers, entry, activity_payload
):
    payload = {"entry_id": entry.id, **activity_payload}
    response = await async_client.post(
        "/activities",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["entry_id"] == entry.id
    assert data["category"] == "running"
    assert "id" in data


async def test_should_return_201_when_optional_fields_none(
    async_client, auth_headers, entry
):
    response = await async_client.post(
        "/activities",
        json={"entry_id": entry.id},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["started_at"] is None
    assert data["ended_at"] is None
    assert data["category"] is None


async def test_should_return_401_when_create_activity_without_auth(
    async_client, entry, activity_payload
):
    payload = {"entry_id": entry.id, **activity_payload}
    response = await async_client.post("/activities", json=payload)
    assert response.status_code == 401


async def test_should_return_404_when_entry_not_found(
    async_client, auth_headers, activity_payload
):
    payload = {"entry_id": 99999, **activity_payload}
    response = await async_client.post(
        "/activities", json=payload, headers=auth_headers
    )
    assert response.status_code == 404


async def test_should_return_404_when_entry_not_owned(
    async_client, entry, activity_payload, other_auth_headers
):
    payload = {"entry_id": entry.id, **activity_payload}
    response = await async_client.post(
        "/activities",
        json=payload,
        headers=other_auth_headers,
    )
    assert response.status_code == 404


async def test_should_return_409_when_activity_already_exists(
    async_client, auth_headers, activity, activity_payload
):
    payload = {"entry_id": activity.entry_id, **activity_payload}
    response = await async_client.post(
        "/activities", json=payload, headers=auth_headers
    )
    assert response.status_code == 409


async def test_should_return_422_when_create_with_ended_at_before_started_at(
    async_client, auth_headers, entry
):
    response = await async_client.post(
        "/activities",
        json={
            "entry_id": entry.id,
            "started_at": "2025-01-01T02:00:00Z",
            "ended_at": "2025-01-01T01:00:00Z",
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_should_return_422_when_create_with_ended_at_equal_started_at(
    async_client, auth_headers, entry
):
    response = await async_client.post(
        "/activities",
        json={
            "entry_id": entry.id,
            "started_at": "2025-01-01T01:00:00Z",
            "ended_at": "2025-01-01T01:00:00Z",
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_should_return_200_when_list_activities(
    async_client, auth_headers, activity
):
    response = await async_client.get("/activities", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == activity.id


async def test_should_return_200_when_list_empty(async_client, auth_headers):
    response = await async_client.get("/activities", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


async def test_should_return_401_when_list_without_auth(async_client):
    response = await async_client.get("/activities")
    assert response.status_code == 401


async def test_should_not_return_other_user_activities(
    async_client, activity, other_auth_headers
):
    response = await async_client.get(
        "/activities",
        headers=other_auth_headers,
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_should_return_200_when_get_activity(
    async_client, auth_headers, activity
):
    response = await async_client.get(
        f"/activities/{activity.id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["id"] == activity.id


async def test_should_return_401_when_get_activity_without_auth(async_client, activity):
    response = await async_client.get(f"/activities/{activity.id}")
    assert response.status_code == 401


async def test_should_return_404_when_get_activity_not_found(
    async_client, auth_headers
):
    response = await async_client.get("/activities/99999", headers=auth_headers)
    assert response.status_code == 404


async def test_should_return_404_when_get_activity_not_owned(
    async_client, activity, other_auth_headers
):
    response = await async_client.get(
        f"/activities/{activity.id}",
        headers=other_auth_headers,
    )
    assert response.status_code == 404


async def test_should_return_200_when_update_activity(
    async_client, auth_headers, activity
):
    response = await async_client.patch(
        f"/activities/{activity.id}",
        json={"category": "swimming"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "swimming"


async def test_should_return_422_when_update_ended_at_before_started_at(
    async_client, auth_headers, activity
):
    response = await async_client.patch(
        f"/activities/{activity.id}",
        json={
            "started_at": "2025-01-01T02:00:00Z",
            "ended_at": "2025-01-01T01:00:00Z",
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_should_return_401_when_update_activity_without_auth(
    async_client, activity
):
    response = await async_client.patch(
        f"/activities/{activity.id}",
        json={"category": "swimming"},
    )
    assert response.status_code == 401


async def test_should_return_404_when_update_activity_not_found(
    async_client, auth_headers
):
    response = await async_client.patch(
        "/activities/99999",
        json={"category": "swimming"},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_should_return_404_when_update_activity_not_owned(
    async_client, activity, other_auth_headers
):
    response = await async_client.patch(
        f"/activities/{activity.id}",
        json={"category": "swimming"},
        headers=other_auth_headers,
    )
    assert response.status_code == 404


async def test_should_return_204_when_delete_activity(
    async_client, auth_headers, activity
):
    response = await async_client.delete(
        f"/activities/{activity.id}", headers=auth_headers
    )
    assert response.status_code == 204

    get_response = await async_client.get(
        f"/activities/{activity.id}", headers=auth_headers
    )
    assert get_response.status_code == 404


async def test_should_return_401_when_delete_activity_without_auth(
    async_client, activity
):
    response = await async_client.delete(f"/activities/{activity.id}")
    assert response.status_code == 401


async def test_should_return_404_when_delete_activity_not_found(
    async_client, auth_headers
):
    response = await async_client.delete("/activities/99999", headers=auth_headers)
    assert response.status_code == 404


async def test_should_return_404_when_delete_activity_not_owned(
    async_client, activity, other_auth_headers
):
    response = await async_client.delete(
        f"/activities/{activity.id}",
        headers=other_auth_headers,
    )
    assert response.status_code == 404
