from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.user import UserCreate, UserPatch, UserRead
from app.services import users as user_service

router = APIRouter(prefix="/users", tags=["Пользователи"])
SessionDependency = Annotated[AsyncSession, Depends(get_session)]


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, session: SessionDependency) -> UserRead:
    user = await user_service.create_user(session, payload)
    return UserRead.model_validate(user)


@router.get("", response_model=list[UserRead])
async def get_users(session: SessionDependency) -> list[UserRead]:
    users = await user_service.list_users(session)
    return [UserRead.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID, session: SessionDependency) -> UserRead:
    user = await user_service.get_user(session, user_id)
    return UserRead.model_validate(user)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    payload: UserPatch,
    session: SessionDependency,
) -> UserRead:
    user = await user_service.update_user(session, user_id, payload)
    return UserRead.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, session: SessionDependency) -> Response:
    await user_service.delete_user(session, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
