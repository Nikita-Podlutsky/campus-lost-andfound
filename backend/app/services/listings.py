from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    EntityConflictError,
    EntityNotFoundError,
    RelatedEntityNotFoundError,
)
from app.models.category import Category
from app.models.listing import Listing, ListingStatus, ListingType
from app.models.user import User
from app.schemas.listing import ListingCreate, ListingPatch


async def _ensure_references(
    session: AsyncSession,
    author_id: UUID,
    category_id: int,
) -> None:
    if await session.get(User, author_id) is None:
        raise RelatedEntityNotFoundError(f"Пользователь с author_id '{author_id}' не найден")
    if await session.get(Category, category_id) is None:
        raise RelatedEntityNotFoundError(f"Категория с category_id '{category_id}' не найдена")


async def get_listing(session: AsyncSession, listing_id: UUID) -> Listing:
    result = await session.scalars(
        select(Listing)
        .where(Listing.id == listing_id)
        .options(selectinload(Listing.author), selectinload(Listing.category))
    )
    listing = result.one_or_none()
    if listing is None:
        raise EntityNotFoundError(f"Объявление с id '{listing_id}' не найдено")
    return listing


def _apply_filters(
    statement,
    *,
    listing_type: ListingType | None,
    status: ListingStatus | None,
    author_id: UUID | None,
    category_id: int | None,
    query: str | None,
):
    if listing_type is not None:
        statement = statement.where(Listing.type == listing_type)
    if status is not None:
        statement = statement.where(Listing.status == status)
    if author_id is not None:
        statement = statement.where(Listing.author_id == author_id)
    if category_id is not None:
        statement = statement.where(Listing.category_id == category_id)
    if query:
        search_query = query.strip()
        if search_query:
            statement = statement.where(
                or_(
                    Listing.title.icontains(search_query, autoescape=True),
                    Listing.description.icontains(search_query, autoescape=True),
                    Listing.location.icontains(search_query, autoescape=True),
                )
            )
    return statement


async def list_listings(
    session: AsyncSession,
    *,
    listing_type: ListingType | None,
    status: ListingStatus | None,
    author_id: UUID | None,
    category_id: int | None,
    query: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Listing], int]:
    filters = {
        "listing_type": listing_type,
        "status": status,
        "author_id": author_id,
        "category_id": category_id,
        "query": query,
    }
    count_statement = _apply_filters(
        select(func.count(Listing.id)),
        **filters,
    )
    total = await session.scalar(count_statement) or 0

    rows_statement = _apply_filters(select(Listing), **filters)
    rows_statement = (
        rows_statement.options(
            selectinload(Listing.author),
            selectinload(Listing.category),
        )
        .order_by(Listing.created_at.desc(), Listing.id)
        .limit(limit)
        .offset(offset)
    )
    result = await session.scalars(rows_statement)
    return list(result), total


async def create_listing(session: AsyncSession, payload: ListingCreate) -> Listing:
    await _ensure_references(session, payload.author_id, payload.category_id)
    values = payload.model_dump()
    values["photo_url"] = str(payload.photo_url) if payload.photo_url else None
    listing = Listing(**values)
    session.add(listing)

    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise EntityConflictError("Не удалось создать объявление из-за конфликта данных") from error

    await session.refresh(listing)
    return listing


async def update_listing(
    session: AsyncSession,
    listing_id: UUID,
    payload: ListingPatch,
) -> Listing:
    listing = await get_listing(session, listing_id)
    changes = payload.model_dump(exclude_unset=True)

    if "author_id" in changes or "category_id" in changes:
        await _ensure_references(
            session,
            changes.get("author_id", listing.author_id),
            changes.get("category_id", listing.category_id),
        )

    if "photo_url" in changes:
        photo_url = changes["photo_url"]
        changes["photo_url"] = str(photo_url) if photo_url else None

    for field, value in changes.items():
        setattr(listing, field, value)

    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise EntityConflictError(
            "Не удалось обновить объявление из-за конфликта данных"
        ) from error

    await session.refresh(listing)
    await session.refresh(listing, attribute_names=["author", "category"])
    return listing


async def delete_listing(session: AsyncSession, listing_id: UUID) -> None:
    listing = await get_listing(session, listing_id)
    await session.delete(listing)
    await session.commit()
