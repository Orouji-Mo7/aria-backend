"""RFC 7807 Problem Details schema."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProblemDetail(BaseModel):
    """Error response body following RFC 7807."""

    model_config = ConfigDict(populate_by_name=True)

    type: str = Field(default="about:blank", description="URI reference identifying the problem type.")
    title: str = Field(..., description="Short, human-readable summary of the problem.")
    status: int = Field(..., description="HTTP status code.")
    detail: str | None = Field(default=None, description="Human-readable explanation.")
    instance: str | None = Field(default=None, description="URI reference identifying this occurrence.")
    errors: list[dict[str, object]] | None = Field(
        default=None, description="Optional structured validation errors."
    )
