from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.category import CategoryCreate, CategoryPatch, CategoryRead
from app.services import categories as category_service

router = APIRouter(prefix="/categories", tags=["Категории"])
SessionDependency = Annotated[AsyncSession, Depends(get_session)]


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    session: SessionDependency,
) -> CategoryRead:
    category = await category_service.create_category(session, payload)
    return CategoryRead.model_validate(category)


@router.get("", response_model=list[CategoryRead])
async def get_categories(session: SessionDependency) -> list[CategoryRead]:
    categories = await category_service.list_categories(session)
    return [CategoryRead.model_validate(category) for category in categories]


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: int, session: SessionDependency) -> CategoryRead:
    category = await category_service.get_category(session, category_id)
    return CategoryRead.model_validate(category)


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    payload: CategoryPatch,
    session: SessionDependency,
) -> CategoryRead:
    category = await category_service.update_category(session, category_id, payload)
    return CategoryRead.model_validate(category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, session: SessionDependency) -> Response:
    await category_service.delete_category(session, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
