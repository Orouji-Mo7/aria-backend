"""Structured logging configuration based on structlog."""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from app.core.config import get_settings


def configure_logging() -> None:
    """Configure stdlib logging and structlog with environment-aware processors."""
    settings = get_settings()
    level = getattr(logging, settings.log_level, logging.INFO)

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.stdlib.add_logger_name,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    renderer: Processor = (
        structlog.dev.ConsoleRenderer(colors=True)
        if settings.environment == "development"
        else structlog.processors.JSONRenderer()
    )

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)

    for noisy in ("uvicorn", "uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(level)


def get_logger(name: str | None = None, **initial_values: Any) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger, optionally pre-bound with context."""
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    if initial_values:
        logger = logger.bind(**initial_values)
    return logger
