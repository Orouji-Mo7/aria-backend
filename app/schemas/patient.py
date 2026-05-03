"""Pydantic schemas for the Patient resource."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.patient import Gender, PatientStatus


class PatientBase(BaseModel):
    """Fields shared between create requests and responses."""

    mrn: str = Field(..., min_length=1, max_length=64, description="Medical record number.")
    given_name: str = Field(..., min_length=1, max_length=128)
    family_name: str = Field(..., min_length=1, max_length=128)
    birth_date: date
    gender: Gender = Gender.UNKNOWN
    admission_date: datetime | None = None
    room_number: str | None = Field(default=None, max_length=32)
    station: str | None = Field(default=None, max_length=64)


class PatientCreate(PatientBase):
    """Payload accepted by `POST /patients`."""

    status: PatientStatus = PatientStatus.ACTIVE


class PatientRead(PatientBase):
    """Patient representation returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: PatientStatus
    created_at: datetime
    updated_at: datetime


class PatientList(BaseModel):
    """Paginated list of patients."""

    items: list[PatientRead]
    total: int
    limit: int
    offset: int
