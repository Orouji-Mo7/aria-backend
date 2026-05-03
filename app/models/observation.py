"""Observation ORM model. FHIR-aligned vital signs."""

from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin

LOINC_SYSTEM = "http://loinc.org"


class ObservationStatus(str, enum.Enum):
    """FHIR Observation.status value set (subset)."""

    FINAL = "final"
    PRELIMINARY = "preliminary"
    AMENDED = "amended"
    ENTERED_IN_ERROR = "entered_in_error"


class Observation(TimestampMixin, Base):
    """A single clinical measurement, modeled after FHIR Observation."""

    __tablename__ = "observations"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)

    patient_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    code_system: Mapped[str] = mapped_column(
        String(255), nullable=False, default=LOINC_SYSTEM
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    code_display: Mapped[str] = mapped_column(String(255), nullable=False)

    value_numeric: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    value_unit: Mapped[str] = mapped_column(String(32), nullable=False)

    effective_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    status: Mapped[ObservationStatus] = mapped_column(
        Enum(
            ObservationStatus,
            name="observation_status",
            native_enum=False,
            length=32,
        ),
        nullable=False,
        default=ObservationStatus.FINAL,
    )

    recorded_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    note: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    __table_args__ = (
        Index(
            "ix_observations_patient_effective",
            "patient_id",
            "effective_at",
        ),
        Index(
            "ix_observations_patient_code_effective",
            "patient_id",
            "code",
            "effective_at",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"Observation(id={self.id!s}, patient_id={self.patient_id!s}, "
            f"code={self.code!r}, effective_at={self.effective_at!s})"
        )
