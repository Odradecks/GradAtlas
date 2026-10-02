"""admissions: requirements through entrance exams

Revision ID: 002
Revises: 001
Create Date: 2026-09-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

requirement_status = postgresql.ENUM(
    "required",
    "recommended",
    "optional",
    "not_required",
    "not_stated",
    "unknown",
    name="requirement_status",
    create_type=True,
)
gpa_requirement_type = postgresql.ENUM(
    "minimum",
    "recommended",
    "range",
    "percentile",
    "not_stated",
    "unknown",
    name="gpa_requirement_type",
    create_type=True,
)
language_test_type = postgresql.ENUM(
    "ielts",
    "toefl_ibt",
    "toefl_pbt",
    "cambridge",
    "pte",
    "duolingo",
    "other",
    name="language_test_type",
    create_type=True,
)
student_category = postgresql.ENUM(
    "all",
    "eu_eea",
    "non_eu",
    "domestic",
    "international",
    name="student_category",
    create_type=True,
)
billing_period = postgresql.ENUM(
    "per_year",
    "per_semester",
    "per_term",
    "total_program",
    name="billing_period",
    create_type=True,
)


def _enum(name: str, *values: str) -> postgresql.ENUM:
    return postgresql.ENUM(*values, name=name, create_type=False)


def upgrade() -> None:
    requirement_status.create(op.get_bind(), checkfirst=True)
    gpa_requirement_type.create(op.get_bind(), checkfirst=True)
    language_test_type.create(op.get_bind(), checkfirst=True)
    student_category.create(op.get_bind(), checkfirst=True)
    billing_period.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "admission_requirements",
        sa.Column("intake_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "gpa_requirement_type",
            _enum(
                "gpa_requirement_type",
                "minimum",
                "recommended",
                "range",
                "percentile",
                "not_stated",
                "unknown",
            ),
            nullable=True,
        ),
        sa.Column("gpa_min", sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column("gpa_scale", sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column("gpa_note", sa.Text(), nullable=True),
        sa.Column(
            "gre_requirement",
            _enum(
                "requirement_status",
                "required",
                "recommended",
                "optional",
                "not_required",
                "not_stated",
                "unknown",
            ),
            server_default="unknown",
            nullable=False,
        ),
        sa.Column("gre_note", sa.Text(), nullable=True),
        sa.Column("recommendation_letter_count", sa.Integer(), nullable=True),
        sa.Column(
            "professor_contact_status",
            _enum(
                "requirement_status",
                "required",
                "recommended",
                "optional",
                "not_required",
                "not_stated",
                "unknown",
            ),
            server_default="unknown",
            nullable=False,
        ),
        sa.Column(
            "entrance_exam_status",
            _enum(
                "requirement_status",
                "required",
                "recommended",
                "optional",
                "not_required",
                "not_stated",
                "unknown",
            ),
            server_default="unknown",
            nullable=False,
        ),
        sa.Column(
            "interview_status",
            _enum(
                "requirement_status",
                "required",
                "recommended",
                "optional",
                "not_required",
                "not_stated",
                "unknown",
            ),
            server_default="unknown",
            nullable=False,
        ),
        sa.Column("extra", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["intake_id"], ["program_intakes.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("intake_id"),
    )

    op.create_table(
        "language_requirements",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("intake_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "test_type",
            _enum(
                "language_test_type",
                "ielts",
                "toefl_ibt",
                "toefl_pbt",
                "cambridge",
                "pte",
                "duolingo",
                "other",
            ),
            nullable=False,
        ),
        sa.Column("minimum_overall", sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column("minimum_reading", sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column("minimum_writing", sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column("minimum_listening", sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column("minimum_speaking", sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column(
            "requirement_status",
            _enum(
                "requirement_status",
                "required",
                "recommended",
                "optional",
                "not_required",
                "not_stated",
                "unknown",
            ),
            server_default="unknown",
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["intake_id"], ["program_intakes.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "tuition_fees",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("intake_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "student_category",
            _enum(
                "student_category",
                "all",
                "eu_eea",
                "non_eu",
                "domestic",
                "international",
            ),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column(
            "billing_period",
            _enum(
                "billing_period",
                "per_year",
                "per_semester",
                "per_term",
                "total_program",
            ),
            nullable=False,
        ),
        sa.Column("mandatory_fee", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column(
            "normalized_annual_eur", sa.Numeric(precision=12, scale=2), nullable=True
        ),
        sa.Column(
            "normalization_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["intake_id"], ["program_intakes.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "application_rounds",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("intake_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("applicant_group", sa.String(length=32), nullable=True),
        sa.Column("opens_on", sa.Date(), nullable=True),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("exam_date", sa.Date(), nullable=True),
        sa.Column("result_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["intake_id"], ["program_intakes.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "entrance_exam_subjects",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("round_id", sa.BigInteger(), nullable=False),
        sa.Column("subject", sa.String(length=128), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["round_id"], ["application_rounds.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("entrance_exam_subjects")
    op.drop_table("application_rounds")
    op.drop_table("tuition_fees")
    op.drop_table("language_requirements")
    op.drop_table("admission_requirements")
    billing_period.drop(op.get_bind(), checkfirst=True)
    student_category.drop(op.get_bind(), checkfirst=True)
    language_test_type.drop(op.get_bind(), checkfirst=True)
    gpa_requirement_type.drop(op.get_bind(), checkfirst=True)
    requirement_status.drop(op.get_bind(), checkfirst=True)
