from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints, model_validator

from app.models.listing import ListingStatus, ListingType
from app.schemas.category import CategorySummary
from app.schemas.common import PatchSchema, RequestSchema
from app.schemas.user import UserSummary

ListingTitle = Annotated[str, StringConstraints(min_length=2, max_length=120)]
ListingDescription = Annotated[str, StringConstraints(min_length=1, max_length=5000)]
ListingLocation = Annotated[str, StringConstraints(min_length=2, max_length=500)]
PhotoUrl = Annotated[HttpUrl, Field(max_length=2048)]
MapCoordinate = Annotated[float, Field(ge=0, le=100, allow_inf_nan=False)]


class ListingCreate(RequestSchema):
    type: ListingType = ListingType.FOUND
    status: ListingStatus = ListingStatus.ACTIVE
    title: ListingTitle
    description: ListingDescription
    photo_url: PhotoUrl | None = None
    location: ListingLocation
    x: MapCoordinate
    y: MapCoordinate
    author_id: UUID
    category_id: int = Field(ge=1)


class ListingPatch(PatchSchema):
    type: ListingType | None = None
    status: ListingStatus | None = None
    title: ListingTitle | None = None
    description: ListingDescription | None = None
    photo_url: PhotoUrl | None = None
    location: ListingLocation | None = None
    x: MapCoordinate | None = None
    y: MapCoordinate | None = None
    author_id: UUID | None = None
    category_id: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> "ListingPatch":
        required_fields = (
            "type",
            "status",
            "title",
            "description",
            "location",
            "x",
            "y",
            "author_id",
            "category_id",
        )
        for field_name in required_fields:
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"Поле '{field_name}' не может быть null")
        return self


class ListingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: ListingType
    status: ListingStatus
    title: str
    description: str
    photo_url: str | None
    location: str
    x: float
    y: float
    author_id: UUID
    category_id: int
    author: UserSummary
    category: CategorySummary
    created_at: datetime
    updated_at: datetime


class ListingPage(BaseModel):
    items: list[ListingRead]
    total: int
    limit: int
    offset: int
