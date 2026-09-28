from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityConflictError, EntityNotFoundError
from app.models.listing import Listing
from app.models.user import User
from app.schemas.user import UserCreate, UserPatch


async def get_user(session: AsyncSession, user_id: UUID) -> User:
    user = await session.get(User, user_id)
    if user is None:
        raise EntityNotFoundError(f"Пользователь с id '{user_id}' не найден")
    return user


async def list_users(session: AsyncSession) -> list[User]:
    result = await session.scalars(select(User).order_by(User.created_at, User.id))
    return list(result)


async def create_user(session: AsyncSession, payload: UserCreate) -> User:
    email = str(payload.email)
    existing_id = await session.scalar(select(User.id).where(User.email == email))
    if existing_id is not None:
        raise EntityConflictError("Пользователь с таким email уже существует")

    user = User(
        display_name=payload.display_name,
        email=email,
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise EntityConflictError("Пользователь с таким email уже существует") from error
    await session.refresh(user)
    return user


async def update_user(
    session: AsyncSession,
    user_id: UUID,
    payload: UserPatch,
) -> User:
    user = await get_user(session, user_id)
    changes = payload.model_dump(exclude_unset=True)

    if "email" in changes:
        email = str(changes["email"])
        existing_id = await session.scalar(
            select(User.id).where(User.email == email, User.id != user_id)
        )
        if existing_id is not None:
            raise EntityConflictError("Пользователь с таким email уже существует")
        changes["email"] = email

    for field, value in changes.items():
        setattr(user, field, value)

    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise EntityConflictError(
            "Не удалось обновить пользователя: нарушено уникальное поле"
        ) from error
    await session.refresh(user)
    return user


async def delete_user(session: AsyncSession, user_id: UUID) -> None:
    user = await get_user(session, user_id)
    listings_count = await session.scalar(
        select(func.count(Listing.id)).where(Listing.author_id == user_id)
    )
    if listings_count:
        raise EntityConflictError(
            "Нельзя удалить пользователя, у которого есть связанные объявления"
        )

    await session.delete(user)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise EntityConflictError(
            "Нельзя удалить пользователя, у которого появились связанные объявления"
        ) from error
