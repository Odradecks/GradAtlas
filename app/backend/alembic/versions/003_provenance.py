"""provenance: sources through documents

Revision ID: 003
Revises: 002
Create Date: 2026-09-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

source_type = postgresql.ENUM(
    "admission_guideline",
    "program_page",
    "faq",
    "curriculum",
    "department_page",
    "lab_page",
    "other",
    name="source_type",
    create_type=True,
)
document_type = postgresql.ENUM(
    "admission_guideline",
    "program_page",
    "faq",
    "curriculum",
    "department_page",
    "lab_page",
    "other",
    name="document_type",
    create_type=True,
)


def _enum(name: str, *values: str) -> postgresql.ENUM:
    return postgresql.ENUM(*values, name=name, create_type=False)


def upgrade() -> None:
    source_type.create(op.get_bind(), checkfirst=True)
    document_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "sources",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("university_id", sa.BigInteger(), nullable=True),
        sa.Column("department_id", sa.BigInteger(), nullable=True),
        sa.Column("program_id", sa.BigInteger(), nullable=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column(
            "source_type",
            _enum(
                "source_type",
                "admission_guideline",
                "program_page",
                "faq",
                "curriculum",
                "department_page",
                "lab_page",
                "other",
            ),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column("last_crawled_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["university_id"], ["universities.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["department_id"], ["departments.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "source_snapshots",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.BigInteger(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("content_type", sa.String(length=128), nullable=True),
        sa.Column("etag", sa.String(length=255), nullable=True),
        sa.Column("last_modified", sa.String(length=255), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", "content_hash"),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("source_snapshot_id", sa.BigInteger(), nullable=False),
        sa.Column("university_id", sa.BigInteger(), nullable=True),
        sa.Column("department_id", sa.BigInteger(), nullable=True),
        sa.Column("program_id", sa.BigInteger(), nullable=True),
        sa.Column("intake_id", sa.BigInteger(), nullable=True),
        sa.Column("title", sa.String(length=512), nullable=True),
        sa.Column(
            "document_type",
            _enum(
                "document_type",
                "admission_guideline",
                "program_page",
                "faq",
                "curriculum",
                "department_page",
                "lab_page",
                "other",
            ),
            nullable=False,
        ),
        sa.Column("language", sa.String(length=8), nullable=True),
        sa.Column("admission_year", sa.Integer(), nullable=True),
        sa.Column("mime_type", sa.String(length=128), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["source_snapshot_id"], ["source_snapshots.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["university_id"], ["universities.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["department_id"], ["departments.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["intake_id"], ["program_intakes.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("documents")
    op.drop_table("source_snapshots")
    op.drop_table("sources")
    document_type.drop(op.get_bind(), checkfirst=True)
    source_type.drop(op.get_bind(), checkfirst=True)
