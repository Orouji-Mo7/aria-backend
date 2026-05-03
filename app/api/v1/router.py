"""Aggregates all v1 sub-routers under a single APIRouter."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes import health, observations, patients

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(patients.router)
api_router.include_router(observations.router)
