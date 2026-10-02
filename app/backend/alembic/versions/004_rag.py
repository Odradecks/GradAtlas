"""rag: chunks, embeddings, extracted facts

Revision ID: 004
Revises: 003
Create Date: 2026-09-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

extractor_type = postgresql.ENUM(
    "manual",
    "rule",
    "llm",
    name="extractor_type",
    create_type=True,
)
verification_status = postgresql.ENUM(
    "pending",
    "verified",
    "rejected",
    "superseded",
    name="verification_status",
    create_type=True,
)


def _enum(name: str, *values: str) -> postgresql.ENUM:
    return postgresql.ENUM(*values, name=name, create_type=False)


def upgrade() -> None:
    extractor_type.create(op.get_bind(), checkfirst=True)
    verification_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("document_id", sa.BigInteger(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("page_start", sa.Integer(), nullable=True),
        sa.Column("page_end", sa.Integer(), nullable=True),
        sa.Column("heading_path", sa.Text(), nullable=True),
        sa.Column("char_start", sa.Integer(), nullable=True),
        sa.Column("char_end", sa.Integer(), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("university_id", sa.BigInteger(), nullable=True),
        sa.Column("program_id", sa.BigInteger(), nullable=True),
        sa.Column("intake_id", sa.BigInteger(), nullable=True),
        sa.Column("admission_year", sa.Integer(), nullable=True),
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
            nullable=True,
        ),
        sa.Column("language", sa.String(length=8), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["university_id"], ["universities.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["intake_id"], ["program_intakes.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id", "chunk_index"),
    )

    op.create_table(
        "chunk_embeddings",
        sa.Column("chunk_id", sa.BigInteger(), nullable=False),
        sa.Column("embedding_model", sa.String(length=128), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["chunk_id"], ["document_chunks.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("chunk_id", "embedding_model"),
    )

    op.create_table(
        "extracted_facts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("intake_id", sa.BigInteger(), nullable=False),
        sa.Column("field_name", sa.String(length=128), nullable=False),
        sa.Column(
            "value_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("document_id", sa.BigInteger(), nullable=True),
        sa.Column("chunk_id", sa.BigInteger(), nullable=True),
        sa.Column("evidence_text", sa.Text(), nullable=True),
        sa.Column(
            "extractor_type",
            _enum("extractor_type", "manual", "rule", "llm"),
            nullable=False,
        ),
        sa.Column("extractor_name", sa.String(length=128), nullable=True),
        sa.Column("extractor_version", sa.String(length=64), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "verification_status",
            _enum(
                "verification_status",
                "pending",
                "verified",
                "rejected",
                "superseded",
            ),
            server_default="pending",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["intake_id"], ["program_intakes.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["chunk_id"], ["document_chunks.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("extracted_facts")
    op.drop_table("chunk_embeddings")
    op.drop_table("document_chunks")
    verification_status.drop(op.get_bind(), checkfirst=True)
    extractor_type.drop(op.get_bind(), checkfirst=True)
