"""Patient domain service. All persistence access for patients flows through here."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.schemas.patient import PatientCreate
from app.services.exceptions import ConflictError, NotFoundError


class PatientService:
    """Encapsulates patient persistence operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_patients(self, *, limit: int, offset: int) -> tuple[list[Patient], int]:
        """Return a page of patients ordered by creation time, plus the total count."""
        items_stmt = (
            select(Patient)
            .order_by(Patient.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        count_stmt = select(func.count()).select_from(Patient)

        items = (await self._session.execute(items_stmt)).scalars().all()
        total = (await self._session.execute(count_stmt)).scalar_one()

        return list(items), int(total)

    async def get_patient(self, patient_id: UUID) -> Patient:
        """Fetch a single patient by ID or raise `NotFoundError`."""
        patient = await self._session.get(Patient, patient_id)
        if patient is None:
            raise NotFoundError("Patient", patient_id)
        return patient

    async def create_patient(self, data: PatientCreate) -> Patient:
        """Persist a new patient. Raises `ConflictError` if the MRN is taken."""
        patient = Patient(**data.model_dump())
        self._session.add(patient)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            await self._session.rollback()
            raise ConflictError(f"Patient with MRN '{data.mrn}' already exists.") from exc
        await self._session.commit()
        await self._session.refresh(patient)
        return patient
