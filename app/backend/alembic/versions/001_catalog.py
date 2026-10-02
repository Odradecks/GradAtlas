"""catalog: universities through program_intakes

Revision ID: 001
Revises:
Create Date: 2026-09-19

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

intake_status = postgresql.ENUM(
    "published",
    "tbd",
    "suspended",
    "closed",
    name="intake_status",
    create_type=True,
)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    intake_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "universities",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("name_local", sa.String(length=255), nullable=True),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("city", sa.String(length=128), nullable=True),
        sa.Column("website_url", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "university_aliases",
        sa.Column("university_id", sa.BigInteger(), nullable=False),
        sa.Column("alias", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["university_id"], ["universities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("university_id", "alias"),
        sa.UniqueConstraint("university_id", "alias"),
    )

    op.create_table(
        "departments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("university_id", sa.BigInteger(), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("name_local", sa.String(length=255), nullable=True),
        sa.Column("website_url", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["university_id"], ["universities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("university_id", "name_en"),
    )

    op.create_table(
        "fields",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "programs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("department_id", sa.BigInteger(), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("name_local", sa.String(length=255), nullable=True),
        sa.Column("degree_type", sa.String(length=64), nullable=True),
        sa.Column("duration_months", sa.Integer(), nullable=True),
        sa.Column("official_url", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("department_id", "slug"),
    )

    op.create_table(
        "program_fields",
        sa.Column("program_id", sa.BigInteger(), nullable=False),
        sa.Column("field_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["field_id"], ["fields.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("program_id", "field_id"),
    )

    op.create_table(
        "program_intakes",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("program_id", sa.BigInteger(), nullable=False),
        sa.Column("admission_year", sa.Integer(), nullable=False),
        sa.Column("entry_month", sa.Integer(), nullable=False),
        sa.Column("intake_label", sa.String(length=64), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "published",
                "tbd",
                "suspended",
                "closed",
                name="intake_status",
                create_type=False,
            ),
            server_default="tbd",
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("program_id", "admission_year", "entry_month"),
    )

    op.create_index(
        "ix_program_intakes_program_year",
        "program_intakes",
        ["program_id", "admission_year"],
    )


def downgrade() -> None:
    op.drop_index("ix_program_intakes_program_year", table_name="program_intakes")
    op.drop_table("program_intakes")
    op.drop_table("program_fields")
    op.drop_table("programs")
    op.drop_table("fields")
    op.drop_table("departments")
    op.drop_table("university_aliases")
    op.drop_table("universities")
    intake_status.drop(op.get_bind(), checkfirst=True)
