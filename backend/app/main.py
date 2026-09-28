from typing import Annotated, Any

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError, DatabaseUnavailableError
from app.db.session import get_session
from app.schemas.error import ErrorResponse, FieldError
from app.schemas.health import DatabaseHealthResponse, HealthResponse

settings = get_settings()
SessionDependency = Annotated[AsyncSession, Depends(get_session)]

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


def _localized_validation_message(error: dict[str, Any]) -> str:
    error_type = error["type"]
    context = error.get("ctx", {})

    if error_type == "missing":
        return "Поле обязательно для заполнения"
    if error_type == "extra_forbidden":
        return "Лишние поля не допускаются"
    if error_type == "string_too_short":
        return f"Значение должно содержать не менее {context.get('min_length')} символов"
    if error_type == "string_too_long":
        return f"Значение должно содержать не более {context.get('max_length')} символов"
    if error_type == "greater_than_equal":
        return f"Значение должно быть не меньше {context.get('ge')}"
    if error_type == "less_than_equal":
        return f"Значение должно быть не больше {context.get('le')}"
    if error_type in {"url_parsing", "url_scheme", "url_type"}:
        return "Укажите корректный URL"
    if error_type in {"int_parsing", "int_type", "float_parsing", "float_type"}:
        return "Укажите числовое значение"
    if error_type in {"json_invalid", "json_type"}:
        return "Тело запроса должно содержать корректный JSON"
    if error_type == "enum":
        return "Укажите одно из допустимых значений"
    if error_type == "value_error":
        return str(error.get("msg", "")).removeprefix("Value error, ")
    return "Некорректное значение поля"


@app.exception_handler(AppError)
async def handle_app_error(request: Request, error: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content=ErrorResponse(detail=error.message, code=error.code).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    errors = [
        FieldError(
            field=".".join(str(part) for part in item["loc"]),
            message=_localized_validation_message(item),
            type=item["type"],
        )
        for item in error.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            detail="Запрос содержит некорректные данные",
            code="VALIDATION_ERROR",
            errors=errors,
        ).model_dump(),
    )


@app.exception_handler(StarletteHTTPException)
async def handle_http_error(
    request: Request,
    error: StarletteHTTPException,
) -> JSONResponse:
    default_messages = {
        404: "Ресурс не найден",
        405: "Метод не поддерживается",
    }
    detail = (
        error.detail
        if isinstance(error.detail, str)
        else default_messages.get(
            error.status_code,
            "Ошибка HTTP-запроса",
        )
    )
    detail = default_messages.get(error.status_code, detail)
    return JSONResponse(
        status_code=error.status_code,
        content=ErrorResponse(
            detail=detail,
            code=f"HTTP_{error.status_code}",
        ).model_dump(),
    )


@app.exception_handler(SQLAlchemyError)
async def handle_database_error(
    request: Request,
    error: SQLAlchemyError,
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content=ErrorResponse(
            detail="База данных недоступна",
            code="DATABASE_UNAVAILABLE",
        ).model_dump(),
    )


@app.get("/health", response_model=HealthResponse, tags=["Система"])
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )


@app.get("/health/db", response_model=DatabaseHealthResponse, tags=["Система"])
async def database_health_check(session: SessionDependency) -> DatabaseHealthResponse:
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise DatabaseUnavailableError("Проверка базы данных не пройдена") from error

    return DatabaseHealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        database="ok",
    )
