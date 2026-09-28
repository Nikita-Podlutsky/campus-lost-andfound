from httpx import AsyncClient


async def test_user_crud(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/v1/users",
        json={"display_name": "Анна Петрова", "email": "ANNA@example.com"},
    )
    assert create_response.status_code == 201
    user = create_response.json()
    assert user["email"] == "anna@example.com"
    assert user["id"]
    assert user["created_at"]

    duplicate_response = await client.post(
        "/api/v1/users",
        json={"display_name": "Другая Анна", "email": "anna@example.com"},
    )
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["code"] == "CONFLICT"

    list_response = await client.get("/api/v1/users")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    patch_response = await client.patch(
        f"/api/v1/users/{user['id']}",
        json={"display_name": "Анна Смирнова"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["display_name"] == "Анна Смирнова"

    delete_response = await client.delete(f"/api/v1/users/{user['id']}")
    assert delete_response.status_code == 204

    missing_response = await client.get(f"/api/v1/users/{user['id']}")
    assert missing_response.status_code == 404
    assert missing_response.json()["code"] == "NOT_FOUND"


async def test_category_crud_and_validation(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/v1/categories",
        json={"name": "Сумки", "description": "Рюкзаки и сумки"},
    )
    assert create_response.status_code == 201
    category = create_response.json()

    list_response = await client.get("/api/v1/categories")
    assert list_response.status_code == 200
    assert list_response.json() == [category]

    patch_response = await client.patch(
        f"/api/v1/categories/{category['id']}",
        json={"description": "Школьные и городские сумки"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["description"] == "Школьные и городские сумки"

    invalid_response = await client.patch(
        f"/api/v1/categories/{category['id']}",
        json={},
    )
    assert invalid_response.status_code == 422
    assert invalid_response.json()["code"] == "VALIDATION_ERROR"

    delete_response = await client.delete(f"/api/v1/categories/{category['id']}")
    assert delete_response.status_code == 204


async def test_email_and_null_validation(client: AsyncClient) -> None:
    invalid_email = await client.post(
        "/api/v1/users",
        json={"display_name": "Пользователь", "email": "not-an-email"},
    )
    assert invalid_email.status_code == 422
    assert invalid_email.json()["errors"]

    create_response = await client.post(
        "/api/v1/users",
        json={"display_name": "Пользователь", "email": "user@example.com"},
    )
    user_id = create_response.json()["id"]

    null_response = await client.patch(
        f"/api/v1/users/{user_id}",
        json={"email": None},
    )
    assert null_response.status_code == 422
    assert "не может быть null" in null_response.json()["errors"][0]["message"]
