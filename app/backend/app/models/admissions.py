from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import (
    BillingPeriod,
    GpaRequirementType,
    LanguageTestType,
    RequirementStatus,
    StudentCategory,
)

_enum_values = lambda enum_cls: [member.value for member in enum_cls]


class AdmissionRequirement(Base):
    __tablename__ = "admission_requirements"

    intake_id: Mapped[int] = mapped_column(
        ForeignKey("program_intakes.id", ondelete="CASCADE"), primary_key=True
    )

    gpa_requirement_type: Mapped[GpaRequirementType | None] = mapped_column(
        Enum(
            GpaRequirementType,
            name="gpa_requirement_type",
            native_enum=True,
            values_callable=_enum_values,
        ),
        default=GpaRequirementType.UNKNOWN,
    )
    gpa_min: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    gpa_scale: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    gpa_note: Mapped[str | None] = mapped_column(Text)

    gre_requirement: Mapped[RequirementStatus] = mapped_column(
        Enum(
            RequirementStatus,
            name="requirement_status",
            native_enum=True,
            values_callable=_enum_values,
        ),
        default=RequirementStatus.UNKNOWN,
        nullable=False,
    )
    gre_note: Mapped[str | None] = mapped_column(Text)
    recommendation_letter_count: Mapped[int | None] = mapped_column(Integer)

    professor_contact_status: Mapped[RequirementStatus] = mapped_column(
        Enum(
            RequirementStatus,
            name="requirement_status",
            native_enum=True,
            create_type=False,
            values_callable=_enum_values,
        ),
        default=RequirementStatus.UNKNOWN,
        nullable=False,
    )
    entrance_exam_status: Mapped[RequirementStatus] = mapped_column(
        Enum(
            RequirementStatus,
            name="requirement_status",
            native_enum=True,
            create_type=False,
            values_callable=_enum_values,
        ),
        default=RequirementStatus.UNKNOWN,
        nullable=False,
    )
    interview_status: Mapped[RequirementStatus] = mapped_column(
        Enum(
            RequirementStatus,
            name="requirement_status",
            native_enum=True,
            create_type=False,
            values_callable=_enum_values,
        ),
        default=RequirementStatus.UNKNOWN,
        nullable=False,
    )

    extra: Mapped[dict | None] = mapped_column(JSONB)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    intake: Mapped["ProgramIntake"] = relationship(back_populates="admission_requirement")


class LanguageRequirement(Base):
    __tablename__ = "language_requirements"

    id: Mapped[int] = mapped_column(primary_key=True)
    intake_id: Mapped[int] = mapped_column(
        ForeignKey("program_intakes.id", ondelete="CASCADE"), nullable=False
    )
    test_type: Mapped[LanguageTestType] = mapped_column(
        Enum(
            LanguageTestType,
            name="language_test_type",
            native_enum=True,
            values_callable=_enum_values,
        ),
        nullable=False,
    )
    minimum_overall: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    minimum_reading: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    minimum_writing: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    minimum_listening: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    minimum_speaking: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    requirement_status: Mapped[RequirementStatus] = mapped_column(
        Enum(
            RequirementStatus,
            name="requirement_status",
            native_enum=True,
            create_type=False,
            values_callable=_enum_values,
        ),
        default=RequirementStatus.UNKNOWN,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text)

    intake: Mapped["ProgramIntake"] = relationship(back_populates="language_requirements")


class TuitionFee(Base):
    __tablename__ = "tuition_fees"

    id: Mapped[int] = mapped_column(primary_key=True)
    intake_id: Mapped[int] = mapped_column(
        ForeignKey("program_intakes.id", ondelete="CASCADE"), nullable=False
    )
    student_category: Mapped[StudentCategory] = mapped_column(
        Enum(
            StudentCategory,
            name="student_category",
            native_enum=True,
            values_callable=_enum_values,
        ),
        nullable=False,
    )
    amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str | None] = mapped_column(String(3))
    billing_period: Mapped[BillingPeriod] = mapped_column(
        Enum(
            BillingPeriod,
            name="billing_period",
            native_enum=True,
            values_callable=_enum_values,
        ),
        nullable=False,
    )
    mandatory_fee: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    normalized_annual_eur: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    normalization_metadata: Mapped[dict | None] = mapped_column(JSONB)
    notes: Mapped[str | None] = mapped_column(Text)

    intake: Mapped["ProgramIntake"] = relationship(back_populates="tuition_fees")


class ApplicationRound(Base):
    __tablename__ = "application_rounds"

    id: Mapped[int] = mapped_column(primary_key=True)
    intake_id: Mapped[int] = mapped_column(
        ForeignKey("program_intakes.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    applicant_group: Mapped[str | None] = mapped_column(String(32))
    opens_on: Mapped[date | None] = mapped_column(Date)
    deadline: Mapped[date | None] = mapped_column(Date)
    exam_date: Mapped[date | None] = mapped_column(Date)
    result_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)

    intake: Mapped["ProgramIntake"] = relationship(back_populates="application_rounds")
    exam_subjects: Mapped[list["EntranceExamSubject"]] = relationship(back_populates="round")


class EntranceExamSubject(Base):
    __tablename__ = "entrance_exam_subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    round_id: Mapped[int] = mapped_column(
        ForeignKey("application_rounds.id", ondelete="CASCADE"), nullable=False
    )
    subject: Mapped[str] = mapped_column(String(128), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    round: Mapped[ApplicationRound] = relationship(back_populates="exam_subjects")