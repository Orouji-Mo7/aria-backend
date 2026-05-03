"""Tests for Settings env-var parsing, especially cors_origins."""

from __future__ import annotations

import pytest

from app.core.config import Settings


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent the repo .env file from leaking into these tests."""
    monkeypatch.setattr(Settings.model_config, "env_file", None, raising=False)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)


def _build(monkeypatch: pytest.MonkeyPatch, value: str) -> Settings:
    monkeypatch.setenv("CORS_ORIGINS", value)
    return Settings()


def test_cors_origins_comma_separated(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _build(monkeypatch, "http://localhost:3000,http://localhost:5173")
    assert settings.cors_origins == [
        "http://localhost:3000",
        "http://localhost:5173",
    ]


def test_cors_origins_comma_separated_with_whitespace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = _build(monkeypatch, " http://a.test , http://b.test ,, ")
    assert settings.cors_origins == ["http://a.test", "http://b.test"]


def test_cors_origins_json_array(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _build(monkeypatch, '["http://a.test","http://b.test"]')
    assert settings.cors_origins == ["http://a.test", "http://b.test"]


def test_cors_origins_single_value(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _build(monkeypatch, "http://only.test")
    assert settings.cors_origins == ["http://only.test"]


def test_cors_origins_wildcard(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _build(monkeypatch, "*")
    assert settings.cors_origins == ["*"]


def test_cors_origins_default_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings()
    assert settings.cors_origins == ["*"]
