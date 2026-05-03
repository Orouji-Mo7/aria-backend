"""create observations table

Revision ID: 0002_create_observations
Revises: 0001_create_patients
Create Date: 2026-04-28

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_create_observations"
down_revision: str | None = "0001_create_patients"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "observations",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("patient_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("code_system", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("code_display", sa.String(length=255), nullable=False),
        sa.Column("value_numeric", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column("value_unit", sa.String(length=32), nullable=False),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "final",
                "preliminary",
                "amended",
                "entered_in_error",
                name="observation_status",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("recorded_by", sa.String(length=128), nullable=True),
        sa.Column("note", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_observations")),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            name=op.f("fk_observations_patient_id_patients"),
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        op.f("ix_observations_patient_id"),
        "observations",
        ["patient_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_observations_code"),
        "observations",
        ["code"],
        unique=False,
    )
    op.create_index(
        op.f("ix_observations_effective_at"),
        "observations",
        ["effective_at"],
        unique=False,
    )
    op.create_index(
        "ix_observations_patient_effective",
        "observations",
        ["patient_id", sa.text("effective_at DESC")],
        unique=False,
    )
    op.create_index(
        "ix_observations_patient_code_effective",
        "observations",
        ["patient_id", "code", sa.text("effective_at DESC")],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_observations_patient_code_effective", table_name="observations")
    op.drop_index("ix_observations_patient_effective", table_name="observations")
    op.drop_index(op.f("ix_observations_effective_at"), table_name="observations")
    op.drop_index(op.f("ix_observations_code"), table_name="observations")
    op.drop_index(op.f("ix_observations_patient_id"), table_name="observations")
    op.drop_table("observations")
