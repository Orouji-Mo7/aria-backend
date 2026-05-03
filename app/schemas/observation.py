"""Pydantic schemas for the Observation resource."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.observation import LOINC_SYSTEM, ObservationStatus

_FUTURE_TOLERANCE = timedelta(minutes=1)


class ObservationBase(BaseModel):
    """Fields shared between create requests and responses."""

    code: str = Field(..., min_length=1, max_length=64, description="LOINC code, e.g. '8867-4'.")
    code_display: str = Field(..., min_length=1, max_length=255)
    code_system: str = Field(default=LOINC_SYSTEM, max_length=255)
    value_numeric: Decimal = Field(..., description="Numeric value of the measurement.")
    value_unit: str = Field(..., min_length=1, max_length=32, description="UCUM unit.")
    effective_at: datetime = Field(..., description="Clinical time the measurement was taken.")
    status: ObservationStatus = ObservationStatus.FINAL
    recorded_by: str | None = Field(default=None, max_length=128)
    note: str | None = Field(default=None, max_length=1024)

    @field_validator("value_numeric")
    @classmethod
    def _value_must_be_positive(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("value_numeric must be greater than zero.")
        return value

    @field_validator("effective_at")
    @classmethod
    def _effective_at_not_in_future(cls, value: datetime) -> datetime:
        reference = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        if reference - now > _FUTURE_TOLERANCE:
            raise ValueError("effective_at must not be in the future.")
        return value


class ObservationCreate(ObservationBase):
    """Payload accepted by `POST /patients/{patient_id}/observations`."""


class ObservationRead(ObservationBase):
    """Observation representation returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: UUID
    created_at: datetime
    updated_at: datetime


class ObservationList(BaseModel):
    """Paginated list of observations."""

    items: list[ObservationRead]
    total: int
    limit: int
    offset: int
