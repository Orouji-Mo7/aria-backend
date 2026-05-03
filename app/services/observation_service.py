"""Observation domain service. All persistence access for observations flows through here."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.observation import Observation
from app.models.patient import Patient
from app.schemas.observation import ObservationCreate
from app.services.exceptions import NotFoundError


class ObservationService:
    """Encapsulates observation persistence operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_observation(
        self, patient_id: UUID, data: ObservationCreate
    ) -> Observation:
        """Persist a new observation for an existing patient."""
        patient = await self._session.get(Patient, patient_id)
        if patient is None:
            raise NotFoundError("Patient", patient_id)

        observation = Observation(patient_id=patient_id, **data.model_dump())
        self._session.add(observation)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(observation)
        return observation

    async def get_observation(self, observation_id: UUID) -> Observation:
        """Fetch a single observation by ID or raise `NotFoundError`."""
        observation = await self._session.get(Observation, observation_id)
        if observation is None:
            raise NotFoundError("Observation", observation_id)
        return observation

    async def list_observations_for_patient(
        self,
        patient_id: UUID,
        *,
        code: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Observation], int]:
        """Return a page of observations for a patient, newest first.

        Verifies that the patient exists; otherwise raises `NotFoundError`. This
        matches the REST contract of nesting observations under a patient
        resource and avoids returning an empty list for an unknown patient.
        """
        patient = await self._session.get(Patient, patient_id)
        if patient is None:
            raise NotFoundError("Patient", patient_id)

        filters = [Observation.patient_id == patient_id]
        if code is not None:
            filters.append(Observation.code == code)
        if since is not None:
            filters.append(Observation.effective_at >= since)

        items_stmt = (
            select(Observation)
            .where(*filters)
            .order_by(Observation.effective_at.desc())
            .limit(limit)
            .offset(offset)
        )
        count_stmt = select(func.count()).select_from(Observation).where(*filters)

        items = (await self._session.execute(items_stmt)).scalars().all()
        total = (await self._session.execute(count_stmt)).scalar_one()

        return list(items), int(total)

    async def latest_per_code(
        self,
        patient_id: UUID,
        *,
        codes: list[str] | None = None,
    ) -> list[Observation]:
        """Return the most recent observation per LOINC code for a patient.

        Optionally restricted to a subset of `codes`. Used by the station
        dashboard to render the current vital-signs panel in a single round-trip.
        """
        patient = await self._session.get(Patient, patient_id)
        if patient is None:
            raise NotFoundError("Patient", patient_id)

        row_number = (
            func.row_number()
            .over(
                partition_by=Observation.code,
                order_by=Observation.effective_at.desc(),
            )
            .label("rn")
        )

        base = select(Observation, row_number).where(
            Observation.patient_id == patient_id
        )
        if codes:
            base = base.where(Observation.code.in_(codes))

        ranked = base.subquery()
        observation_alias = ranked.c

        latest_stmt = (
            select(Observation)
            .join(ranked, Observation.id == observation_alias.id)
            .where(observation_alias.rn == 1)
            .order_by(observation_alias.code)
        )

        result = await self._session.execute(latest_stmt)
        return list(result.scalars().all())


__all__ = ["ObservationService"]
