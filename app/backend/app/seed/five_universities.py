"""
Seed five sample universities with one CS-related master's program each.

Data is illustrative for development; verify against official admission pages before production use.
Run: docker compose run --rm backend python -m app.seed.five_universities
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.admissions import (
    AdmissionRequirement,
    ApplicationRound,
    EntranceExamSubject,
    LanguageRequirement,
    TuitionFee,
)
from app.models.catalog import (
    Department,
    Field,
    Program,
    ProgramField,
    ProgramIntake,
    University,
    UniversityAlias,
)
from app.models.enums import (
    BillingPeriod,
    GpaRequirementType,
    IntakeStatus,
    LanguageTestType,
    RequirementStatus,
    StudentCategory,
)


@dataclass
class LanguageSpec:
    test_type: LanguageTestType
    minimum_overall: Decimal | None = None
    notes: str | None = None


@dataclass
class TuitionSpec:
    student_category: StudentCategory
    amount: Decimal
    currency: str
    billing_period: BillingPeriod
    normalized_annual_eur: Decimal | None = None
    notes: str | None = None


@dataclass
class RoundSpec:
    name: str
    deadline: date | None = None
    opens_on: date | None = None
    exam_date: date | None = None
    applicant_group: str | None = None
    exam_subjects: list[str] = field(default_factory=list)
    notes: str | None = None


@dataclass
class ProgramSpec:
    slug: str
    name_en: str
    degree_type: str
    duration_months: int
    official_url: str
    field_slugs: list[str]
    admission_year: int
    entry_month: int
    intake_label: str
    gre: RequirementStatus
    gre_note: str | None
    recommendation_letters: int | None
    entrance_exam: RequirementStatus
    interview: RequirementStatus
    languages: list[LanguageSpec]
    tuitions: list[TuitionSpec]
    rounds: list[RoundSpec]
    gpa_min: Decimal | None = None
    gpa_note: str | None = None


@dataclass
class UniversitySpec:
    slug: str
    name_en: str
    name_local: str | None
    country_code: str
    city: str
    website_url: str
    aliases: list[str]
    department_name_en: str
    department_url: str | None
    program: ProgramSpec


SAMPLES: list[UniversitySpec] = [
    UniversitySpec(
        slug="stanford-university",
        name_en="Stanford University",
        name_local=None,
        country_code="US",
        city="Stanford",
        website_url="https://www.stanford.edu",
        aliases=["Stanford", "Leland Stanford Junior University"],
        department_name_en="Department of Computer Science",
        department_url="https://cs.stanford.edu",
        program=ProgramSpec(
            slug="ms-computer-science",
            name_en="MS Computer Science",
            degree_type="MS",
            duration_months=24,
            official_url="https://cs.stanford.edu/admissions/masters",
            field_slugs=["cs"],
            admission_year=2027,
            entry_month=9,
            intake_label="Fall 2027",
            gre=RequirementStatus.OPTIONAL,
            gre_note="Policy varies by year; check CS admissions page.",
            recommendation_letters=3,
            entrance_exam=RequirementStatus.NOT_REQUIRED,
            interview=RequirementStatus.NOT_STATED,
            languages=[
                LanguageSpec(
                    LanguageTestType.TOEFL_IBT,
                    Decimal("100"),
                    notes="Minimum iBT score; department may publish subscores.",
                ),
            ],
            tuitions=[
                TuitionSpec(
                    StudentCategory.INTERNATIONAL,
                    Decimal("62484"),
                    "USD",
                    BillingPeriod.PER_YEAR,
                    Decimal("58000"),
                    notes="Approximate graduate tuition; verify Stanford budget site.",
                ),
            ],
            rounds=[
                RoundSpec(
                    name="Graduate application deadline",
                    deadline=date(2026, 12, 2),
                    applicant_group="all",
                    notes="Typical CS MS timeline; confirm for 2027 cycle.",
                ),
            ],
            gpa_note="Strong academic record expected; no fixed public minimum.",
        ),
    ),
    UniversitySpec(
        slug="university-of-copenhagen",
        name_en="University of Copenhagen",
        name_local="Københavns Universitet",
        country_code="DK",
        city="Copenhagen",
        website_url="https://www.ku.dk",
        aliases=["UCPH", "KU"],
        department_name_en="Department of Computer Science",
        department_url="https://di.ku.dk/english/",
        program=ProgramSpec(
            slug="msc-computer-science",
            name_en="MSc in Computer Science",
            degree_type="MSc",
            duration_months=24,
            official_url="https://studies.ku.dk/masters/computer-science",
            field_slugs=["cs"],
            admission_year=2027,
            entry_month=9,
            intake_label="September 2027",
            gre=RequirementStatus.NOT_REQUIRED,
            gre_note=None,
            recommendation_letters=None,
            entrance_exam=RequirementStatus.NOT_REQUIRED,
            interview=RequirementStatus.NOT_STATED,
            languages=[
                LanguageSpec(
                    LanguageTestType.IELTS,
                    Decimal("6.5"),
                    notes="English proficiency required for English-taught MSc.",
                ),
            ],
            tuitions=[
                TuitionSpec(
                    StudentCategory.EU_EEA,
                    Decimal("0"),
                    "DKK",
                    BillingPeriod.PER_YEAR,
                    Decimal("0"),
                    notes="EU/EEA citizens often exempt from tuition; verify current law.",
                ),
                TuitionSpec(
                    StudentCategory.NON_EU,
                    Decimal("102000"),
                    "DKK",
                    BillingPeriod.PER_YEAR,
                    Decimal("13700"),
                    notes="Non-EU tuition approx.; verify studies.ku.dk for exact year.",
                ),
            ],
            rounds=[
                RoundSpec(
                    name="Application deadline",
                    deadline=date(2027, 1, 15),
                    applicant_group="non_eu",
                ),
                RoundSpec(
                    name="Application deadline",
                    deadline=date(2027, 3, 1),
                    applicant_group="eu_eea",
                ),
            ],
        ),
    ),
    UniversitySpec(
        slug="technical-university-of-munich",
        name_en="Technical University of Munich",
        name_local="Technische Universität München",
        country_code="DE",
        city="Munich",
        website_url="https://www.tum.de",
        aliases=["TUM", "TU München"],
        department_name_en="Department of Informatics",
        department_url="https://www.in.tum.de",
        program=ProgramSpec(
            slug="msc-informatics",
            name_en="MSc Informatics",
            degree_type="MSc",
            duration_months=24,
            official_url="https://www.in.tum.de/in/fuer-studierende/master/informatics/",
            field_slugs=["cs"],
            admission_year=2027,
            entry_month=10,
            intake_label="Winter semester 2027/28",
            gre=RequirementStatus.NOT_REQUIRED,
            gre_note=None,
            recommendation_letters=2,
            entrance_exam=RequirementStatus.NOT_REQUIRED,
            interview=RequirementStatus.OPTIONAL,
            languages=[
                LanguageSpec(
                    LanguageTestType.IELTS,
                    Decimal("6.5"),
                    notes="English-taught Informatics track.",
                ),
                LanguageSpec(
                    LanguageTestType.TOEFL_IBT,
                    Decimal("88"),
                    notes="Alternative English test.",
                ),
            ],
            tuitions=[
                TuitionSpec(
                    StudentCategory.NON_EU,
                    Decimal("6000"),
                    "EUR",
                    BillingPeriod.PER_SEMESTER,
                    Decimal("12000"),
                    notes="Non-EU tuition per semester; plus semester fees.",
                ),
                TuitionSpec(
                    StudentCategory.EU_EEA,
                    Decimal("150"),
                    "EUR",
                    BillingPeriod.PER_SEMESTER,
                    Decimal("300"),
                    notes="Semester contribution only for many EU students.",
                ),
            ],
            rounds=[
                RoundSpec(
                    name="Winter semester application",
                    deadline=date(2027, 5, 31),
                    applicant_group="non_eu",
                ),
            ],
        ),
    ),
    UniversitySpec(
        slug="university-of-helsinki",
        name_en="University of Helsinki",
        name_local="Helsingin yliopisto",
        country_code="FI",
        city="Helsinki",
        website_url="https://www.helsinki.fi",
        aliases=["UH"],
        department_name_en="Department of Computer Science",
        department_url="https://www.helsinki.fi/en/faculty-science/faculty/computer-science",
        program=ProgramSpec(
            slug="msc-computer-science",
            name_en="Master's Programme in Computer Science",
            degree_type="MSc",
            duration_months=24,
            official_url="https://studies.helsinki.fi/en/programmes/master/computer-science",
            field_slugs=["cs"],
            admission_year=2027,
            entry_month=9,
            intake_label="Autumn 2027",
            gre=RequirementStatus.NOT_REQUIRED,
            gre_note=None,
            recommendation_letters=None,
            entrance_exam=RequirementStatus.NOT_REQUIRED,
            interview=RequirementStatus.NOT_STATED,
            languages=[
                LanguageSpec(
                    LanguageTestType.IELTS,
                    Decimal("6.5"),
                    notes="English proficiency for English-taught programme.",
                ),
            ],
            tuitions=[
                TuitionSpec(
                    StudentCategory.NON_EU,
                    Decimal("15000"),
                    "EUR",
                    BillingPeriod.PER_YEAR,
                    Decimal("15000"),
                    notes="Non-EU/EEA tuition fee master's; verify for intake year.",
                ),
                TuitionSpec(
                    StudentCategory.EU_EEA,
                    Decimal("0"),
                    "EUR",
                    BillingPeriod.PER_YEAR,
                    Decimal("0"),
                    notes="No tuition for EU/EEA citizens.",
                ),
            ],
            rounds=[
                RoundSpec(
                    name="Application period ends",
                    deadline=date(2027, 1, 5),
                    applicant_group="all",
                ),
            ],
        ),
    ),
    UniversitySpec(
        slug="university-of-tokyo",
        name_en="The University of Tokyo",
        name_local="東京大学",
        country_code="JP",
        city="Tokyo",
        website_url="https://www.u-tokyo.ac.jp",
        aliases=["UTokyo", "Todai"],
        department_name_en="Department of Creative Informatics",
        department_url="https://www.creative-informatics.jp",
        program=ProgramSpec(
            slug="msc-creative-informatics",
            name_en="Master of Information Science and Technology (Creative Informatics)",
            degree_type="Master",
            duration_months=24,
            official_url="https://www.creative-informatics.jp/admissions/",
            field_slugs=["cs", "ai"],
            admission_year=2027,
            entry_month=4,
            intake_label="April 2027 intake",
            gre=RequirementStatus.NOT_STATED,
            gre_note="Graduate School of IST policies apply.",
            recommendation_letters=2,
            entrance_exam=RequirementStatus.REQUIRED,
            interview=RequirementStatus.OPTIONAL,
            languages=[
                LanguageSpec(
                    LanguageTestType.TOEFL_IBT,
                    Decimal("90"),
                    notes="English programs may require TOEFL/IELTS; verify guideline.",
                ),
                LanguageSpec(
                    LanguageTestType.IELTS,
                    Decimal("6.5"),
                ),
            ],
            tuitions=[
                TuitionSpec(
                    StudentCategory.INTERNATIONAL,
                    Decimal("535800"),
                    "JPY",
                    BillingPeriod.PER_YEAR,
                    Decimal("3200"),
                    notes="National university standard annual tuition; plus admission fees.",
                ),
            ],
            rounds=[
                RoundSpec(
                    name="Summer entrance examination",
                    deadline=date(2026, 7, 7),
                    exam_date=date(2026, 8, 28),
                    applicant_group="all",
                    exam_subjects=["Mathematics", "Programming", "Specialized subjects", "Interview"],
                    notes="Exam structure summarized; see admission guideline for details.",
                ),
            ],
            gpa_note="Bachelor's degree required; screening includes academic record.",
        ),
    ),
]


def ensure_fields(session: Session) -> dict[str, Field]:
    specs = [
        ("cs", "Computer Science"),
        ("ai", "Artificial Intelligence"),
        ("data-science", "Data Science"),
    ]
    out: dict[str, Field] = {}
    for slug, name in specs:
        row = session.scalar(select(Field).where(Field.slug == slug))
        if row is None:
            row = Field(slug=slug, name=name)
            session.add(row)
            session.flush()
        out[slug] = row
    return out


def seed_one(session: Session, spec: UniversitySpec, fields: dict[str, Field]) -> bool:
    existing = session.scalar(select(University).where(University.slug == spec.slug))
    if existing is not None:
        print(f"  skip (exists): {spec.slug}")
        return False

    uni = University(
        slug=spec.slug,
        name_en=spec.name_en,
        name_local=spec.name_local,
        country_code=spec.country_code,
        city=spec.city,
        website_url=spec.website_url,
    )
    session.add(uni)
    session.flush()

    for alias in spec.aliases:
        session.add(UniversityAlias(university_id=uni.id, alias=alias))

    dept = Department(
        university_id=uni.id,
        name_en=spec.department_name_en,
        website_url=spec.department_url,
    )
    session.add(dept)
    session.flush()

    p = spec.program
    program = Program(
        department_id=dept.id,
        slug=p.slug,
        name_en=p.name_en,
        degree_type=p.degree_type,
        duration_months=p.duration_months,
        official_url=p.official_url,
        is_active=True,
    )
    session.add(program)
    session.flush()

    for fslug in p.field_slugs:
        session.add(ProgramField(program_id=program.id, field_id=fields[fslug].id))

    intake = ProgramIntake(
        program_id=program.id,
        admission_year=p.admission_year,
        entry_month=p.entry_month,
        intake_label=p.intake_label,
        status=IntakeStatus.PUBLISHED,
    )
    session.add(intake)
    session.flush()

    session.add(
        AdmissionRequirement(
            intake_id=intake.id,
            gpa_requirement_type=GpaRequirementType.NOT_STATED if p.gpa_min is None else GpaRequirementType.MINIMUM,
            gpa_min=p.gpa_min,
            gpa_scale=Decimal("4.0") if p.gpa_min else None,
            gpa_note=p.gpa_note,
            gre_requirement=p.gre,
            gre_note=p.gre_note,
            recommendation_letter_count=p.recommendation_letters,
            professor_contact_status=RequirementStatus.NOT_STATED,
            entrance_exam_status=p.entrance_exam,
            interview_status=p.interview,
        )
    )

    for lang in p.languages:
        session.add(
            LanguageRequirement(
                intake_id=intake.id,
                test_type=lang.test_type,
                minimum_overall=lang.minimum_overall,
                requirement_status=RequirementStatus.REQUIRED,
                notes=lang.notes,
            )
        )

    for t in p.tuitions:
        session.add(
            TuitionFee(
                intake_id=intake.id,
                student_category=t.student_category,
                amount=t.amount,
                currency=t.currency,
                billing_period=t.billing_period,
                normalized_annual_eur=t.normalized_annual_eur,
                notes=t.notes,
            )
        )

    for r in p.rounds:
        round_row = ApplicationRound(
            intake_id=intake.id,
            name=r.name,
            applicant_group=r.applicant_group,
            opens_on=r.opens_on,
            deadline=r.deadline,
            exam_date=r.exam_date,
            notes=r.notes,
        )
        session.add(round_row)
        session.flush()
        for subj in r.exam_subjects:
            session.add(EntranceExamSubject(round_id=round_row.id, subject=subj))

    print(f"  seeded: {spec.slug} / {p.slug} / {p.admission_year}-{p.entry_month}")
    return True


def main() -> None:
    session = SessionLocal()
    try:
        fields = ensure_fields(session)
        session.commit()
        print("Fields ready.")

        added = 0
        for spec in SAMPLES:
            if seed_one(session, spec, fields):
                session.commit()
                added += 1
            else:
                session.rollback()

        print(f"Done. New universities seeded: {added}/{len(SAMPLES)}")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
