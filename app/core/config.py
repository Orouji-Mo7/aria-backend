"""Application configuration loaded from environment variables."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

Environment = Literal["development", "staging", "production", "test"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """Runtime configuration sourced from environment variables or `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    project_name: str = "ARIA Backend"
    api_v1_prefix: str = "/api/v1"

    environment: Environment = "development"
    debug: bool = False
    log_level: LogLevel = "INFO"

    database_url: str = Field(
        default="postgresql+asyncpg://aria:aria@localhost:15432/aria",
        description="Async SQLAlchemy database URL.",
    )

    # NoDecode: disable pydantic-settings' implicit JSON decoding for this list
    # field so the validator below owns the parsing (CSV, JSON, single value).
    cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=lambda: ["*"])

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: object) -> object:
        if value is None or isinstance(value, list):
            return value
        if not isinstance(value, str):
            return value

        raw = value.strip()
        if not raw:
            return ["*"]
        if raw == "*":
            return ["*"]
        if raw.startswith("["):
            parsed = json.loads(raw)
            if not isinstance(parsed, list):
                raise ValueError("cors_origins JSON must decode to a list")
            return [str(item).strip() for item in parsed if str(item).strip()]
        return [item.strip() for item in raw.split(",") if item.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
