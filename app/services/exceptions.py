"""Domain-level exceptions shared across services."""

from __future__ import annotations


class DomainError(Exception):
    """Base class for application-level errors."""


class NotFoundError(DomainError):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str, identifier: object) -> None:
        super().__init__(f"{resource} not found: {identifier}")
        self.resource = resource
        self.identifier = identifier


class ConflictError(DomainError):
    """Raised when an operation violates a uniqueness or state constraint."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
