from __future__ import annotations

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings
from app.models.base import Base
from app.models.enums import DocumentType, ExtractorType, VerificationStatus


def _pg_enum_values(enum_cls: type) -> list[str]:
    return [member.value for member in enum_cls]


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (UniqueConstraint("document_id", "chunk_index"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    page_start: Mapped[int | None] = mapped_column(Integer)
    page_end: Mapped[int | None] = mapped_column(Integer)
    heading_path: Mapped[str | None] = mapped_column(Text)

    char_start: Mapped[int | None] = mapped_column(Integer)
    char_end: Mapped[int | None] = mapped_column(Integer)
    token_count: Mapped[int | None] = mapped_column(Integer)

    text: Mapped[str] = mapped_column(Text, nullable=False)

    # Denormalized metadata for filtering before vector search
    university_id: Mapped[int | None] = mapped_column(
        ForeignKey("universities.id", ondelete="SET NULL")
    )
    program_id: Mapped[int | None] = mapped_column(
        ForeignKey("programs.id", ondelete="SET NULL")
    )
    intake_id: Mapped[int | None] = mapped_column(
        ForeignKey("program_intakes.id", ondelete="SET NULL")
    )
    admission_year: Mapped[int | None] = mapped_column(Integer)
    document_type: Mapped[DocumentType | None] = mapped_column(
        Enum(
            DocumentType,
            name="document_type",
            native_enum=True,
            create_type=False,
            values_callable=_pg_enum_values,
        )
    )
    language: Mapped[str | None] = mapped_column(String(8))

    document: Mapped["Document"] = relationship(back_populates="chunks")
    embeddings: Mapped[list[ChunkEmbedding]] = relationship(back_populates="chunk")
    extracted_facts: Mapped[list[ExtractedFact]] = relationship(back_populates="chunk")


class ChunkEmbedding(Base):
    __tablename__ = "chunk_embeddings"

    chunk_id: Mapped[int] = mapped_column(
        ForeignKey("document_chunks.id", ondelete="CASCADE"), primary_key=True
    )
    embedding_model: Mapped[str] = mapped_column(String(128), primary_key=True)
    embedding: Mapped[list[float]] = mapped_column(
        Vector(settings.embedding_dimensions), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )

    chunk: Mapped[DocumentChunk] = relationship(back_populates="embeddings")


class ExtractedFact(Base):
    __tablename__ = "extracted_facts"

    id: Mapped[int] = mapped_column(primary_key=True)
    intake_id: Mapped[int] = mapped_column(
        ForeignKey("program_intakes.id", ondelete="CASCADE"), nullable=False
    )

    field_name: Mapped[str] = mapped_column(String(128), nullable=False)
    value_json: Mapped[dict] = mapped_column(JSONB, nullable=False)

    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL")
    )
    chunk_id: Mapped[int | None] = mapped_column(
        ForeignKey("document_chunks.id", ondelete="SET NULL")
    )

    evidence_text: Mapped[str | None] = mapped_column(Text)

    extractor_type: Mapped[ExtractorType] = mapped_column(
        Enum(
            ExtractorType,
            name="extractor_type",
            native_enum=True,
            create_type=False,
            values_callable=_pg_enum_values,
        ),
        nullable=False,
    )
    extractor_name: Mapped[str | None] = mapped_column(String(128))
    extractor_version: Mapped[str | None] = mapped_column(String(64))

    confidence: Mapped[float | None] = mapped_column()
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(
            VerificationStatus,
            name="verification_status",
            native_enum=True,
            create_type=False,
            values_callable=_pg_enum_values,
        ),
        default=VerificationStatus.PENDING,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )

    intake: Mapped["ProgramIntake"] = relationship(back_populates="extracted_facts")
    document: Mapped["Document | None"] = relationship(back_populates="extracted_facts")
    chunk: Mapped[DocumentChunk | None] = relationship(back_populates="extracted_facts")
