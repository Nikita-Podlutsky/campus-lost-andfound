from pydantic import BaseModel, ConfigDict, model_validator


class RequestSchema(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )


class PatchSchema(RequestSchema):
    @model_validator(mode="after")
    def validate_not_empty(self) -> "PatchSchema":
        if not self.model_fields_set:
            raise ValueError("Передайте хотя бы одно поле для изменения")
        return self


class MessageResponse(BaseModel):
    message: str
