"""Patient ORM model."""

from __future__ import annotations

import enum
from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, Enum, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Gender(str, enum.Enum):
    """FHIR-aligned administrative gender."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class PatientStatus(str, enum.Enum):
    """Lifecycle status of a patient record."""

    ACTIVE = "active"
    DISCHARGED = "discharged"


class Patient(TimestampMixin, Base):
    """A patient under care. Modeled to align with FHIR Patient where reasonable."""

    __tablename__ = "patients"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)

    mrn: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    given_name: Mapped[str] = mapped_column(String(128), nullable=False)
    family_name: Mapped[str] = mapped_column(String(128), nullable=False)

    birth_date: Mapped[date] = mapped_column(Date, nullable=False)

    gender: Mapped[Gender] = mapped_column(
        Enum(Gender, name="patient_gender", native_enum=False, length=16),
        nullable=False,
        default=Gender.UNKNOWN,
    )

    admission_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    room_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    station: Mapped[str | None] = mapped_column(String(64), nullable=True)

    status: Mapped[PatientStatus] = mapped_column(
        Enum(PatientStatus, name="patient_status", native_enum=False, length=16),
        nullable=False,
        default=PatientStatus.ACTIVE,
        index=True,
    )

    def __repr__(self) -> str:
        return f"Patient(id={self.id!s}, mrn={self.mrn!r})"
