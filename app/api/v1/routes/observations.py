"""Observation endpoints. Vital signs are nested under a patient resource."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.errors import ProblemDetail
from app.schemas.observation import (
    ObservationCreate,
    ObservationList,
    ObservationRead,
)
from app.services.observation_service import ObservationService

router = APIRouter(tags=["observations"])


def _service(session: Annotated[AsyncSession, Depends(get_session)]) -> ObservationService:
    return ObservationService(session)


ServiceDep = Annotated[ObservationService, Depends(_service)]


@router.post(
    "/patients/{patient_id}/observations",
    response_model=ObservationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record an observation for a patient",
    responses={status.HTTP_404_NOT_FOUND: {"model": ProblemDetail}},
)
async def create_observation(
    patient_id: UUID,
    payload: ObservationCreate,
    service: ServiceDep,
) -> ObservationRead:
    """Persist a new vital-sign observation for the given patient."""
    observation = await service.create_observation(patient_id, payload)
    return ObservationRead.model_validate(observation)


@router.get(
    "/patients/{patient_id}/observations",
    response_model=ObservationList,
    summary="List observations for a patient",
    responses={status.HTTP_404_NOT_FOUND: {"model": ProblemDetail}},
)
async def list_observations(
    patient_id: UUID,
    service: ServiceDep,
    code: Annotated[
        str | None,
        Query(description="Filter to a specific LOINC code, e.g. '8867-4'."),
    ] = None,
    since: Annotated[
        datetime | None,
        Query(description="Only return observations recorded at or after this instant."),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ObservationList:
    """Return observations for a patient ordered by `effective_at` descending."""
    items, total = await service.list_observations_for_patient(
        patient_id,
        code=code,
        since=since,
        limit=limit,
        offset=offset,
    )
    return ObservationList(
        items=[ObservationRead.model_validate(o) for o in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/patients/{patient_id}/observations/latest",
    response_model=list[ObservationRead],
    summary="Latest observation per code for a patient",
    responses={status.HTTP_404_NOT_FOUND: {"model": ProblemDetail}},
)
async def latest_observations(
    patient_id: UUID,
    service: ServiceDep,
    code: Annotated[
        list[str] | None,
        Query(description="Restrict to one or more LOINC codes; repeatable."),
    ] = None,
) -> list[ObservationRead]:
    """Return the most recent observation for each distinct code."""
    items = await service.latest_per_code(patient_id, codes=code)
    return [ObservationRead.model_validate(o) for o in items]


@router.get(
    "/observations/{observation_id}",
    response_model=ObservationRead,
    summary="Retrieve an observation",
    responses={status.HTTP_404_NOT_FOUND: {"model": ProblemDetail}},
)
async def get_observation(
    observation_id: UUID,
    service: ServiceDep,
) -> ObservationRead:
    """Return a single observation by ID."""
    observation = await service.get_observation(observation_id)
    return ObservationRead.model_validate(observation)
