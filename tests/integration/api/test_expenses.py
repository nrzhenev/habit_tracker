import pytest

pytestmark = pytest.mark.integration


@pytest.fixture
def expense_payload():
    return {
        "occurred_at": "2025-01-01T00:00:00Z",
        "currency": "USD",
        "items": ["coffee", "lunch"],
    }


async def test_should_return_201_when_create_expense(
    async_client, auth_headers, entry, expense_payload
):
    payload = {"entry_id": entry.id, **expense_payload}
    response = await async_client.post(
        "/expenses",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["entry_id"] == entry.id
    assert data["currency"] == "USD"
    assert data["items"] == ["coffee", "lunch"]
    assert data["amount"] is None
    assert data["category"] is None
    assert data["place"] is None
    assert "id" in data


async def test_should_return_401_when_create_expense_without_auth(
    async_client, entry, expense_payload
):
    payload = {"entry_id": entry.id, **expense_payload}
    response = await async_client.post("/expenses", json=payload)
    assert response.status_code == 401


async def test_should_return_404_when_entry_not_found(
    async_client, auth_headers, expense_payload
):
    payload = {"entry_id": 99999, **expense_payload}
    response = await async_client.post("/expenses", json=payload, headers=auth_headers)
    assert response.status_code == 404


async def test_should_return_404_when_entry_not_owned(
    async_client, entry, expense_payload, other_auth_headers
):
    payload = {"entry_id": entry.id, **expense_payload}
    response = await async_client.post(
        "/expenses",
        json=payload,
        headers=other_auth_headers,
    )
    assert response.status_code == 404


async def test_should_return_409_when_expense_already_exists(
    async_client, auth_headers, expense, expense_payload
):
    payload = {"entry_id": expense.entry_id, **expense_payload}
    response = await async_client.post("/expenses", json=payload, headers=auth_headers)
    assert response.status_code == 409


async def test_should_return_200_when_list_expenses(
    async_client, auth_headers, expense
):
    response = await async_client.get("/expenses", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == expense.id


async def test_should_return_200_when_list_empty(async_client, auth_headers):
    response = await async_client.get("/expenses", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


async def test_should_return_401_when_list_without_auth(async_client):
    response = await async_client.get("/expenses")
    assert response.status_code == 401


async def test_should_not_return_other_user_expenses(
    async_client, expense, other_auth_headers
):
    response = await async_client.get(
        "/expenses",
        headers=other_auth_headers,
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_should_return_200_when_get_expense(async_client, auth_headers, expense):
    response = await async_client.get(f"/expenses/{expense.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == expense.id


async def test_should_return_401_when_get_expense_without_auth(async_client, expense):
    response = await async_client.get(f"/expenses/{expense.id}")
    assert response.status_code == 401


async def test_should_return_404_when_get_expense_not_found(async_client, auth_headers):
    response = await async_client.get("/expenses/99999", headers=auth_headers)
    assert response.status_code == 404


async def test_should_return_404_when_get_expense_not_owned(
    async_client, expense, other_auth_headers
):
    response = await async_client.get(
        f"/expenses/{expense.id}",
        headers=other_auth_headers,
    )
    assert response.status_code == 404


async def test_should_return_404_when_update_expense_not_owned(
    async_client, expense, other_auth_headers
):
    response = await async_client.patch(
        f"/expenses/{expense.id}",
        json={"amount": 42.5},
        headers=other_auth_headers,
    )
    assert response.status_code == 404


async def test_should_return_200_when_update_expense(
    async_client, auth_headers, expense
):
    response = await async_client.patch(
        f"/expenses/{expense.id}",
        json={"amount": 42.5, "category": "food"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 42.5
    assert data["category"] == "food"
    assert data["currency"] == "USD"


async def test_should_return_401_when_update_expense_without_auth(
    async_client, expense
):
    response = await async_client.patch(
        f"/expenses/{expense.id}",
        json={"amount": 42.5},
    )
    assert response.status_code == 401


async def test_should_return_404_when_update_expense_not_found(
    async_client, auth_headers
):
    response = await async_client.patch(
        "/expenses/99999",
        json={"amount": 42.5},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_should_return_204_when_delete_expense(
    async_client, auth_headers, expense
):
    response = await async_client.delete(
        f"/expenses/{expense.id}", headers=auth_headers
    )
    assert response.status_code == 204

    get_response = await async_client.get(
        f"/expenses/{expense.id}", headers=auth_headers
    )
    assert get_response.status_code == 404


async def test_should_return_401_when_delete_expense_without_auth(
    async_client, expense
):
    response = await async_client.delete(f"/expenses/{expense.id}")
    assert response.status_code == 401


async def test_should_return_404_when_delete_expense_not_found(
    async_client, auth_headers
):
    response = await async_client.delete("/expenses/99999", headers=auth_headers)
    assert response.status_code == 404


async def test_should_return_404_when_delete_expense_not_owned(
    async_client, expense, other_auth_headers
):
    response = await async_client.delete(
        f"/expenses/{expense.id}",
        headers=other_auth_headers,
    )
    assert response.status_code == 404
