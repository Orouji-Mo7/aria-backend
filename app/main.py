"""FastAPI application entry point."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import __version__
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import engine
from app.core.logging import configure_logging, get_logger
from app.schemas.errors import ProblemDetail
from app.services.exceptions import ConflictError, DomainError, NotFoundError

PROBLEM_CONTENT_TYPE = "application/problem+json"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Run application startup and shutdown hooks."""
    configure_logging()
    logger = get_logger(__name__)
    settings = get_settings()
    logger.info(
        "application.startup",
        environment=settings.environment,
        version=__version__,
    )
    try:
        yield
    finally:
        await engine.dispose()
        logger.info("application.shutdown")


def _problem_response(problem: ProblemDetail) -> JSONResponse:
    return JSONResponse(
        status_code=problem.status,
        content=problem.model_dump(exclude_none=True),
        media_type=PROBLEM_CONTENT_TYPE,
    )


def _register_exception_handlers(app: FastAPI) -> None:
    logger = get_logger("app.errors")

    @app.exception_handler(NotFoundError)
    async def _not_found(request: Request, exc: NotFoundError) -> JSONResponse:
        return _problem_response(
            ProblemDetail(
                title="Resource not found",
                status=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
                instance=str(request.url.path),
            )
        )

    @app.exception_handler(ConflictError)
    async def _conflict(request: Request, exc: ConflictError) -> JSONResponse:
        return _problem_response(
            ProblemDetail(
                title="Conflict",
                status=status.HTTP_409_CONFLICT,
                detail=exc.message,
                instance=str(request.url.path),
            )
        )

    @app.exception_handler(DomainError)
    async def _domain(request: Request, exc: DomainError) -> JSONResponse:
        logger.warning("domain.error", error=str(exc), path=request.url.path)
        return _problem_response(
            ProblemDetail(
                title="Bad request",
                status=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
                instance=str(request.url.path),
            )
        )

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors: list[dict[str, Any]] = [
            {
                "location": list(err.get("loc", [])),
                "message": err.get("msg"),
                "type": err.get("type"),
            }
            for err in exc.errors()
        ]
        return _problem_response(
            ProblemDetail(
                title="Validation error",
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The request body failed validation.",
                instance=str(request.url.path),
                errors=errors,
            )
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _problem_response(
            ProblemDetail(
                title=exc.detail if isinstance(exc.detail, str) else "HTTP error",
                status=exc.status_code,
                detail=str(exc.detail) if exc.detail else None,
                instance=str(request.url.path),
            )
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled.exception", path=request.url.path)
        settings = get_settings()
        detail = str(exc) if settings.debug else "An unexpected error occurred."
        return _problem_response(
            ProblemDetail(
                title="Internal server error",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=detail,
                instance=str(request.url.path),
            )
        )


def create_app() -> FastAPI:
    """Application factory. Allows test overrides without import-time side effects."""
    settings = get_settings()
    configure_logging()

    app = FastAPI(
        title=settings.project_name,
        version=__version__,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    _register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
