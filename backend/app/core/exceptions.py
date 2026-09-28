class AppError(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class EntityNotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class EntityConflictError(AppError):
    status_code = 409
    code = "CONFLICT"


class RelatedEntityNotFoundError(AppError):
    status_code = 422
    code = "RELATED_ENTITY_NOT_FOUND"


class DatabaseUnavailableError(AppError):
    status_code = 503
    code = "DATABASE_UNAVAILABLE"
