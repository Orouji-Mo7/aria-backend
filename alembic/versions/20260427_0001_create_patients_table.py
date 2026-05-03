"""create patients table

Revision ID: 0001_create_patients
Revises:
Create Date: 2026-04-27

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_create_patients"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "patients",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("mrn", sa.String(length=64), nullable=False),
        sa.Column("given_name", sa.String(length=128), nullable=False),
        sa.Column("family_name", sa.String(length=128), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column(
            "gender",
            sa.Enum(
                "male",
                "female",
                "other",
                "unknown",
                name="patient_gender",
                native_enum=False,
                length=16,
            ),
            nullable=False,
        ),
        sa.Column("admission_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("room_number", sa.String(length=32), nullable=True),
        sa.Column("station", sa.String(length=64), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "discharged",
                name="patient_status",
                native_enum=False,
                length=16,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_patients")),
        sa.UniqueConstraint("mrn", name=op.f("uq_patients_mrn")),
    )
    op.create_index(op.f("ix_patients_mrn"), "patients", ["mrn"], unique=True)
    op.create_index(op.f("ix_patients_status"), "patients", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_patients_status"), table_name="patients")
    op.drop_index(op.f("ix_patients_mrn"), table_name="patients")
    op.drop_table("patients")
