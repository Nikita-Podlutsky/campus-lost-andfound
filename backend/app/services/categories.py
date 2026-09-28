from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityConflictError, EntityNotFoundError
from app.models.category import Category
from app.models.listing import Listing
from app.schemas.category import CategoryCreate, CategoryPatch


async def get_category(session: AsyncSession, category_id: int) -> Category:
    category = await session.get(Category, category_id)
    if category is None:
        raise EntityNotFoundError(f"Категория с id '{category_id}' не найдена")
    return category


async def list_categories(session: AsyncSession) -> list[Category]:
    result = await session.scalars(select(Category).order_by(Category.name))
    return list(result)


async def create_category(session: AsyncSession, payload: CategoryCreate) -> Category:
    existing_id = await session.scalar(select(Category.id).where(Category.name == payload.name))
    if existing_id is not None:
        raise EntityConflictError("Категория с таким названием уже существует")

    category = Category(
        name=payload.name,
        description=payload.description,
    )
    session.add(category)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise EntityConflictError("Категория с таким названием уже существует") from error
    await session.refresh(category)
    return category


async def update_category(
    session: AsyncSession,
    category_id: int,
    payload: CategoryPatch,
) -> Category:
    category = await get_category(session, category_id)
    changes = payload.model_dump(exclude_unset=True)

    if "name" in changes:
        existing_id = await session.scalar(
            select(Category.id).where(
                Category.name == changes["name"],
                Category.id != category_id,
            )
        )
        if existing_id is not None:
            raise EntityConflictError("Категория с таким названием уже существует")

    for field, value in changes.items():
        setattr(category, field, value)

    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise EntityConflictError(
            "Не удалось обновить категорию: нарушено уникальное поле"
        ) from error
    await session.refresh(category)
    return category


async def delete_category(session: AsyncSession, category_id: int) -> None:
    category = await get_category(session, category_id)
    listings_count = await session.scalar(
        select(func.count(Listing.id)).where(Listing.category_id == category_id)
    )
    if listings_count:
        raise EntityConflictError("Нельзя удалить категорию, у которой есть связанные объявления")

    await session.delete(category)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise EntityConflictError(
            "Нельзя удалить категорию, у которой появились связанные объявления"
        ) from error
