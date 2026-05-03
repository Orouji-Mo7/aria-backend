"""Liveness and readiness probes."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import __version__
from app.core.database import get_session
from app.schemas.errors import ProblemDetail

router = APIRouter(prefix="/health", tags=["health"])


class HealthStatus(BaseModel):
    status: Literal["ok"] = "ok"
    version: str


class ReadyStatus(BaseModel):
    status: Literal["ready"] = "ready"
    database: Literal["ok"] = "ok"


@router.get(
    "",
    response_model=HealthStatus,
    summary="Liveness probe",
)
async def health() -> HealthStatus:
    """Return basic process health and the deployed version."""
    return HealthStatus(version=__version__)


@router.get(
    "/ready",
    response_model=ReadyStatus,
    summary="Readiness probe",
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ProblemDetail,
            "description": "Database is not reachable.",
        }
    },
)
async def ready(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReadyStatus:
    """Verify the database is reachable before declaring the service ready."""
    await session.execute(text("SELECT 1"))
    return ReadyStatus()
