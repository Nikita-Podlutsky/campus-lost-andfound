from uuid import UUID, uuid4

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.listing import Listing, ListingStatus, ListingType


async def create_references(client: AsyncClient) -> tuple[str, int]:
    user_response = await client.post(
        "/api/v1/users",
        json={"display_name": "Иван", "email": "ivan@example.com"},
    )
    category_response = await client.post(
        "/api/v1/categories",
        json={"name": "Обувь"},
    )
    return user_response.json()["id"], category_response.json()["id"]


def listing_payload(author_id: str, category_id: int) -> dict[str, object]:
    return {
        "type": "found",
        "title": "Чёрный рюкзак",
        "description": "Найден чёрный рюкзак возле главного входа",
        "photo_url": "https://example.com/backpack.jpg",
        "location": "Главный корпус, вход №1",
        "x": 30.5,
        "y": 40.0,
        "author_id": author_id,
        "category_id": category_id,
    }


async def test_listing_crud_persistence_and_filters(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    author_id, category_id = await create_references(client)
    payload = listing_payload(author_id, category_id)

    create_response = await client.post("/api/v1/listings", json=payload)
    assert create_response.status_code == 201
    listing = create_response.json()
    listing_id = UUID(listing["id"])
    assert listing["author"]["email"] == "ivan@example.com"
    assert listing["category"]["name"] == "Обувь"

    stored_listing = await db_session.get(Listing, listing_id)
    assert stored_listing is not None
    assert stored_listing.title == "Чёрный рюкзак"
    assert stored_listing.type == ListingType.FOUND
    assert stored_listing.author_id == UUID(author_id)
    assert stored_listing.category_id == category_id

    list_response = await client.get(
        "/api/v1/listings",
        params={"type": "found", "q": "рюкзак", "limit": 10, "offset": 0},
    )
    assert list_response.status_code == 200
    page = list_response.json()
    assert page["total"] == 1
    assert page["items"][0]["id"] == listing["id"]

    patch_response = await client.patch(
        f"/api/v1/listings/{listing_id}",
        json={"status": "resolved", "title": "Синий рюкзак", "photo_url": None},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["status"] == "resolved"
    assert patch_response.json()["photo_url"] is None

    await db_session.refresh(stored_listing)
    assert stored_listing.status == ListingStatus.RESOLVED
    assert stored_listing.title == "Синий рюкзак"

    delete_response = await client.delete(f"/api/v1/listings/{listing_id}")
    assert delete_response.status_code == 204

    missing_response = await client.get(f"/api/v1/listings/{listing_id}")
    assert missing_response.status_code == 404


async def test_listing_filters_and_pagination(client: AsyncClient) -> None:
    author_id, category_id = await create_references(client)
    first_payload = listing_payload(author_id, category_id)
    first_payload["title"] = "Красные кроссовки"
    first_payload["description"] = "Найдены возле спортивного зала"
    second_payload = listing_payload(author_id, category_id)
    second_payload.update(
        {
            "type": "lost",
            "title": "Синяя сумка",
            "description": "Потеряна в библиотеке",
            "location": "Библиотека",
        }
    )

    assert (await client.post("/api/v1/listings", json=first_payload)).status_code == 201
    assert (await client.post("/api/v1/listings", json=second_payload)).status_code == 201

    lost_response = await client.get("/api/v1/listings", params={"type": "lost"})
    assert lost_response.status_code == 200
    assert lost_response.json()["total"] == 1
    assert lost_response.json()["items"][0]["title"] == "Синяя сумка"

    search_response = await client.get("/api/v1/listings", params={"q": "библиотеке"})
    assert search_response.json()["total"] == 1

    page_response = await client.get(
        "/api/v1/listings",
        params={"limit": 1, "offset": 1},
    )
    assert page_response.status_code == 200
    assert page_response.json()["total"] == 2
    assert len(page_response.json()["items"]) == 1


async def test_related_records_and_constraints(client: AsyncClient) -> None:
    missing_author_response = await client.post(
        "/api/v1/listings",
        json=listing_payload(str(uuid4()), 999),
    )
    assert missing_author_response.status_code == 422
    assert missing_author_response.json()["code"] == "RELATED_ENTITY_NOT_FOUND"

    author_id, category_id = await create_references(client)
    create_response = await client.post(
        "/api/v1/listings",
        json=listing_payload(author_id, category_id),
    )
    assert create_response.status_code == 201

    delete_user_response = await client.delete(f"/api/v1/users/{author_id}")
    assert delete_user_response.status_code == 409
    delete_category_response = await client.delete(f"/api/v1/categories/{category_id}")
    assert delete_category_response.status_code == 409

    invalid_payload = listing_payload(author_id, category_id)
    invalid_payload["x"] = 101
    invalid_response = await client.post("/api/v1/listings", json=invalid_payload)
    assert invalid_response.status_code == 422
    assert invalid_response.json()["errors"][0]["field"] == "body.x"

    result = await client.get("/api/v1/listings")
    assert result.status_code == 200
    assert result.json()["total"] == 1


async def test_persistence_can_be_read_with_sqlalchemy(
    client: AsyncClient,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    author_id, category_id = await create_references(client)
    await client.post("/api/v1/listings", json=listing_payload(author_id, category_id))

    async with session_factory() as session:
        result = await session.scalars(select(Listing))
        stored_listings = list(result)

    assert len(stored_listings) == 1
    assert stored_listings[0].title == "Чёрный рюкзак"
