"""
Upsert Computer Science / AI / Informatics master's data for:

- University of Copenhagen (English-taught programmes in this scope)
- The University of Tokyo, Graduate School of Information Science and Technology
  (all six master's departments, AY2027)

Replaces admission rows for the same program intake so it can be re-run.
Does not cover every faculty at either university.

Run: docker compose run --rm backend python -m app.seed.ku_utokyo
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

import app.models  # noqa: F401  # register all mappers before inserts
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
    SourceType,
    StudentCategory,
)
from app.ingest.store import sync_sources

VERIFIED_AT = datetime(2026, 9, 29)

KU_LANG_NOTES = (
    "English B. IELTS Academic/Online overall 6.5 with at least 6.0 in each skill. "
    "TOEFL iBT (including Home Edition; MyBest not accepted) overall 83 with at least 20 in each skill. "
    "Cambridge CAE/CPE minimum 180. Tests must be valid at study start. "
    "Source: https://www.ku.dk/studies/masters/application-and-admission/language-requirements"
)

KU_TUITION_NOTE = (
    "Non-EU/EEA/Switzerland citizens pay tuition. EU/EEA/Switzerland citizens pay no tuition. "
    "Semester amount is the 2025/26 Faculty price published for this programme name on the "
    "guest-student fee table (degree-programme invoices can differ; confirm on the tuition page "
    "and in the admission offer). Application deposit DKK 1,120 is charged once per round for "
    "fee-paying applicants and is deducted from the first tuition payment if admitted. "
    "Sources: https://studies.ku.dk/study-abroad/guest/tuition-fees/ and "
    "https://www.ku.dk/studies/masters/application-and-admission/tuition-fees"
)


@dataclass
class LanguageSpec:
    test_type: LanguageTestType
    minimum_overall: Decimal | None = None
    minimum_reading: Decimal | None = None
    minimum_writing: Decimal | None = None
    minimum_listening: Decimal | None = None
    minimum_speaking: Decimal | None = None
    notes: str | None = None
    requirement_status: RequirementStatus = RequirementStatus.REQUIRED


@dataclass
class TuitionSpec:
    student_category: StudentCategory
    amount: Decimal
    currency: str
    billing_period: BillingPeriod
    normalized_annual_eur: Decimal | None = None
    mandatory_fee: Decimal | None = None
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
class IntakeSpec:
    admission_year: int
    entry_month: int
    intake_label: str
    rounds: list[RoundSpec]
    gre: RequirementStatus = RequirementStatus.NOT_REQUIRED
    gre_note: str | None = None
    recommendation_letters: int | None = None
    entrance_exam: RequirementStatus = RequirementStatus.NOT_REQUIRED
    interview: RequirementStatus = RequirementStatus.NOT_STATED
    professor_contact: RequirementStatus = RequirementStatus.NOT_STATED
    gpa_note: str | None = None
    languages: list[LanguageSpec] = field(default_factory=list)
    tuitions: list[TuitionSpec] = field(default_factory=list)


@dataclass
class ProgramSpec:
    department_name_en: str
    department_url: str | None
    slug: str
    name_en: str
    degree_type: str
    duration_months: int
    official_url: str
    field_slugs: list[str]
    intakes: list[IntakeSpec]
    source_urls: list[tuple[SourceType, str]]


@dataclass
class UniversitySpec:
    slug: str
    name_en: str
    name_local: str | None
    country_code: str
    city: str
    website_url: str
    aliases: list[str]
    programs: list[ProgramSpec]


def ku_languages() -> list[LanguageSpec]:
    return [
        LanguageSpec(
            LanguageTestType.IELTS,
            Decimal("6.5"),
            Decimal("6.0"),
            Decimal("6.0"),
            Decimal("6.0"),
            Decimal("6.0"),
            KU_LANG_NOTES,
        ),
        LanguageSpec(
            LanguageTestType.TOEFL_IBT,
            Decimal("83"),
            Decimal("20"),
            Decimal("20"),
            Decimal("20"),
            Decimal("20"),
            KU_LANG_NOTES,
        ),
        LanguageSpec(
            LanguageTestType.CAMBRIDGE,
            Decimal("180"),
            notes="CAE/CPE, C1. " + KU_LANG_NOTES,
        ),
    ]


def ku_tuitions(semester_dkk: Decimal, annual_eur: Decimal) -> list[TuitionSpec]:
    return [
        TuitionSpec(
            StudentCategory.EU_EEA,
            Decimal("0"),
            "DKK",
            BillingPeriod.PER_YEAR,
            Decimal("0"),
            notes="No tuition for citizens of the EU, EEA, or Switzerland. " + KU_TUITION_NOTE,
        ),
        TuitionSpec(
            StudentCategory.NON_EU,
            semester_dkk,
            "DKK",
            BillingPeriod.PER_SEMESTER,
            annual_eur,
            Decimal("1120"),
            notes=KU_TUITION_NOTE,
        ),
    ]


def ku_september_rounds() -> list[RoundSpec]:
    return [
        RoundSpec(
            name="September intake, applicants outside EU/EEA/Switzerland",
            opens_on=date(2026, 11, 15),
            deadline=date(2027, 1, 15),
            applicant_group="non_eu",
            notes="Deadline 15 January 23:59. Reply expected by 13 March. Study start September 2027.",
        ),
        RoundSpec(
            name="September intake, applicants within EU/EEA/Switzerland",
            opens_on=date(2027, 1, 16),
            deadline=date(2027, 3, 1),
            applicant_group="eu_eea",
            notes="Deadline 1 March 23:59. Includes applicants with a legal right of admission. Reply expected by 15 May.",
        ),
    ]


def ku_february_rounds() -> list[RoundSpec]:
    return [
        RoundSpec(
            name="February intake, legal right of admission only",
            deadline=date(2026, 10, 15),
            applicant_group="legal_right",
            notes=(
                "University deadline 15 October 23:59. February start is only open to applicants "
                "with a legal right of admission."
            ),
        ),
    ]


def ku_intake(year: int, month: int, label: str, rounds: list[RoundSpec], semester_dkk: Decimal, annual_eur: Decimal, gpa_note: str) -> IntakeSpec:
    return IntakeSpec(
        admission_year=year,
        entry_month=month,
        intake_label=label,
        rounds=rounds,
        languages=ku_languages(),
        tuitions=ku_tuitions(semester_dkk, annual_eur),
        gpa_note=gpa_note,
        gre_note="GRE is not part of the published admission requirements.",
    )


SCIENCE_FEE = Decimal("62500")
SCIENCE_EUR = Decimal("16750")
HUMANITIES_IT_FEE = Decimal("47000")
HUMANITIES_IT_EUR = Decimal("12596")

KU_CS_NOTE = (
    "English-taught, 120 ECTS. International applicants need a relevant bachelor's degree covering "
    "at least 7.5 ECTS programming (two paradigms), 10 ECTS computer systems, 10 ECTS theoretical "
    "computer science, and 7.5 ECTS discrete mathematics, linear algebra, and mathematical modelling. "
    "Listed Danish bachelor's degrees have a legal right of admission. No pre-assessment."
)
KU_ITC_NOTE = (
    "English-taught, 120 ECTS, Faculty of Humanities. Automatic academic eligibility includes "
    "computer-science bachelor's degrees and certain humanities degrees with 15 ECTS in language "
    "technology, computer science, cognitive science, or linguistics. No pre-assessment."
)
KU_BIO_NOTE = (
    "English-taught, 120 ECTS. Combines biology, statistics, and computer science, with a computer "
    "science specialisation. English B. Listed qualifying bachelor's degrees include computer science "
    "and machine learning and data science. No pre-assessment."
)

UT_GUIDE = "https://www.i.u-tokyo.ac.jp/edu/entra/2027_ag_m_e.pdf"
UT_ADMISSIONS = "https://www.i.u-tokyo.ac.jp/edu/entra/entra_e.shtml"
UT_TOEFL = (
    "English is assessed by TOEFL iBT / TOEFL iBT Home Edition Institutional Score Report. "
    "MyBest scores and the Test Taker Score Report are not accepted. Native speakers must still submit TOEFL. "
    "The school guide does not publish a numeric cutoff. "
    "Guidelines: https://www.i.u-tokyo.ac.jp/edu/entra/entra_e.shtml"
)
UT_TUITION_NOTE = (
    "Estimated AY2027 national-university fees, same schedule for domestic and international students: "
    "admission fee JPY 282,000; tuition JPY 267,900 per half year (JPY 535,800 per year). "
    "Waived for MEXT scholarship students. Amounts can be revised. Examination fee JPY 30,000. "
    f"Source: {UT_GUIDE}"
)
UT_GPA_NOTE = (
    "A bachelor's degree, or an equivalent qualification recognised by the graduate school, is required. "
    "Screening uses transcripts, written examinations, TOEFL, and oral examinations where required. "
    "No published GPA cutoff."
)


def ut_languages() -> list[LanguageSpec]:
    return [
        LanguageSpec(
            LanguageTestType.TOEFL_IBT,
            notes=UT_TOEFL,
        )
    ]


def ut_tuitions() -> list[TuitionSpec]:
    return [
        TuitionSpec(
            StudentCategory.ALL,
            Decimal("267900"),
            "JPY",
            BillingPeriod.PER_SEMESTER,
            Decimal("3150"),
            Decimal("282000"),
            notes=UT_TUITION_NOTE + " mandatory_fee here is the admission fee, not the examination fee.",
        )
    ]


def ut_summer_rounds(subjects: list[str], notes: str) -> list[RoundSpec]:
    return [
        RoundSpec(
            name="Summer entrance examination",
            opens_on=date(2026, 5, 29),
            deadline=date(2026, 6, 4),
            exam_date=date(2026, 8, 20),
            applicant_group="all",
            exam_subjects=subjects,
            notes=notes,
        )
    ]


def ut_winter_rounds(notes: str) -> list[RoundSpec]:
    return [
        RoundSpec(
            name="Winter entrance examination",
            opens_on=date(2026, 11, 11),
            deadline=date(2026, 11, 17),
            applicant_group="all",
            notes=notes,
        )
    ]


SUMMER_NOTE = (
    "Applications close 14:00 JST on 4 June 2026. Document-screening results about 15:00 on 21 July 2026. "
    "General education mathematics (and programming, where that department uses it) on 20 August 2026, 13:00-15:30 tentative, Hongo campus. "
    "Specialized subjects and oral examinations from 24 August through 1 September 2026. "
    "Final results about 15:00 on 9 September 2026. Standard entrance April 2027. "
    f"Source: {UT_GUIDE}"
)
WINTER_NOTE = (
    "Applications close 14:00 JST on 17 November 2026. Document-screening results about 15:00 on 18 December 2026. "
    "Examinations from late January to mid-February 2027; some departments may examine online. "
    "Final results about 15:00 on 15 February 2027. Standard entrance October 2027. "
    "Subject list is in the department admission guide, not the school-wide summer table. "
    f"Source: {UT_GUIDE}"
)

MATH_SUBJECTS = [
    "Mathematics: linear algebra",
    "Mathematics: analysis",
    "Mathematics: probability and statistics",
]


def ut_program(
    department: str,
    slug: str,
    fields: list[str],
    department_url: str,
    summer_subjects: list[str],
    summer_extra: str,
    winter: bool,
    interview: RequirementStatus,
) -> ProgramSpec:
    intakes = [
        IntakeSpec(
            admission_year=2027,
            entry_month=4,
            intake_label="April 2027 (summer examination)",
            rounds=ut_summer_rounds(summer_subjects, SUMMER_NOTE + " " + summer_extra),
            entrance_exam=RequirementStatus.REQUIRED,
            interview=interview,
            languages=ut_languages(),
            tuitions=ut_tuitions(),
            gpa_note=UT_GPA_NOTE,
            gre_note="GRE is not used. English is TOEFL only.",
        )
    ]
    if winter:
        intakes.append(
            IntakeSpec(
                admission_year=2027,
                entry_month=10,
                intake_label="October 2027 (winter examination)",
                rounds=ut_winter_rounds(WINTER_NOTE),
                entrance_exam=RequirementStatus.REQUIRED,
                interview=interview,
                languages=ut_languages(),
                tuitions=ut_tuitions(),
                gpa_note=UT_GPA_NOTE,
                gre_note="GRE is not used. English is TOEFL only.",
            )
        )
    return ProgramSpec(
        department_name_en=department,
        department_url=department_url,
        slug=slug,
        name_en=f"Master of Information Science and Technology ({department.removeprefix('Department of ')})",
        degree_type="Master",
        duration_months=24,
        official_url=UT_GUIDE,
        field_slugs=fields,
        intakes=intakes,
        source_urls=[
            (SourceType.ADMISSION_GUIDELINE, UT_GUIDE),
            (SourceType.DEPARTMENT_PAGE, department_url),
            (SourceType.PROGRAM_PAGE, UT_ADMISSIONS),
        ],
    )


SAMPLES: list[UniversitySpec] = [
    UniversitySpec(
        slug="university-of-copenhagen",
        name_en="University of Copenhagen",
        name_local="Københavns Universitet",
        country_code="DK",
        city="Copenhagen",
        website_url="https://www.ku.dk",
        aliases=["UCPH", "KU"],
        programs=[
            ProgramSpec(
                department_name_en="Department of Computer Science",
                department_url="https://di.ku.dk/english/",
                slug="msc-computer-science",
                name_en="MSc in Computer Science",
                degree_type="MSc",
                duration_months=24,
                official_url="https://www.ku.dk/studies/masters/computer-science",
                field_slugs=["cs", "ai", "data-science"],
                source_urls=[
                    (SourceType.PROGRAM_PAGE, "https://www.ku.dk/studies/masters/computer-science"),
                    (
                        SourceType.ADMISSION_GUIDELINE,
                        "https://www.ku.dk/studies/masters/application-and-admission/language-requirements",
                    ),
                    (
                        SourceType.OTHER,
                        "https://studies.ku.dk/study-abroad/guest/tuition-fees/",
                    ),
                ],
                intakes=[
                    ku_intake(2027, 9, "September 2027", ku_september_rounds(), SCIENCE_FEE, SCIENCE_EUR, KU_CS_NOTE),
                    ku_intake(2027, 2, "February 2027", ku_february_rounds(), SCIENCE_FEE, SCIENCE_EUR, KU_CS_NOTE),
                ],
            ),
            ProgramSpec(
                department_name_en="Department of Nordic Research",
                department_url="https://nors.ku.dk/english/",
                slug="msc-it-and-cognition",
                name_en="MSc in IT and Cognition",
                degree_type="MSc",
                duration_months=24,
                official_url="https://www.ku.dk/studies/masters/it-and-cognition",
                field_slugs=["ai", "cs"],
                source_urls=[
                    (SourceType.PROGRAM_PAGE, "https://www.ku.dk/studies/masters/it-and-cognition"),
                    (
                        SourceType.ADMISSION_GUIDELINE,
                        "https://www.ku.dk/studies/masters/application-and-admission/language-requirements",
                    ),
                    (SourceType.OTHER, "https://studies.ku.dk/study-abroad/guest/tuition-fees/"),
                ],
                intakes=[
                    ku_intake(2027, 9, "September 2027", ku_september_rounds(), HUMANITIES_IT_FEE, HUMANITIES_IT_EUR, KU_ITC_NOTE),
                    ku_intake(2027, 2, "February 2027", ku_february_rounds(), HUMANITIES_IT_FEE, HUMANITIES_IT_EUR, KU_ITC_NOTE),
                ],
            ),
            ProgramSpec(
                department_name_en="Faculty of Science",
                department_url="https://science.ku.dk/",
                slug="msc-bioinformatics",
                name_en="MSc in Bioinformatics",
                degree_type="MSc",
                duration_months=24,
                official_url="https://www.ku.dk/studies/masters/bioinformatics",
                field_slugs=["data-science", "cs"],
                source_urls=[
                    (SourceType.PROGRAM_PAGE, "https://www.ku.dk/studies/masters/bioinformatics"),
                    (
                        SourceType.ADMISSION_GUIDELINE,
                        "https://www.ku.dk/studies/masters/application-and-admission/language-requirements",
                    ),
                    (SourceType.OTHER, "https://studies.ku.dk/study-abroad/guest/tuition-fees/"),
                ],
                intakes=[
                    ku_intake(2027, 9, "September 2027", ku_september_rounds(), SCIENCE_FEE, SCIENCE_EUR, KU_BIO_NOTE),
                    ku_intake(2027, 2, "February 2027", ku_february_rounds(), SCIENCE_FEE, SCIENCE_EUR, KU_BIO_NOTE),
                ],
            ),
        ],
    ),
    UniversitySpec(
        slug="university-of-tokyo",
        name_en="The University of Tokyo",
        name_local="東京大学",
        country_code="JP",
        city="Tokyo",
        website_url="https://www.u-tokyo.ac.jp",
        aliases=["UTokyo", "Todai"],
        programs=[
            ut_program(
                "Department of Computer Science",
                "msc-computer-science",
                ["cs"],
                "https://www.i.u-tokyo.ac.jp/edu/course/cs/admission_e.shtml",
                MATH_SUBJECTS + ["Computer Science (written)", "Computer Science (oral)"],
                "Expected intake about 44. Winter examination is not offered for this master's department.",
                winter=False,
                interview=RequirementStatus.OPTIONAL,
            ),
            ut_program(
                "Department of Mathematical Informatics",
                "msc-mathematical-informatics",
                ["cs"],
                "https://www.i.u-tokyo.ac.jp/edu/entra/entra_e.shtml",
                MATH_SUBJECTS + ["Mathematical Informatics (written)", "Mathematical Informatics (oral)"],
                "Expected intake about 40. Applicants may be allowed to sit another department's specialized subject; see the department guide. Winter examination is not offered.",
                winter=False,
                interview=RequirementStatus.OPTIONAL,
            ),
            ut_program(
                "Department of Information Physics and Computing",
                "msc-information-physics-computing",
                ["cs"],
                "https://www.i.u-tokyo.ac.jp/edu/entra/entra_e.shtml",
                MATH_SUBJECTS + ["Information Physics and Computing (written)", "Information Physics and Computing (oral)"],
                "Expected intake about 47. Summer and winter examinations are both offered.",
                winter=True,
                interview=RequirementStatus.OPTIONAL,
            ),
            ut_program(
                "Department of Information and Communication Engineering",
                "msc-information-communication-engineering",
                ["cs"],
                "https://www.i.u-tokyo.ac.jp/edu/course/ice/pdf/ice2027-guide-e.pdf",
                MATH_SUBJECTS
                + [
                    "Information and Communication Engineering (written)",
                    "Information and Communication Engineering (oral)",
                ],
                "Expected intake about 60. Master's applications are summer examination only; winter examination is not conducted.",
                winter=False,
                interview=RequirementStatus.OPTIONAL,
            ),
            ut_program(
                "Department of Mechano-Informatics",
                "msc-mechano-informatics",
                ["cs", "ai"],
                "https://www.i.u-tokyo.ac.jp/edu/course/m-i/pdf/MI-application2027e.pdf",
                MATH_SUBJECTS
                + ["Oral examination covering mechanics, robotics, and information subjects"],
                "Expected intake about 56. Specialized subjects are examined inside the oral examination, not as a separate written paper. Winter examination is not offered for the master's program in the school guide.",
                winter=False,
                interview=RequirementStatus.REQUIRED,
            ),
            ut_program(
                "Department of Creative Informatics",
                "msc-creative-informatics",
                ["cs", "ai"],
                "https://www.i.u-tokyo.ac.jp/edu/entra/entra_e.shtml",
                [
                    "Mathematics or Programming (general education; choose one)",
                    "Creative Informatics (written)",
                    "Creative Informatics (oral)",
                ],
                "Expected intake about 38, plus possible transfers from other IST departments. Summer and winter examinations are both offered. For AY2027, applicants choose a specialized subject among Creative Informatics, Computer Science, Mathematical Informatics, and Information Physics and Computing.",
                winter=True,
                interview=RequirementStatus.OPTIONAL,
            ),
        ],
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


def ensure_university(session: Session, spec: UniversitySpec) -> University:
    uni = session.scalar(select(University).where(University.slug == spec.slug))
    if uni is None:
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
        exists = session.scalar(
            select(UniversityAlias).where(
                UniversityAlias.university_id == uni.id,
                UniversityAlias.alias == alias,
            )
        )
        if exists is None:
            session.add(UniversityAlias(university_id=uni.id, alias=alias))
    session.flush()
    return uni


def replace_intake_children(session: Session, intake: ProgramIntake, spec: IntakeSpec) -> None:
    round_ids = list(
        session.scalars(select(ApplicationRound.id).where(ApplicationRound.intake_id == intake.id))
    )
    if round_ids:
        session.execute(delete(EntranceExamSubject).where(EntranceExamSubject.round_id.in_(round_ids)))
        session.execute(delete(ApplicationRound).where(ApplicationRound.intake_id == intake.id))
    session.execute(delete(LanguageRequirement).where(LanguageRequirement.intake_id == intake.id))
    session.execute(delete(TuitionFee).where(TuitionFee.intake_id == intake.id))
    session.execute(delete(AdmissionRequirement).where(AdmissionRequirement.intake_id == intake.id))
    session.flush()

    session.add(
        AdmissionRequirement(
            intake_id=intake.id,
            gpa_requirement_type=GpaRequirementType.NOT_STATED,
            gpa_note=spec.gpa_note,
            gre_requirement=spec.gre,
            gre_note=spec.gre_note,
            recommendation_letter_count=spec.recommendation_letters,
            professor_contact_status=spec.professor_contact,
            entrance_exam_status=spec.entrance_exam,
            interview_status=spec.interview,
        )
    )
    for lang in spec.languages:
        session.add(
            LanguageRequirement(
                intake_id=intake.id,
                test_type=lang.test_type,
                minimum_overall=lang.minimum_overall,
                minimum_reading=lang.minimum_reading,
                minimum_writing=lang.minimum_writing,
                minimum_listening=lang.minimum_listening,
                minimum_speaking=lang.minimum_speaking,
                requirement_status=lang.requirement_status,
                notes=lang.notes,
            )
        )
    for tuition in spec.tuitions:
        session.add(
            TuitionFee(
                intake_id=intake.id,
                student_category=tuition.student_category,
                amount=tuition.amount,
                currency=tuition.currency,
                billing_period=tuition.billing_period,
                normalized_annual_eur=tuition.normalized_annual_eur,
                mandatory_fee=tuition.mandatory_fee,
                notes=tuition.notes,
            )
        )
    for rnd in spec.rounds:
        row = ApplicationRound(
            intake_id=intake.id,
            name=rnd.name,
            applicant_group=rnd.applicant_group,
            opens_on=rnd.opens_on,
            deadline=rnd.deadline,
            exam_date=rnd.exam_date,
            notes=rnd.notes,
        )
        session.add(row)
        session.flush()
        for subject in rnd.exam_subjects:
            session.add(EntranceExamSubject(round_id=row.id, subject=subject))


def upsert_program(session: Session, uni: University, spec: ProgramSpec, fields: dict[str, Field]) -> None:
    dept = session.scalar(
        select(Department).where(
            Department.university_id == uni.id,
            Department.name_en == spec.department_name_en,
        )
    )
    if dept is None:
        dept = Department(
            university_id=uni.id,
            name_en=spec.department_name_en,
            website_url=spec.department_url,
        )
        session.add(dept)
        session.flush()
    else:
        dept.website_url = spec.department_url

    program = session.scalar(
        select(Program).where(Program.department_id == dept.id, Program.slug == spec.slug)
    )
    if program is None:
        program = Program(
            department_id=dept.id,
            slug=spec.slug,
            name_en=spec.name_en,
            degree_type=spec.degree_type,
            duration_months=spec.duration_months,
            official_url=spec.official_url,
            is_active=True,
        )
        session.add(program)
        session.flush()
    else:
        program.name_en = spec.name_en
        program.degree_type = spec.degree_type
        program.duration_months = spec.duration_months
        program.official_url = spec.official_url
        program.is_active = True

    session.execute(delete(ProgramField).where(ProgramField.program_id == program.id))
    for slug in spec.field_slugs:
        session.add(ProgramField(program_id=program.id, field_id=fields[slug].id))

    sync_sources(
        session,
        university_id=uni.id,
        department_id=dept.id,
        program_id=program.id,
        sources=list(spec.source_urls),
    )

    for intake_spec in spec.intakes:
        intake = session.scalar(
            select(ProgramIntake).where(
                ProgramIntake.program_id == program.id,
                ProgramIntake.admission_year == intake_spec.admission_year,
                ProgramIntake.entry_month == intake_spec.entry_month,
            )
        )
        if intake is None:
            intake = ProgramIntake(
                program_id=program.id,
                admission_year=intake_spec.admission_year,
                entry_month=intake_spec.entry_month,
                intake_label=intake_spec.intake_label,
                status=IntakeStatus.PUBLISHED,
                last_verified_at=VERIFIED_AT,
            )
            session.add(intake)
            session.flush()
        else:
            intake.intake_label = intake_spec.intake_label
            intake.status = IntakeStatus.PUBLISHED
            intake.last_verified_at = VERIFIED_AT
        replace_intake_children(session, intake, intake_spec)
        print(
            f"  upserted {uni.slug} / {spec.slug} / {intake_spec.admission_year}-{intake_spec.entry_month}"
        )


def main() -> None:
    session = SessionLocal()
    try:
        fields = ensure_fields(session)
        for uni_spec in SAMPLES:
            uni = ensure_university(session, uni_spec)
            for program in uni_spec.programs:
                upsert_program(session, uni, program, fields)
            session.commit()
        print("Done. Copenhagen and Tokyo programmes upserted.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
