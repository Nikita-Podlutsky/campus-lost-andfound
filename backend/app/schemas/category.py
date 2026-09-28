from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

from app.schemas.common import PatchSchema, RequestSchema

CategoryName = Annotated[str, StringConstraints(min_length=2, max_length=80)]
CategoryDescription = Annotated[str, StringConstraints(min_length=1, max_length=300)]


class CategoryCreate(RequestSchema):
    name: CategoryName
    description: CategoryDescription | None = None


class CategoryPatch(PatchSchema):
    name: CategoryName | None = None
    description: CategoryDescription | None = None

    @model_validator(mode="after")
    def reject_null_name(self) -> "CategoryPatch":
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("Поле 'name' не может быть null")
        return self


class CategorySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CategoryRead(CategorySummary):
    description: str | None
    created_at: datetime
    updated_at: datetime
