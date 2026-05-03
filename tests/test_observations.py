"""Tests for the Observation API."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from httpx import AsyncClient


def _patient_payload(mrn: str = "MRN-OBS-001") -> dict[str, Any]:
    return {
        "mrn": mrn,
        "given_name": "Ada",
        "family_name": "Lovelace",
        "birth_date": "1980-01-01",
        "gender": "female",
    }


def _observation_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "code": "8867-4",
        "code_display": "Heart rate",
        "value_numeric": "72",
        "value_unit": "/min",
        "effective_at": (datetime.now(timezone.utc) - timedelta(minutes=5))
        .isoformat()
        .replace("+00:00", "Z"),
    }
    payload.update(overrides)
    return payload


async def _create_patient(client: AsyncClient, mrn: str = "MRN-OBS-001") -> str:
    response = await client.post("/api/v1/patients", json=_patient_payload(mrn))
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.fixture
async def patient_id(client: AsyncClient) -> str:
    return await _create_patient(client)


async def test_create_observation_for_existing_patient(
    client: AsyncClient, patient_id: str
) -> None:
    response = await client.post(
        f"/api/v1/patients/{patient_id}/observations",
        json=_observation_payload(),
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["patient_id"] == patient_id
    assert body["code"] == "8867-4"
    assert body["code_display"] == "Heart rate"
    assert body["code_system"] == "http://loinc.org"
    assert body["value_unit"] == "/min"
    assert body["status"] == "final"
    assert float(body["value_numeric"]) == 72.0
    assert "id" in body
    assert "created_at" in body


async def test_create_observation_for_nonexistent_patient(client: AsyncClient) -> None:
    missing_id = "00000000-0000-0000-0000-000000000000"
    response = await client.post(
        f"/api/v1/patients/{missing_id}/observations",
        json=_observation_payload(),
    )

    assert response.status_code == 404
    assert response.json()["title"] == "Resource not found"


async def test_list_observations_filters_by_code(
    client: AsyncClient, patient_id: str
) -> None:
    base = datetime.now(timezone.utc) - timedelta(hours=1)
    samples = [
        ("8867-4", "Heart rate", "/min", "70"),
        ("8867-4", "Heart rate", "/min", "75"),
        ("8310-5", "Body temperature", "Cel", "37.1"),
    ]
    for offset, (code, display, unit, value) in enumerate(samples):
        payload = _observation_payload(
            code=code,
            code_display=display,
            value_unit=unit,
            value_numeric=value,
            effective_at=(base + timedelta(minutes=offset))
            .isoformat()
            .replace("+00:00", "Z"),
        )
        response = await client.post(
            f"/api/v1/patients/{patient_id}/observations", json=payload
        )
        assert response.status_code == 201, response.text

    response = await client.get(
        f"/api/v1/patients/{patient_id}/observations",
        params={"code": "8867-4"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert {item["code"] for item in body["items"]} == {"8867-4"}


async def test_list_observations_filters_by_since(
    client: AsyncClient, patient_id: str
) -> None:
    now = datetime.now(timezone.utc)
    old = now - timedelta(hours=6)
    recent = now - timedelta(minutes=10)

    for ts, value in [(old, "68"), (recent, "82")]:
        payload = _observation_payload(
            value_numeric=value,
            effective_at=ts.isoformat().replace("+00:00", "Z"),
        )
        response = await client.post(
            f"/api/v1/patients/{patient_id}/observations", json=payload
        )
        assert response.status_code == 201, response.text

    cutoff = (now - timedelta(hours=1)).isoformat().replace("+00:00", "Z")
    response = await client.get(
        f"/api/v1/patients/{patient_id}/observations",
        params={"since": cutoff},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert float(body["items"][0]["value_numeric"]) == 82.0


async def test_latest_per_code_returns_one_per_code(
    client: AsyncClient, patient_id: str
) -> None:
    base = datetime.now(timezone.utc) - timedelta(hours=2)
    samples = [
        ("8867-4", "Heart rate", "/min", "70", base),
        ("8867-4", "Heart rate", "/min", "78", base + timedelta(minutes=30)),
        ("8867-4", "Heart rate", "/min", "82", base + timedelta(minutes=60)),
        ("8310-5", "Body temperature", "Cel", "36.9", base),
        ("8310-5", "Body temperature", "Cel", "37.4", base + timedelta(minutes=45)),
    ]
    for code, display, unit, value, ts in samples:
        payload = _observation_payload(
            code=code,
            code_display=display,
            value_unit=unit,
            value_numeric=value,
            effective_at=ts.isoformat().replace("+00:00", "Z"),
        )
        response = await client.post(
            f"/api/v1/patients/{patient_id}/observations", json=payload
        )
        assert response.status_code == 201, response.text

    response = await client.get(
        f"/api/v1/patients/{patient_id}/observations/latest"
    )
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    by_code = {item["code"]: item for item in items}
    assert float(by_code["8867-4"]["value_numeric"]) == 82.0
    assert float(by_code["8310-5"]["value_numeric"]) == 37.4


async def test_value_numeric_must_be_positive(
    client: AsyncClient, patient_id: str
) -> None:
    response = await client.post(
        f"/api/v1/patients/{patient_id}/observations",
        json=_observation_payload(value_numeric="0"),
    )
    assert response.status_code == 422


async def test_effective_at_in_future_rejected(
    client: AsyncClient, patient_id: str
) -> None:
    far_future = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat().replace(
        "+00:00", "Z"
    )
    response = await client.post(
        f"/api/v1/patients/{patient_id}/observations",
        json=_observation_payload(effective_at=far_future),
    )
    assert response.status_code == 422
