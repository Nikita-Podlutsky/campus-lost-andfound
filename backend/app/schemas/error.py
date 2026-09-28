from pydantic import BaseModel


class FieldError(BaseModel):
    field: str
    message: str
    type: str


class ErrorResponse(BaseModel):
    detail: str
    code: str
    errors: list[FieldError] | None = None
