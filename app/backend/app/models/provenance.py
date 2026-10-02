from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import DocumentType, SourceType

def _pg_enum_values(enum_cls: type) -> list[str]:
    return [member.value for member in enum_cls]


class Source(Base, TimestampMixin):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int | None] = mapped_column(
        ForeignKey("universities.id", ondelete="SET NULL")
    )
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL")
    )
    program_id: Mapped[int | None] = mapped_column(
        ForeignKey("programs.id", ondelete="SET NULL")
    )

    url: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[SourceType] = mapped_column(
        Enum(
            SourceType,
            name="source_type",
            native_enum=True,
            values_callable=_pg_enum_values,
        ),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_crawled_at: Mapped[datetime | None] = mapped_column()

    university: Mapped["University | None"] = relationship(back_populates="sources")
    department: Mapped["Department | None"] = relationship(back_populates="sources")
    program: Mapped["Program | None"] = relationship(back_populates="sources")
    snapshots: Mapped[list[SourceSnapshot]] = relationship(back_populates="source")


class SourceSnapshot(Base):
    __tablename__ = "source_snapshots"
    __table_args__ = (UniqueConstraint("source_id", "content_hash"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )

    fetched_at: Mapped[datetime] = mapped_column(nullable=False)

    http_status: Mapped[int | None] = mapped_column(Integer)
    content_type: Mapped[str | None] = mapped_column(String(128))

    etag: Mapped[str | None] = mapped_column(String(255))
    last_modified: Mapped[str | None] = mapped_column(String(255))
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    storage_path: Mapped[str | None] = mapped_column(Text)

    source: Mapped[Source] = relationship(back_populates="snapshots")
    documents: Mapped[list[Document]] = relationship(back_populates="source_snapshot")


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (UniqueConstraint("source_snapshot_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source_snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("source_snapshots.id", ondelete="CASCADE"), nullable=False
    )

    university_id: Mapped[int | None] = mapped_column(
        ForeignKey("universities.id", ondelete="SET NULL")
    )
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL")
    )
    program_id: Mapped[int | None] = mapped_column(
        ForeignKey("programs.id", ondelete="SET NULL")
    )
    intake_id: Mapped[int | None] = mapped_column(
        ForeignKey("program_intakes.id", ondelete="SET NULL")
    )

    title: Mapped[str | None] = mapped_column(String(512))
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(
            DocumentType,
            name="document_type",
            native_enum=True,
            values_callable=_pg_enum_values,
        ),
        nullable=False,
    )
    language: Mapped[str | None] = mapped_column(String(8))
    admission_year: Mapped[int | None] = mapped_column(Integer)

    mime_type: Mapped[str | None] = mapped_column(String(128))
    raw_text: Mapped[str | None] = mapped_column(Text)
    page_count: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )

    source_snapshot: Mapped[SourceSnapshot] = relationship(back_populates="documents")
    university: Mapped["University | None"] = relationship(back_populates="documents")
    department: Mapped["Department | None"] = relationship(back_populates="documents")
    program: Mapped["Program | None"] = relationship(back_populates="documents")
    intake: Mapped["ProgramIntake | None"] = relationship(back_populates="documents")
    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="document")
    extracted_facts: Mapped[list["ExtractedFact"]] = relationship(
        back_populates="document"
    )
