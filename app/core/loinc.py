"""LOINC code constants for the standard vital signs panel.

These constants are the single source of truth for the codes the system emits
and accepts. They are consumed by the API layer, seed data, and the frontend.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ObservationCode:
    """A LOINC code paired with its expected display text and UCUM unit."""

    code: str
    display: str
    unit: str


HEART_RATE = ObservationCode(code="8867-4", display="Heart rate", unit="/min")
SPO2 = ObservationCode(
    code="2708-6",
    display="Oxygen saturation in Arterial blood",
    unit="%",
)
BODY_TEMP = ObservationCode(code="8310-5", display="Body temperature", unit="Cel")
RESP_RATE = ObservationCode(code="9279-1", display="Respiratory rate", unit="/min")
BP_SYSTOLIC = ObservationCode(
    code="8480-6",
    display="Systolic blood pressure",
    unit="mm[Hg]",
)
BP_DIASTOLIC = ObservationCode(
    code="8462-4",
    display="Diastolic blood pressure",
    unit="mm[Hg]",
)


VITAL_SIGNS: tuple[ObservationCode, ...] = (
    HEART_RATE,
    SPO2,
    BODY_TEMP,
    RESP_RATE,
    BP_SYSTOLIC,
    BP_DIASTOLIC,
)


__all__ = [
    "BODY_TEMP",
    "BP_DIASTOLIC",
    "BP_SYSTOLIC",
    "HEART_RATE",
    "ObservationCode",
    "RESP_RATE",
    "SPO2",
    "VITAL_SIGNS",
]
