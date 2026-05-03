"""Patient CRUD endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.errors import ProblemDetail
from app.schemas.patient import PatientCreate, PatientList, PatientRead
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["patients"])


def _service(session: Annotated[AsyncSession, Depends(get_session)]) -> PatientService:
    return PatientService(session)


ServiceDep = Annotated[PatientService, Depends(_service)]


@router.get(
    "",
    response_model=PatientList,
    summary="List patients",
)
async def list_patients(
    service: ServiceDep,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PatientList:
    """Return a paginated list of patients ordered by recency."""
    items, total = await service.list_patients(limit=limit, offset=offset)
    return PatientList(
        items=[PatientRead.model_validate(p) for p in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{patient_id}",
    response_model=PatientRead,
    summary="Retrieve a patient",
    responses={status.HTTP_404_NOT_FOUND: {"model": ProblemDetail}},
)
async def get_patient(patient_id: UUID, service: ServiceDep) -> PatientRead:
    """Return a single patient by ID."""
    patient = await service.get_patient(patient_id)
    return PatientRead.model_validate(patient)


@router.post(
    "",
    response_model=PatientRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a patient",
    responses={status.HTTP_409_CONFLICT: {"model": ProblemDetail}},
)
async def create_patient(payload: PatientCreate, service: ServiceDep) -> PatientRead:
    """Create a new patient record."""
    patient = await service.create_patient(payload)
    return PatientRead.model_validate(patient)
