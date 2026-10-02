"""
Official requirements for the remaining Canada P0 programs.

Checked on 2026-10-02. A fee, score, or deadline that the fetched page does not
state is left empty. The UBC Master of Data Science program site blocked the
fetch, so that row uses only the UBC Graduate School program page.

Run: docker compose run --rm backend python -m app.seed.p0_ca_batch
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from app.database import SessionLocal
from app.models.catalog import ProgramIntake
from app.models.enums import (
    BillingPeriod,
    LanguageTestType,
    RequirementStatus,
    SourceType,
    StudentCategory,
)
from app.seed.ku_utokyo import IntakeSpec, LanguageSpec, RoundSpec, TuitionSpec
from app.seed.verified_intakes import _program, _save

VERIFIED_AT = datetime(2026, 10, 2)

TORONTO_MSC = "https://web.cs.toronto.edu/graduate/msc"
TORONTO_APPLY = "https://web.cs.toronto.edu/graduate/how-to-apply"
TORONTO_CALENDAR = "https://sgs.calendar.utoronto.ca/computer-science-computer-science-msc"
TORONTO_ENGLISH = "https://www.sgs.utoronto.ca/future-students/admission-application-requirements/english-language-proficiency-testing/"
UBC_ADMISSIONS = "https://www.cs.ubc.ca/students/grad/admissions"
UBC_MSC = "https://www.grad.ubc.ca/prospective-students/graduate-degree-programs/master-of-science-computer-science"
UBC_ELIGIBILITY = "https://www.cs.ubc.ca/students/grad/admissions/eligibility"
UBC_MDS = "https://www.grad.ubc.ca/prospective-students/graduate-degree-programs/master-of-data-science"
WATERLOO_MMATH = "https://uwaterloo.ca/future-graduate-students/programs/by-faculty/math/computer-science-master-math-mmath"
WATERLOO_DS = "https://uwaterloo.ca/future-graduate-students/programs/by-faculty/math/data-science-master-math-mmath"
WATERLOO_DS_REQ = "https://uwaterloo.ca/data-science/graduate-programs/admission-requirements"
WATERLOO_DS_DATES = "https://uwaterloo.ca/data-science/graduate-programs/application-deadlines"
MCGILL_MSC = "https://www.mcgill.ca/gradapplicants/program/computer-science-msc"
MCGILL_APPLY = "https://www.cs.mcgill.ca/academic/graduate/applying/"
MCGILL_DEADLINE = "https://www.cs.mcgill.ca/graduate/future/deadline/"
MCGILL_DATES = "https://www.mcgill.ca/importantdates/channels/event/application-period-admission-september-2027-graduate-studies-361690"
MCGILL_CATALOGUE = "https://coursecatalogue.mcgill.ca/en/regulations/graduate/admissions-application-procedures/"


def toronto_languages() -> list[LanguageSpec]:
    note = (
        "The Computer Science calendar requires TOEFL 4.5/6.0 overall, 4.5/6.0 in writing, and 4.0/6.0 in speaking "
        "for an applicant whose primary language is not English and whose university did not teach in English. "
        "It does not state reading or listening minimums. "
        "The School of Graduate Studies page for the same new scale lists overall 4.5, writing 4.5, and speaking 4.0, "
        "and the previous 0-120 scale as overall 93 with writing and speaking 22. "
        "That page also requires IELTS Academic 7.0 with at least 6.5 in each component, "
        "Cambridge C1 Advanced or C2 Proficiency 185 overall with at least 176 in each component, "
        "COPE 76 with at least 22 in each component and 32 in writing, and CAEL 70 with at least 60 in each part. "
        "Tests must have been taken within 24 months. TOEFL MyBest, TOEFL ITP, IELTS Indicator, and IELTS One Skill Retake are not accepted. "
        "The calendar does not restate the IELTS, Cambridge, COPE, or CAEL figures."
    )
    return [
        LanguageSpec(
            LanguageTestType.TOEFL_IBT,
            Decimal("4.5"),
            minimum_writing=Decimal("4.5"),
            minimum_speaking=Decimal("4.0"),
            notes=note,
        ),
        LanguageSpec(
            LanguageTestType.IELTS,
            Decimal("7.0"),
            Decimal("6.5"),
            Decimal("6.5"),
            Decimal("6.5"),
            Decimal("6.5"),
            notes="School of Graduate Studies minimum. Academic module. " + note,
        ),
        LanguageSpec(
            LanguageTestType.CAMBRIDGE,
            Decimal("185"),
            notes="C1 Advanced or C2 Proficiency, at least 176 in each component. " + note,
        ),
    ]


def ubc_msc_languages() -> list[LanguageSpec]:
    note = (
        "Required when the degree is from a university outside Canada where English is not the primary language of instruction. "
        "Tests must have been taken within the last 24 months. "
        "The current TOEFL scale on the program page is overall 5.0, reading 4.5, writing 4.5, speaking 4.0, listening 5.0. "
        "For a test taken before 21 January 2026, the same page lists the 120-point scale: overall 100, reading 22, writing 21, speaking 21, listening 22."
    )
    return [
        LanguageSpec(
            LanguageTestType.TOEFL_IBT,
            Decimal("5.0"),
            Decimal("4.5"),
            Decimal("4.5"),
            Decimal("5.0"),
            Decimal("4.0"),
            notes=note,
        ),
        LanguageSpec(
            LanguageTestType.IELTS,
            Decimal("7.0"),
            Decimal("6.5"),
            Decimal("6.5"),
            Decimal("6.5"),
            Decimal("6.5"),
            notes="IELTS Academic. " + note,
        ),
        LanguageSpec(
            LanguageTestType.DUOLINGO,
            Decimal("130"),
            Decimal("120"),
            Decimal("130"),
            Decimal("120"),
            Decimal("120"),
            notes=note,
        ),
    ]


def mcgill_languages() -> list[LanguageSpec]:
    note = (
        "School of Computer Science applying page: internet-based TOEFL 100 with no component below 22; "
        "it also lists paper-based 600 and computer-based 230. IELTS overall band 6.5, with no section minimum stated there. "
        "International students must submit TOEFL or IELTS unless their mother tongue is English, "
        "or they completed a degree where English was the language of instruction. Canadian students do not need the test. "
        "The 2026-27 graduate catalogue states a university minimum, which a department may set higher: "
        "on the 6-point scale as of January 2026, TOEFL overall 4.5 with reading 4.5, listening 4.5, writing 4.5, and speaking 4.0; "
        "for an exam before January 2026, 86 overall and no component below 20. IELTS band 6.5 or greater. "
        "The School page does not restate the 6-point scale."
    )
    return [
        LanguageSpec(
            LanguageTestType.TOEFL_IBT,
            Decimal("100"),
            Decimal("22"),
            Decimal("22"),
            Decimal("22"),
            Decimal("22"),
            notes=note,
        ),
        LanguageSpec(LanguageTestType.IELTS, Decimal("6.5"), notes=note),
    ]


def main() -> None:
    session = SessionLocal()
    try:
        toronto_note = (
            "Fall only. Winter and summer starts are not offered. "
            "International applicants are not considered for the MSc in Computer Science. "
            "Minimum standing is a University of Toronto B+, stated as 77–79% or 3.3/4.0 in the final year. "
            "Program length is 4 academic sessions full-time. The guaranteed funding period is 16 months. "
            "No tuition amount is published on the program or application pages fetched for this row. "
            "The application fee on the how-to-apply page is 130 CAD and is not stored as tuition. "
            "Some applicants may be asked to interview. Supervisors are assigned from the interests named in the application."
        )
        ubc_msc_note = (
            "A four-year bachelor's degree equivalent to a UBC degree, normally in computer science. "
            "The Graduate School minimum is a B+ average, 76% at UBC. The department says meeting that minimum does not guarantee admission. "
            "The research MSc is described as a 2-year program. "
            "Applicants indicate faculty they want to work with. Contacting faculty before applying is not necessary. "
            "The Graduate School program page said upcoming open dates were not yet configured; the department page states the dates stored here."
        )
        records: list[tuple] = [
            (
                "university-of-toronto",
                "msc-computer-science",
                TORONTO_MSC,
                None,
                [
                    (SourceType.PROGRAM_PAGE, TORONTO_MSC),
                    (SourceType.ADMISSION_GUIDELINE, TORONTO_APPLY),
                    (SourceType.ADMISSION_GUIDELINE, TORONTO_CALENDAR),
                    (SourceType.ADMISSION_GUIDELINE, TORONTO_ENGLISH),
                ],
                [
                    IntakeSpec(
                        2027,
                        9,
                        "Fall 2027",
                        [
                            RoundSpec(
                                "Fall admission",
                                deadline=date(2026, 12, 1),
                                applicant_group="not international",
                                notes=(
                                    "The how-to-apply page says Fall 2027 applications are open and close on 1 December 2026. "
                                    "The MSc page says Fall 2027 applications open in October 2026 and does not give a day. "
                                    "All mandatory documents must be uploaded by the deadline."
                                ),
                            )
                        ],
                        gre=RequirementStatus.RECOMMENDED,
                        gre_note=(
                            "Applicants who do not have a Canadian university degree are encouraged, but not required, to submit GRE General Test scores. "
                            "Institution code 0982. Department code 0402."
                        ),
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_STATED,
                        interview=RequirementStatus.NOT_STATED,
                        professor_contact=RequirementStatus.NOT_STATED,
                        gpa_note=toronto_note,
                        languages=toronto_languages(),
                    )
                ],
            ),
            (
                "university-of-british-columbia",
                "msc-computer-science",
                UBC_ADMISSIONS,
                24,
                [
                    (SourceType.ADMISSION_GUIDELINE, UBC_ADMISSIONS),
                    (SourceType.PROGRAM_PAGE, UBC_MSC),
                    (SourceType.ADMISSION_GUIDELINE, UBC_ELIGIBILITY),
                ],
                [
                    IntakeSpec(
                        2027,
                        9,
                        "September 2027",
                        [
                            RoundSpec(
                                "September 2027",
                                opens_on=date(2026, 9, 15),
                                deadline=date(2026, 12, 15),
                                applicant_group="all",
                                notes="Department page: the portal opens on 15 September and closes on 15 December. 15 December 2026 is the deadline for a start in September 2027 or January 2028.",
                            )
                        ],
                        gre=RequirementStatus.NOT_REQUIRED,
                        gre_note="The Graduate School program page says the GRE is not required.",
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_STATED,
                        interview=RequirementStatus.NOT_STATED,
                        professor_contact=RequirementStatus.NOT_REQUIRED,
                        gpa_note=ubc_msc_note,
                        languages=ubc_msc_languages(),
                        tuitions=[
                            TuitionSpec(
                                StudentCategory.DOMESTIC,
                                Decimal("5738.52"),
                                "CAD",
                                BillingPeriod.PER_YEAR,
                                notes=(
                                    "Graduate School first-year tuition for a Canadian citizen, permanent resident, refugee, or diplomat: "
                                    "5,738.52 CAD per year, in three installments of 1,912.84 CAD. "
                                    "Student fees are listed as about 1,169.35 CAD per year. Application fee 118.50 CAD. "
                                    "The page says tuition usually increases 2% to 5% a year."
                                ),
                            ),
                            TuitionSpec(
                                StudentCategory.INTERNATIONAL,
                                Decimal("10081.65"),
                                "CAD",
                                BillingPeriod.PER_YEAR,
                                notes=(
                                    "Graduate School first-year international tuition: 10,081.65 CAD per year, in three installments of 3,360.55 CAD. "
                                    "An International Tuition Award of 3,200 CAD per year is listed for eligible students. "
                                    "Application fee 168.25 CAD."
                                ),
                            ),
                        ],
                    ),
                    IntakeSpec(
                        2028,
                        1,
                        "January 2028",
                        [
                            RoundSpec(
                                "January 2028",
                                opens_on=date(2026, 9, 15),
                                deadline=date(2026, 12, 15),
                                applicant_group="all",
                                notes="Same department deadline as September 2027: 15 December 2026.",
                            )
                        ],
                        gre=RequirementStatus.NOT_REQUIRED,
                        gre_note="The Graduate School program page says the GRE is not required.",
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_STATED,
                        interview=RequirementStatus.NOT_STATED,
                        professor_contact=RequirementStatus.NOT_REQUIRED,
                        gpa_note=ubc_msc_note,
                        languages=ubc_msc_languages(),
                        tuitions=[
                            TuitionSpec(StudentCategory.DOMESTIC, Decimal("5738.52"), "CAD", BillingPeriod.PER_YEAR, notes="Same annual figure as the September row. The page does not print a separate January rate."),
                            TuitionSpec(StudentCategory.INTERNATIONAL, Decimal("10081.65"), "CAD", BillingPeriod.PER_YEAR, notes="Same annual figure as the September row. The page does not print a separate January rate."),
                        ],
                    ),
                ],
            ),
            (
                "university-of-british-columbia",
                "master-of-data-science",
                UBC_MDS,
                10,
                [(SourceType.PROGRAM_PAGE, UBC_MDS)],
                [
                    IntakeSpec(
                        2027,
                        9,
                        "September 2027",
                        [
                            RoundSpec(
                                "Canadian applicants",
                                deadline=date(2027, 1, 31),
                                applicant_group="Canadian",
                                notes="Graduate School page: Canadian applicant deadline 31 January 2027. The program website could not be fetched.",
                            ),
                            RoundSpec(
                                "International applicants",
                                deadline=date(2027, 1, 31),
                                applicant_group="international",
                                notes="Graduate School page: international applicant deadline 31 January 2027.",
                            ),
                        ],
                        gre=RequirementStatus.NOT_STATED,
                        recommendation_letters=None,
                        entrance_exam=RequirementStatus.NOT_STATED,
                        interview=RequirementStatus.NOT_STATED,
                        professor_contact=RequirementStatus.NOT_STATED,
                        gpa_note=(
                            "10-month professional program, coursework only, in person at UBC Vancouver. "
                            "The Graduate School page says this program is not administered by the Faculty of Graduate and Postdoctoral Studies "
                            "and points to the program website for the application process. That site blocked the fetch, "
                            "so English scores, reference-letter count, GPA, and GRE are not stored."
                        ),
                        tuitions=[
                            TuitionSpec(
                                StudentCategory.DOMESTIC,
                                Decimal("36569.73"),
                                "CAD",
                                BillingPeriod.TOTAL_PROGRAM,
                                notes=(
                                    "Program fee for a Canadian citizen, permanent resident, refugee, or diplomat: 36,569.73 CAD, "
                                    "charged in three installments of 12,189.91 CAD. "
                                    "Deposit to accept an offer: 3,000 CAD. Application fee 120.75 CAD. "
                                    "Student fees about 1,203.20 CAD per year."
                                ),
                            ),
                            TuitionSpec(
                                StudentCategory.INTERNATIONAL,
                                Decimal("59767.92"),
                                "CAD",
                                BillingPeriod.TOTAL_PROGRAM,
                                notes=(
                                    "International program fee: 59,767.92 CAD, in three installments of 19,922.64 CAD. "
                                    "Deposit to accept an offer: 3,000 CAD. Application fee 168.25 CAD. "
                                    "The International Tuition Award is listed as not applicable."
                                ),
                            ),
                        ],
                    )
                ],
            ),
            (
                "university-of-waterloo",
                "mmath-computer-science",
                WATERLOO_MMATH,
                24,
                [(SourceType.PROGRAM_PAGE, WATERLOO_MMATH)],
                [
                    IntakeSpec(
                        2027,
                        9,
                        "Fall 2027",
                        [
                            RoundSpec(
                                "September admission",
                                deadline=date(2026, 12, 1),
                                applicant_group="all",
                                notes="The program page says 1 December for admission in September of the following year. It does not print a calendar year. Stored as 1 December 2026 for September 2027.",
                            )
                        ],
                        gre=RequirementStatus.NOT_STATED,
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_STATED,
                        interview=RequirementStatus.NOT_STATED,
                        professor_contact=RequirementStatus.NOT_REQUIRED,
                        gpa_note=(
                            "Honours bachelor's degree in computer science or engineering, or an equivalent degree, with at least a 78% standing. "
                            "Length is 24 months full-time. Admission is only to the thesis option. "
                            "A supervisor is not required before applying; students are advised to contact potential supervisors. "
                            "Three references, at least two academic. No tuition figure is printed on this page."
                        ),
                        languages=[
                            LanguageSpec(
                                LanguageTestType.TOEFL_IBT,
                                Decimal("5"),
                                minimum_writing=Decimal("4.5"),
                                minimum_speaking=Decimal("4"),
                                notes="Program page: TOEFL 5 (writing 4.5, speaking 4). Reading and listening minimums are not stated. Required only if applicable.",
                            ),
                            LanguageSpec(
                                LanguageTestType.IELTS,
                                Decimal("6.5"),
                                minimum_writing=Decimal("6.0"),
                                minimum_speaking=Decimal("6.5"),
                                notes="Program page: IELTS 6.5 (writing 6.0, speaking 6.5). Reading and listening minimums are not stated.",
                            ),
                        ],
                    ),
                    IntakeSpec(
                        2028,
                        1,
                        "Winter 2028",
                        [
                            RoundSpec(
                                "January admission",
                                deadline=date(2027, 6, 1),
                                applicant_group="all",
                                notes="The program page says 1 June for admission in January of the following year. Stored as 1 June 2027 for January 2028.",
                            )
                        ],
                        gre=RequirementStatus.NOT_STATED,
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_STATED,
                        interview=RequirementStatus.NOT_STATED,
                        professor_contact=RequirementStatus.NOT_REQUIRED,
                        gpa_note="Same admission requirements as the September row. No separate tuition figure is printed.",
                        languages=[
                            LanguageSpec(LanguageTestType.TOEFL_IBT, Decimal("5"), minimum_writing=Decimal("4.5"), minimum_speaking=Decimal("4"), notes="Same figures as the September row."),
                            LanguageSpec(LanguageTestType.IELTS, Decimal("6.5"), minimum_writing=Decimal("6.0"), minimum_speaking=Decimal("6.5"), notes="Same figures as the September row."),
                        ],
                    ),
                    IntakeSpec(
                        2027,
                        5,
                        "Spring 2027",
                        [
                            RoundSpec(
                                "May admission",
                                deadline=date(2026, 10, 1),
                                applicant_group="all",
                                notes="The program page says 1 October for admission in May of the following year. Stored as 1 October 2026 for May 2027. The page does not say whether this cycle is still open.",
                            )
                        ],
                        gre=RequirementStatus.NOT_STATED,
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_STATED,
                        interview=RequirementStatus.NOT_STATED,
                        professor_contact=RequirementStatus.NOT_REQUIRED,
                        gpa_note="Same admission requirements as the September row. No separate tuition figure is printed.",
                        languages=[
                            LanguageSpec(LanguageTestType.TOEFL_IBT, Decimal("5"), minimum_writing=Decimal("4.5"), minimum_speaking=Decimal("4"), notes="Same figures as the September row."),
                            LanguageSpec(LanguageTestType.IELTS, Decimal("6.5"), minimum_writing=Decimal("6.0"), minimum_speaking=Decimal("6.5"), notes="Same figures as the September row."),
                        ],
                    ),
                ],
            ),
            (
                "university-of-waterloo",
                "data-science",
                WATERLOO_DS,
                24,
                [
                    (SourceType.PROGRAM_PAGE, WATERLOO_DS),
                    (SourceType.ADMISSION_GUIDELINE, WATERLOO_DS_REQ),
                    (SourceType.ADMISSION_GUIDELINE, WATERLOO_DS_DATES),
                ],
                [
                    IntakeSpec(
                        2027,
                        9,
                        "Fall 2027",
                        [
                            RoundSpec(
                                "September admission",
                                deadline=date(2026, 12, 15),
                                applicant_group="all",
                                notes=(
                                    "The MMath in Data Science page says 15 December for admission in September of the following year, and that the program admits only in Fall. "
                                    "Stored as 15 December 2026 for September 2027. The deadlines table repeats 15 December and does not print a year. "
                                    "This row is the research MMath, not the Master of Data Science and Artificial Intelligence."
                                ),
                            )
                        ],
                        gre=RequirementStatus.RECOMMENDED,
                        gre_note="The Data Science admission-requirements page says GRE scores are not required, and applicants are encouraged to submit them.",
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_STATED,
                        interview=RequirementStatus.NOT_STATED,
                        professor_contact=RequirementStatus.RECOMMENDED,
                        gpa_note=(
                            "Four-year honours bachelor's degree or equivalent in data science, computer science, statistics, mathematics, or a related field, with a minimum overall average of 78%. "
                            "Senior-level experience in at least one of computer science or statistics. "
                            "Length is 24 months full-time, thesis. "
                            "Students are strongly advised to contact potential supervisors before applying. "
                            "Three references, at least two academic. Prior work experience is not required. "
                            "No tuition figure is printed on these pages."
                        ),
                        languages=[
                            LanguageSpec(
                                LanguageTestType.TOEFL_IBT,
                                Decimal("5"),
                                minimum_writing=Decimal("5"),
                                minimum_speaking=Decimal("5"),
                                notes="Program page: TOEFL 5 (writing 5, speaking 5). Reading and listening minimums are not stated.",
                            ),
                            LanguageSpec(
                                LanguageTestType.IELTS,
                                Decimal("7.5"),
                                minimum_writing=Decimal("7"),
                                minimum_speaking=Decimal("7"),
                                notes="Program page: IELTS 7.5 (writing 7, speaking 7). Reading and listening minimums are not stated.",
                            ),
                        ],
                    )
                ],
            ),
            (
                "mcgill-university",
                "msc-computer-science",
                MCGILL_MSC,
                None,
                [
                    (SourceType.PROGRAM_PAGE, MCGILL_MSC),
                    (SourceType.ADMISSION_GUIDELINE, MCGILL_APPLY),
                    (SourceType.ADMISSION_GUIDELINE, MCGILL_DEADLINE),
                    (SourceType.ADMISSION_GUIDELINE, MCGILL_DATES),
                    (SourceType.ADMISSION_GUIDELINE, MCGILL_CATALOGUE),
                ],
                [
                    IntakeSpec(
                        2027,
                        9,
                        "Fall 2027",
                        [
                            RoundSpec(
                                "International",
                                deadline=date(2026, 12, 15),
                                applicant_group="international",
                                notes=(
                                    "Thesis MSc, Fall only. The School deadline page says 15 December for international applicants. "
                                    "The graduate-studies application period for September 2027 runs from 15 September 2026 to 15 June 2027; "
                                    "the School pages give the day and month without a year."
                                ),
                            ),
                            RoundSpec(
                                "Canadian, financial support",
                                deadline=date(2026, 12, 15),
                                applicant_group="canadian-funded",
                                notes="School deadline page: Canadian applicants who want to be considered for financial support apply by 15 December.",
                            ),
                            RoundSpec(
                                "Canadian, no financial support",
                                deadline=date(2027, 2, 15),
                                applicant_group="canadian-unfunded",
                                notes="School deadline page: Canadian applicants who do not request financial support may apply until 15 February. The program listing states the domestic deadline as 15 February without the funding distinction.",
                            ),
                        ],
                        gre=RequirementStatus.OPTIONAL,
                        gre_note="MSc applicants whose undergraduate degree is from outside Canada may optionally submit the GRE General Test. Institution code 0935. PhD rules on this page are not stored on this row.",
                        recommendation_letters=2,
                        entrance_exam=RequirementStatus.NOT_STATED,
                        interview=RequirementStatus.NOT_STATED,
                        professor_contact=RequirementStatus.NOT_REQUIRED,
                        gpa_note=(
                            "The program listing states a minimum 3.2 CGPA out of 4.0. "
                            "The 2026-27 catalogue states a general minimum of 3.0/4.0, or 3.2/4.0 for the last two years of full-time study, and says a unit may set a higher minimum. "
                            "Applicants name an area of research. Contacting a supervisor before arrival is not required. "
                            "The application asks for at least three proposed supervisors. "
                            "MSc applicants are strongly encouraged to include a statement of objectives and a CV. "
                            "Application fee on the School page: 132.90 CAD. No tuition amount and no program length in months are stated on the fetched pages. "
                            "January admission is generally not offered; the page says a December graduate with a very strong background may occasionally be accepted, with documents by 1 September. That exception is not stored as its own intake."
                        ),
                        languages=mcgill_languages(),
                    )
                ],
            ),
        ]
        for university_slug, program_slug, official_url, duration_months, sources, intakes in records:
            program = _program(session, university_slug, program_slug)
            _save(
                session,
                program,
                official_url=official_url,
                duration_months=duration_months,
                sources=sources,
                intakes=intakes,
            )
        session.flush()
        program_ids = []
        for university_slug, program_slug, *_rest in records:
            program = _program(session, university_slug, program_slug)
            program_ids.append(program.id)
        for intake in session.query(ProgramIntake).filter(ProgramIntake.program_id.in_(program_ids)):
            intake.last_verified_at = VERIFIED_AT
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
