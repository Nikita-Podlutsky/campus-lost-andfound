import json
from uuid import uuid4

import pytest
from httpx import AsyncClient


async def create_references(client: AsyncClient) -> tuple[str, int]:
    user_response = await client.post(
        "/api/v1/users",
        json={"display_name": "Пользователь", "email": "user@example.com"},
    )
    category_response = await client.post(
        "/api/v1/categories",
        json={"name": "Другие вещи"},
    )
    return user_response.json()["id"], category_response.json()["id"]


def valid_payload(author_id: str, category_id: int) -> dict[str, object]:
    return {
        "type": "found",
        "title": "Найденная вещь",
        "description": "Описание найденной вещи",
        "location": "Главный корпус",
        "x": 50,
        "y": 50,
        "author_id": author_id,
        "category_id": category_id,
    }


@pytest.mark.parametrize("coordinate", [-1, 101, float("nan"), float("inf")])
async def test_coordinates_are_finite_and_in_range(
    client: AsyncClient,
    coordinate: float,
) -> None:
    author_id, category_id = await create_references(client)
    payload = valid_payload(author_id, category_id)
    payload["x"] = coordinate

    response = await client.post(
        "/api/v1/listings",
        content=json.dumps(payload, allow_nan=True),
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


async def test_listing_rejects_invalid_enum_and_blank_text(client: AsyncClient) -> None:
    author_id, category_id = await create_references(client)
    invalid_type_payload = valid_payload(author_id, category_id)
    invalid_type_payload["type"] = "unknown"
    invalid_type_response = await client.post(
        "/api/v1/listings",
        json=invalid_type_payload,
    )
    assert invalid_type_response.status_code == 422

    blank_text_payload = valid_payload(author_id, category_id)
    blank_text_payload["title"] = "   "
    blank_text_response = await client.post(
        "/api/v1/listings",
        json=blank_text_payload,
    )
    assert blank_text_response.status_code == 422


async def test_listing_rejects_system_fields_and_temporary_url(
    client: AsyncClient,
) -> None:
    author_id, category_id = await create_references(client)
    payload = valid_payload(author_id, category_id)
    payload.update(
        {
            "id": str(uuid4()),
            "created_at": "2026-01-01T00:00:00Z",
            "photo_url": "blob:http://localhost/image-id",
        }
    )

    response = await client.post("/api/v1/listings", json=payload)

    assert response.status_code == 422
    assert len(response.json()["errors"]) == 3


async def test_database_length_limits_are_validated(client: AsyncClient) -> None:
    author_id, category_id = await create_references(client)
    payload = valid_payload(author_id, category_id)
    payload["photo_url"] = f"https://example.com/{'a' * 2100}"
    response = await client.post("/api/v1/listings", json=payload)
    assert response.status_code == 422

    response = await client.post(
        "/api/v1/users",
        json={"display_name": "Пользователь", "email": f"{'a' * 310}@example.com"},
    )
    assert response.status_code == 422


async def test_listing_patch_rejects_null_status(client: AsyncClient) -> None:
    author_id, category_id = await create_references(client)
    create_response = await client.post(
        "/api/v1/listings",
        json=valid_payload(author_id, category_id),
    )
    listing_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/listings/{listing_id}",
        json={"status": None},
    )

    assert response.status_code == 422
    assert "не может быть null" in response.json()["errors"][0]["message"]
