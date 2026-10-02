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
from app.models.enums import IntakeStatus


class University(Base, TimestampMixin):
    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    name_local: Mapped[str | None] = mapped_column(String(255))
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    city: Mapped[str | None] = mapped_column(String(128))
    website_url: Mapped[str | None] = mapped_column(Text)

    aliases: Mapped[list[UniversityAlias]] = relationship(back_populates="university")
    departments: Mapped[list[Department]] = relationship(back_populates="university")
    sources: Mapped[list["Source"]] = relationship(back_populates="university")
    documents: Mapped[list["Document"]] = relationship(back_populates="university")


class UniversityAlias(Base):
    __tablename__ = "university_aliases"
    __table_args__ = (UniqueConstraint("university_id", "alias"),)

    university_id: Mapped[int] = mapped_column(
        ForeignKey("universities.id", ondelete="CASCADE"), primary_key=True
    )
    alias: Mapped[str] = mapped_column(String(255), primary_key=True)

    university: Mapped[University] = relationship(back_populates="aliases")


class Department(Base):
    __tablename__ = "departments"
    __table_args__ = (UniqueConstraint("university_id", "name_en"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int] = mapped_column(
        ForeignKey("universities.id", ondelete="CASCADE"), nullable=False
    )
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    name_local: Mapped[str | None] = mapped_column(String(255))
    website_url: Mapped[str | None] = mapped_column(Text)

    university: Mapped[University] = relationship(back_populates="departments")
    programs: Mapped[list[Program]] = relationship(back_populates="department")
    sources: Mapped[list["Source"]] = relationship(back_populates="department")
    documents: Mapped[list["Document"]] = relationship(back_populates="department")


class Program(Base, TimestampMixin):
    __tablename__ = "programs"
    __table_args__ = (UniqueConstraint("department_id", "slug"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id", ondelete="CASCADE"), nullable=False
    )
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    name_local: Mapped[str | None] = mapped_column(String(255))
    degree_type: Mapped[str | None] = mapped_column(String(64))
    duration_months: Mapped[int | None] = mapped_column(Integer)
    official_url: Mapped[str | None] = mapped_column(Text)
    ingestion_priority: Mapped[str | None] = mapped_column(String(8))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    department: Mapped[Department] = relationship(back_populates="programs")
    fields: Mapped[list[ProgramField]] = relationship(back_populates="program")
    intakes: Mapped[list[ProgramIntake]] = relationship(back_populates="program")
    sources: Mapped[list["Source"]] = relationship(back_populates="program")
    documents: Mapped[list["Document"]] = relationship(back_populates="program")


class Field(Base):
    __tablename__ = "fields"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)

    programs: Mapped[list[ProgramField]] = relationship(back_populates="field")


class ProgramField(Base):
    __tablename__ = "program_fields"

    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id", ondelete="CASCADE"), primary_key=True
    )
    field_id: Mapped[int] = mapped_column(
        ForeignKey("fields.id", ondelete="CASCADE"), primary_key=True
    )

    program: Mapped[Program] = relationship(back_populates="fields")
    field: Mapped[Field] = relationship(back_populates="programs")


class ProgramIntake(Base, TimestampMixin):
    __tablename__ = "program_intakes"
    __table_args__ = (
        UniqueConstraint("program_id", "admission_year", "entry_month"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id", ondelete="CASCADE"), nullable=False
    )
    admission_year: Mapped[int] = mapped_column(Integer, nullable=False)
    entry_month: Mapped[int] = mapped_column(Integer, nullable=False)
    intake_label: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[IntakeStatus] = mapped_column(
        Enum(
            IntakeStatus,
            name="intake_status",
            native_enum=True,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=IntakeStatus.TBD,
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column()
    last_verified_at: Mapped[datetime | None] = mapped_column()

    program: Mapped[Program] = relationship(back_populates="intakes")
    admission_requirement: Mapped["AdmissionRequirement | None"] = relationship(
        back_populates="intake", uselist=False
    )
    language_requirements: Mapped[list["LanguageRequirement"]] = relationship(
        back_populates="intake"
    )
    tuition_fees: Mapped[list["TuitionFee"]] = relationship(back_populates="intake")
    application_rounds: Mapped[list["ApplicationRound"]] = relationship(
        back_populates="intake"
    )
    documents: Mapped[list["Document"]] = relationship(back_populates="intake")
    extracted_facts: Mapped[list["ExtractedFact"]] = relationship(
        back_populates="intake"
    )
