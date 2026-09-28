from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from app.schemas.common import PatchSchema, RequestSchema

DisplayName = Annotated[str, StringConstraints(min_length=2, max_length=100)]
EmailAddress = Annotated[EmailStr, Field(max_length=320)]


class UserCreate(RequestSchema):
    display_name: DisplayName
    email: EmailAddress

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value


class UserPatch(PatchSchema):
    display_name: DisplayName | None = None
    email: EmailAddress | None = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> "UserPatch":
        for field_name in ("display_name", "email"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"Поле '{field_name}' не может быть null")
        return self


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    display_name: str
    email: EmailAddress


class UserRead(UserSummary):
    created_at: datetime
    updated_at: datetime
