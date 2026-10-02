"""
Official requirements for the remaining US P0 programs, then the first US P1 programs.

Checked on 2026-09-29. Michigan CSE is not included: the department site
blocked the fetch. Numbers that a page does not state are left empty.

Run: docker compose run --rm backend python -m app.seed.p0_us_batch3
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.database import SessionLocal
from app.models.enums import LanguageTestType, RequirementStatus, SourceType
from app.seed.ku_utokyo import IntakeSpec, LanguageSpec, RoundSpec
from app.seed.verified_intakes import _program, _save

STANFORD_DEADLINES = "https://www.cs.stanford.edu/admissions-graduate-application-deadlines"
STANFORD_CHECKLIST = "https://www.cs.stanford.edu/admissions/graduate-application-checklists"
STANFORD_FAQ = "https://www.cs.stanford.edu/admissions/masters-admissions-frequently-asked-questions"
STANFORD_SCORES = "https://gradadmissions.stanford.edu/apply/test-scores"
NYU_GSAS = "https://gsas.nyu.edu/admissions/arc/programs/data-science.html"
NYU_FAQ = "https://cds.nyu.edu/masters-in-data-science-faq/"
UCSD_ADMISSIONS = "https://cse.ucsd.edu/graduate/admissions"
UCSD_CHECKLIST = "https://cse.ucsd.edu/graduate/cse-graduate-application-checklist"
UCSD_ENGLISH = "https://grad.ucsd.edu/admissions/requirements/international-students/english-proficiency.html"
UCLA_REQ = "https://www.cs.ucla.edu/graduate-requirements/"
USC_CS = "https://viterbigradadmission.usc.edu/programs/masters/msprograms/computer-science/ms-computer-science/"
USC_AI = "https://viterbigradadmission.usc.edu/programs/masters/msprograms/computer-science/ms-computer-science-artificial-intelligence/"
USC_DS = "https://viterbigradadmission.usc.edu/programs/masters/msprograms/computer-science/ms-cs-data-science/"
USC_APPLY = "https://viterbigradadmission.usc.edu/programs/masters/apply/"
USC_ENGLISH = "https://gradadm.usc.edu/lightboxes/international-students-english-proficiency/"


def usc_languages() -> list[LanguageSpec]:
    return [
        LanguageSpec(
            LanguageTestType.TOEFL_IBT,
            notes=(
                "USC does not publish a university-wide admission minimum. "
                "For Spring 2027 and later, an admitted master's student is exempt from the ISE exam "
                "with 90 overall and 20 in each section on a test before 21 January 2026, "
                "or 4.5 overall and 4 in each section on a later test. "
                "All section scores must come from one sitting. Scores must be within two years of the application date. "
                "PTE and Cambridge C1 Advanced are also accepted for the same exemption."
            ),
        ),
        LanguageSpec(
            LanguageTestType.IELTS,
            notes=(
                "No admission minimum is published. "
                "ISE exemption for a master's applicant is 6.5 overall and 6 on each band, from one sitting."
            ),
        ),
    ]


def usc_intakes(extra_note: str) -> list[IntakeSpec]:
    fall_note = (
        "Program pages list 15 December for scholarship consideration and 15 January as the final deadline, without a year. "
        "The Viterbi deadlines page labels these Fall 2027, and it prints the year on the final deadline: 15 January 2027, 11:59 p.m. Pacific Time. "
        "15 December is stored as 2026."
    )
    spring_note = (
        "Program pages list 15 October for spring, without a year. "
        "The Viterbi deadlines page labels Spring 2027 as 15 October, 11:59 p.m. Pacific Time. Stored as 2026."
    )
    return [
        IntakeSpec(
            2027,
            8,
            "Fall 2027",
            [
                RoundSpec(
                    "Scholarship consideration",
                    deadline=date(2026, 12, 15),
                    applicant_group="all",
                    notes=fall_note,
                ),
                RoundSpec(
                    "Final deadline",
                    deadline=date(2027, 1, 15),
                    applicant_group="all",
                    notes=fall_note,
                ),
            ],
            gre=RequirementStatus.NOT_REQUIRED,
            gre_note="The program page says the GRE is not required for 2027 applications.",
            entrance_exam=RequirementStatus.NOT_REQUIRED,
            gpa_note=extra_note + " A letter of recommendation is listed as optional. No tuition figure is stored.",
            languages=usc_languages(),
        ),
        IntakeSpec(
            2027,
            1,
            "Spring 2027",
            [
                RoundSpec(
                    "Spring admission",
                    deadline=date(2026, 10, 15),
                    applicant_group="all",
                    notes=spring_note,
                )
            ],
            gre=RequirementStatus.NOT_REQUIRED,
            gre_note="The program page says the GRE is not required for 2027 applications.",
            entrance_exam=RequirementStatus.NOT_REQUIRED,
            gpa_note=extra_note + " A letter of recommendation is listed as optional.",
            languages=usc_languages(),
        ),
    ]


def main() -> None:
    session = SessionLocal()
    try:
        stanford = _program(session, "stanford-university", "ms-computer-science")
        stanford.duration_months = None
        _save(
            session,
            stanford,
            official_url=STANFORD_FAQ,
            duration_months=None,
            sources=[
                (SourceType.ADMISSION_GUIDELINE, STANFORD_DEADLINES),
                (SourceType.ADMISSION_GUIDELINE, STANFORD_CHECKLIST),
                (SourceType.FAQ, STANFORD_FAQ),
                (SourceType.ADMISSION_GUIDELINE, STANFORD_SCORES),
            ],
            intakes=[
                IntakeSpec(
                    2027,
                    9,
                    "Autumn 2027",
                    [
                        RoundSpec(
                            "Master's application",
                            opens_on=date(2026, 9, 15),
                            deadline=date(2026, 12, 8),
                            applicant_group="all",
                            notes=(
                                "One cycle, Autumn quarter only. Application fee is $125. "
                                "Decisions are sent by the end of March 2027. "
                                "This replaces the earlier illustrative intake. "
                                "HCP uses the same requirements and is limited to people located in the United States."
                            ),
                        )
                    ],
                    gre=RequirementStatus.NOT_REQUIRED,
                    gre_note="The MS FAQ says GRE scores are not required and are not considered.",
                    recommendation_letters=3,
                    entrance_exam=RequirementStatus.NOT_REQUIRED,
                    gpa_note=(
                        "The FAQ says GPAs are typically at least 3.7 on a 4.0 scale. That is not written as a cutoff. "
                        "The department does not offer financial support for MS students. "
                        "The page does not state a program length, so the earlier 24-month sample value was cleared."
                    ),
                    languages=[
                        LanguageSpec(
                            LanguageTestType.TOEFL_IBT,
                            Decimal("90"),
                            notes=(
                                "University minimum for admission consideration is 90 on a test taken before 21 January 2026, "
                                "and 4.5 on a test taken on or after that date. "
                                "CS does not publish a higher minimum. "
                                "A score below 109 on the older scale, or below 5.5 on the later scale, still requires the Stanford English Placement Test."
                            ),
                        ),
                        LanguageSpec(
                            LanguageTestType.IELTS,
                            Decimal("7"),
                            notes="University minimum for admission consideration is 7. A score below 8 requires the Stanford English Placement Test.",
                        ),
                    ],
                )
            ],
        )

        _save(
            session,
            _program(session, "new-york-university", "ms-data-science"),
            official_url=NYU_GSAS,
            duration_months=None,
            sources=[
                (SourceType.ADMISSION_GUIDELINE, NYU_GSAS),
                (SourceType.ADMISSION_GUIDELINE, NYU_FAQ),
            ],
            intakes=[
                IntakeSpec(
                    2027,
                    9,
                    "Fall 2027",
                    [
                        RoundSpec(
                            "Fall admission",
                            deadline=date(2027, 2, 12),
                            applicant_group="all",
                            notes=(
                                "The GSAS Data Science page lists 12 February for M.S. fall admission, at 5 p.m. Eastern Time, and does not print a year. "
                                "If that date falls on a weekend or US federal holiday, the next business day applies. "
                                "There is no spring M.S. deadline on that page."
                            ),
                        )
                    ],
                    gre=RequirementStatus.OPTIONAL,
                    gre_note="GSAS lists GRE as optional for the M.S. The CDS FAQ says there is no minimum cutoff and GMAT is not accepted.",
                    entrance_exam=RequirementStatus.NOT_REQUIRED,
                    gpa_note=(
                        "Prerequisites named on the GSAS page: Calculus I, linear algebra, an introductory computer science course, "
                        "and one of Calculus II, probability, statistics, or a heavily mathematical advanced course. "
                        "The page does not state how many recommendation letters are required."
                    ),
                    languages=[
                        LanguageSpec(
                            LanguageTestType.TOEFL_IBT,
                            Decimal("100"),
                            notes="The CDS FAQ says there is no minimum cutoff. It recommends at least 100 on the internet-based test.",
                            requirement_status=RequirementStatus.RECOMMENDED,
                        ),
                        LanguageSpec(
                            LanguageTestType.IELTS,
                            Decimal("7.0"),
                            notes="The CDS FAQ says there is no minimum cutoff. It recommends an IELTS band of at least 7.0.",
                            requirement_status=RequirementStatus.RECOMMENDED,
                        ),
                    ],
                )
            ],
        )

        _save(
            session,
            _program(session, "university-of-california-san-diego", "ms-computer-science-and-engineering"),
            official_url=UCSD_ADMISSIONS,
            duration_months=None,
            sources=[
                (SourceType.ADMISSION_GUIDELINE, UCSD_ADMISSIONS),
                (SourceType.ADMISSION_GUIDELINE, UCSD_CHECKLIST),
                (SourceType.ADMISSION_GUIDELINE, UCSD_ENGLISH),
            ],
            intakes=[
                IntakeSpec(
                    2027,
                    9,
                    "Fall 2027",
                    [
                        RoundSpec(
                            "Fall admission",
                            opens_on=date(2026, 9, 2),
                            deadline=date(2026, 12, 16),
                            applicant_group="all",
                            notes=(
                                "Open from 2 September 2026 until 16 December 2026 at 12:00 a.m. PST. "
                                "Fall quarter only. The department offers MS degrees in computer science and in computer engineering through this application."
                            ),
                        )
                    ],
                    gre=RequirementStatus.OPTIONAL,
                    gre_note="GRE is not required for Fall 2027 MS applications. Applicants may still submit valid scores. Institution code 4836.",
                    recommendation_letters=3,
                    entrance_exam=RequirementStatus.NOT_REQUIRED,
                    gpa_note="At least a B average, stated as 3.0 GPA or equivalent. Meeting that minimum does not guarantee admission. A bachelor's degree in computer science, computer engineering, electrical engineering, or mathematics is preferred.",
                    languages=[
                        LanguageSpec(
                            LanguageTestType.TOEFL_IBT,
                            Decimal("85"),
                            notes=(
                                "University-wide minimum cited by the GEPA page that CSE links to: 85 on the previous iBT, or 4.5 on the new iBT. "
                                "CSE does not publish a higher score. MyBest scores are not accepted."
                            ),
                        ),
                        LanguageSpec(
                            LanguageTestType.IELTS,
                            Decimal("7"),
                            notes="University-wide minimum band score is 7. CSE does not publish a higher score.",
                        ),
                        LanguageSpec(
                            LanguageTestType.DUOLINGO,
                            Decimal("120"),
                            notes="Minimum total 120 out of 160. The GEPA page says this option is effective for the Fall 2026 admissions cycle.",
                        ),
                        LanguageSpec(
                            LanguageTestType.PTE,
                            Decimal("65"),
                            notes="Minimum overall score is 65.",
                        ),
                    ],
                )
            ],
        )

        _save(
            session,
            _program(session, "university-of-california-los-angeles", "ms-computer-science"),
            official_url=UCLA_REQ,
            duration_months=None,
            sources=[(SourceType.ADMISSION_GUIDELINE, UCLA_REQ)],
            intakes=[
                IntakeSpec(
                    2027,
                    9,
                    "Fall 2027",
                    [
                        RoundSpec(
                            "Fall admission",
                            deadline=date(2026, 12, 15),
                            applicant_group="all",
                            notes=(
                                "The requirements page says the deadline is 15 December at 11:59 p.m. Pacific Time, and that applications are accepted from mid-September through that date. "
                                "It does not print the year. Fall quarter only. The 2026 date is the cycle for a Fall 2027 start."
                            ),
                        )
                    ],
                    gre=RequirementStatus.NOT_STATED,
                    gre_note=(
                        "The page waives the GRE only for the 2025-2026 cycle, with applications due 15 December 2024. "
                        "It does not state the rule for the Fall 2027 intake."
                    ),
                    recommendation_letters=3,
                    entrance_exam=RequirementStatus.NOT_REQUIRED,
                    gpa_note=(
                        "The university requires a cumulative GPA of at least 3.0. "
                        "The department says the most competitive applicants have at least 3.5, and the average cumulative GPA of admitted applicants is 3.60. "
                        "Duolingo is not accepted."
                    ),
                    languages=[
                        LanguageSpec(
                            LanguageTestType.TOEFL_IBT,
                            notes=(
                                "The CS page says a first language other than English requires a TOEFL of at least 87 on the computer-based test or 560 on the paper test. "
                                "It also lists the Graduate Division new-scale figure, for tests on or after 21 January 2026, as overall 4.5, and says that figure is separate from what the CS department requires. "
                                "No internet-based total on the 0-120 scale is stated."
                            ),
                        ),
                        LanguageSpec(
                            LanguageTestType.IELTS,
                            Decimal("7.0"),
                            notes="The CS page requires an IELTS score of at least 7.0 when English is not the first language.",
                        ),
                    ],
                )
            ],
        )

        ai = _program(session, "university-of-southern-california", "ms-artificial-intelligence")
        ai.name_en = "MS in Computer Science - Artificial Intelligence"
        ds = _program(session, "university-of-southern-california", "ms-data-science")
        ds.name_en = "MS in Computer Science - Data Science"

        _save(
            session,
            _program(session, "university-of-southern-california", "ms-computer-science"),
            official_url=USC_CS,
            duration_months=None,
            sources=[
                (SourceType.PROGRAM_PAGE, USC_CS),
                (SourceType.ADMISSION_GUIDELINE, USC_APPLY),
                (SourceType.ADMISSION_GUIDELINE, USC_ENGLISH),
            ],
            intakes=usc_intakes(
                "32 units. A thesis option adds four units. The page does not state a length in months."
            ),
        )
        _save(
            session,
            ai,
            official_url=USC_AI,
            duration_months=None,
            sources=[
                (SourceType.PROGRAM_PAGE, USC_AI),
                (SourceType.ADMISSION_GUIDELINE, USC_APPLY),
                (SourceType.ADMISSION_GUIDELINE, USC_ENGLISH),
            ],
            intakes=usc_intakes(
                "32 units. Thesis option is not available. Directed research may be requested after the first semester. This program is not available through DEN@Viterbi."
            ),
        )
        _save(
            session,
            ds,
            official_url=USC_DS,
            duration_months=None,
            sources=[
                (SourceType.PROGRAM_PAGE, USC_DS),
                (SourceType.ADMISSION_GUIDELINE, USC_APPLY),
                (SourceType.ADMISSION_GUIDELINE, USC_ENGLISH),
            ],
            intakes=usc_intakes(
                "32 units. Thesis option is not available. The same degree is also offered online through DEN@Viterbi; the page does not give a separate online deadline."
            ),
        )

        session.commit()
        print("Done. Stanford, NYU Data Science, UCSD, UCLA, and USC intakes saved.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
