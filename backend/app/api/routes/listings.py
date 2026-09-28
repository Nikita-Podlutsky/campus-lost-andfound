from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.listing import ListingStatus, ListingType
from app.schemas.listing import ListingCreate, ListingPage, ListingPatch, ListingRead
from app.services import listings as listing_service

router = APIRouter(prefix="/listings", tags=["Объявления"])
SessionDependency = Annotated[AsyncSession, Depends(get_session)]


@router.post("", response_model=ListingRead, status_code=status.HTTP_201_CREATED)
async def create_listing(
    payload: ListingCreate,
    session: SessionDependency,
) -> ListingRead:
    listing = await listing_service.create_listing(session, payload)
    return ListingRead.model_validate(listing)


@router.get("", response_model=ListingPage)
async def get_listings(
    session: SessionDependency,
    listing_type: Annotated[ListingType | None, Query(alias="type")] = None,
    listing_status: Annotated[ListingStatus | None, Query(alias="status")] = None,
    author_id: UUID | None = None,
    category_id: Annotated[int | None, Query(ge=1)] = None,
    query: Annotated[
        str | None,
        Query(alias="q", min_length=1, max_length=100),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ListingPage:
    items, total = await listing_service.list_listings(
        session,
        listing_type=listing_type,
        status=listing_status,
        author_id=author_id,
        category_id=category_id,
        query=query,
        limit=limit,
        offset=offset,
    )
    return ListingPage(
        items=[ListingRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{listing_id}", response_model=ListingRead)
async def get_listing(listing_id: UUID, session: SessionDependency) -> ListingRead:
    listing = await listing_service.get_listing(session, listing_id)
    return ListingRead.model_validate(listing)


@router.patch("/{listing_id}", response_model=ListingRead)
async def update_listing(
    listing_id: UUID,
    payload: ListingPatch,
    session: SessionDependency,
) -> ListingRead:
    listing = await listing_service.update_listing(session, listing_id, payload)
    return ListingRead.model_validate(listing)


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(listing_id: UUID, session: SessionDependency) -> Response:
    await listing_service.delete_listing(session, listing_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
