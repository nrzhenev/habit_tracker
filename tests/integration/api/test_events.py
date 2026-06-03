import pytest

pytestmark = pytest.mark.integration


@pytest.fixture
def event_payload():
    return {
        "action": "meeting",
    }


async def test_should_return_201_when_create_event(
    async_client, auth_headers, entry, event_payload
):
    payload = {"entry_id": entry.id, **event_payload}
    response = await async_client.post(
        "/events",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["entry_id"] == entry.id
    assert data["action"] == "meeting"
    assert "id" in data
    assert data["occurred_at"] is not None


async def test_should_return_401_when_create_event_without_auth(
    async_client, entry, event_payload
):
    payload = {"entry_id": entry.id, **event_payload}
    response = await async_client.post("/events", json=payload)
    assert response.status_code == 401


async def test_should_return_404_when_entry_not_found(
    async_client, auth_headers, event_payload
):
    payload = {"entry_id": 99999, **event_payload}
    response = await async_client.post("/events", json=payload, headers=auth_headers)
    assert response.status_code == 404


async def test_should_return_404_when_entry_not_owned(
    async_client, entry, event_payload, other_auth_headers
):
    payload = {"entry_id": entry.id, **event_payload}
    response = await async_client.post(
        "/events",
        json=payload,
        headers=other_auth_headers,
    )
    assert response.status_code == 404


async def test_should_return_409_when_event_already_exists(
    async_client, auth_headers, event, event_payload
):
    payload = {"entry_id": event.entry_id, **event_payload}
    response = await async_client.post("/events", json=payload, headers=auth_headers)
    assert response.status_code == 409


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
