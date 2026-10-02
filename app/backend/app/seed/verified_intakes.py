"""
Add admission requirements for programs whose official pages were checked
on 2026-09-29. Does not invent scores, fees, or deadlines that were not on
those pages, and does not change Copenhagen, Tokyo, or the earlier sample intakes.

Run: docker compose run --rm backend python -m app.seed.verified_intakes
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.database import SessionLocal
from app.models.catalog import Department, Program, ProgramIntake, University
from app.models.enums import (
    BillingPeriod,
    IntakeStatus,
    LanguageTestType,
    RequirementStatus,
    SourceType,
    StudentCategory,
)
from app.ingest.store import sync_sources
from app.seed.ku_utokyo import (
    VERIFIED_AT,
    IntakeSpec,
    LanguageSpec,
    RoundSpec,
    TuitionSpec,
    replace_intake_children,
)

CORNELL_APPLY = "https://www.cs.cornell.edu/master-engineering-computer-science/apply"
CORNELL_TUITION = "https://bursar.cornell.edu/students-parents/tuition-rates-and-fees"
COLUMBIA_FAQ = "https://www.cs.columbia.edu/education/ms/appfaq/"
COLUMBIA_SEAS = "https://www.engineering.columbia.edu/admissions-aid/graduate-admissions/how-apply/application-requirements"
NYU_CS = "https://cs.nyu.edu/dynamic/masters/prospective-overview/admissions-for-ms-in-computer-science-and-ms-in-information-syst/"
NYU_GSAS = "https://gsas.nyu.edu/admissions/arc/programs/computer-science.html"
BERKELEY_PROGRAM = "https://grad.berkeley.edu/program/eecs-electrical-engineering-and-computer-sciences-meng/"
BERKELEY_GRAD = "https://grad.berkeley.edu/admissions/application-process/requirements/"
BERKELEY_EECS = "https://eecs.berkeley.edu/academics/graduate/industry-programs/meng/"
TORONTO_APPLY = "https://mscac.utoronto.ca/apply/"
TORONTO_CALENDAR = "https://sgs.calendar.utoronto.ca/computer-science-applied-computing-mscac-concentration-computer-science"
TUM_PAGE = "https://www.tum.de/en/studies/degree-programs/detail/data-engineering-and-analytics-master-of-science-msc"
TUM_FPSO = "https://www.tum.de/fileadmin/w00bfo/www/Studium/Studienangebot/Lesbare_Fassung/Master/Data_Engineering_and_Analytics_MA_FPSO_Lesb._Fassung_19082024.pdf"
MELBOURNE_ENTRY = "https://study.unimelb.edu.au/find/courses/graduate/master-of-computer-science/entry-requirements/"
MELBOURNE_APPLY = "https://study.unimelb.edu.au/find/courses/graduate/master-of-computer-science/how-to-apply/"
MELBOURNE_ENGLISH = "https://study.unimelb.edu.au/how-to-apply/english-language-requirements/graduate-english-language-requirements/course-specific-requirements"
NTU_PAGE = "https://www.ntu.edu.sg/education/graduate-programme/master-of-science-in-artificial-intelligence"
NTU_FAQ = "https://www.ntu.edu.sg/computing/admissions/graduate-programmes/master-of-science-programmes/frequently-asked-questions"


def _program(session: Session, university_slug: str, program_slug: str) -> Program:
    program = session.scalar(
        select(Program)
        .join(Department, Program.department_id == Department.id)
        .join(University, Department.university_id == University.id)
        .where(University.slug == university_slug, Program.slug == program_slug)
    )
    if program is None:
        raise RuntimeError(f"missing program {university_slug}/{program_slug}")
    return program


def _save(
    session: Session,
    program: Program,
    *,
    official_url: str,
    duration_months: int | None,
    sources: list[tuple[SourceType, str]],
    intakes: list[IntakeSpec],
) -> None:
    program.official_url = official_url
    if duration_months is not None:
        program.duration_months = duration_months
    uni = program.department.university
    sync_sources(
        session,
        university_id=uni.id,
        department_id=program.department_id,
        program_id=program.id,
        sources=sources,
    )
    for spec in intakes:
        intake = session.scalar(
            select(ProgramIntake).where(
                ProgramIntake.program_id == program.id,
                ProgramIntake.admission_year == spec.admission_year,
                ProgramIntake.entry_month == spec.entry_month,
            )
        )
        if intake is None:
            intake = ProgramIntake(
                program_id=program.id,
                admission_year=spec.admission_year,
                entry_month=spec.entry_month,
                intake_label=spec.intake_label,
                status=IntakeStatus.PUBLISHED,
                last_verified_at=VERIFIED_AT,
            )
            session.add(intake)
            session.flush()
        else:
            intake.intake_label = spec.intake_label
            intake.status = IntakeStatus.PUBLISHED
            intake.last_verified_at = VERIFIED_AT
        replace_intake_children(session, intake, spec)
        print(f"  {uni.slug} / {program.slug} / {spec.admission_year}-{spec.entry_month}")


def main() -> None:
    from datetime import date

    session = SessionLocal()
    try:
        cornell_tuition = [
            TuitionSpec(
                StudentCategory.ALL,
                Decimal("73946"),
                "USD",
                BillingPeriod.PER_YEAR,
                notes=(
                    "2026-27 professional master's Tier 1 rate for M.Eng.: USD 73,946 per year "
                    "(USD 36,973 per semester), published by the Cornell bursar as of 31 March 2026. "
                    "A later intake can be billed at a revised rate."
                ),
            )
        ]
        cornell_languages = [
            LanguageSpec(
                LanguageTestType.TOEFL_IBT,
                notes=(
                    "Revised 1-6 scale section minimums on the CS M.Eng. page: Writing >= 4, "
                    "Listening >= 3.5, Reading >= 4, Speaking >= 5.5. No overall total is published there."
                ),
            ),
            LanguageSpec(
                LanguageTestType.IELTS,
                Decimal("7.0"),
                notes="Overall band 7.0 or higher. No section minimum is stated on the CS M.Eng. page.",
            ),
        ]
        records = [
            (
                "cornell-university",
                "meng-computer-science",
                CORNELL_APPLY,
                None,
                [(SourceType.PROGRAM_PAGE, CORNELL_APPLY), (SourceType.OTHER, CORNELL_TUITION)],
                [
                    IntakeSpec(
                        2027, 9, "Fall 2027",
                        [RoundSpec("Fall admission", deadline=date(2027, 2, 1), applicant_group="all", notes="The department lists February 1 as the fall deadline and does not review applications received after it.")],
                        gre=RequirementStatus.NOT_REQUIRED,
                        gre_note="The CS M.Eng. page says GRE scores are no longer required and are not considered.",
                        recommendation_letters=2,
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        languages=cornell_languages,
                        tuitions=cornell_tuition,
                        gpa_note="The 2.7 GPA figure on this page applies to the Early Admit pathway for current Cornell undergraduates, not to the general applicant pool.",
                    ),
                    IntakeSpec(
                        2027, 1, "Spring 2027",
                        [RoundSpec("Spring admission", deadline=date(2026, 10, 1), applicant_group="all", notes="The department lists October 1 as the spring deadline.")],
                        gre=RequirementStatus.NOT_REQUIRED,
                        gre_note="The CS M.Eng. page says GRE scores are no longer required and are not considered.",
                        recommendation_letters=2,
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        languages=cornell_languages,
                        tuitions=cornell_tuition,
                    ),
                ],
            ),
            (
                "columbia-university",
                "ms-computer-science",
                COLUMBIA_FAQ,
                None,
                [(SourceType.FAQ, COLUMBIA_FAQ), (SourceType.ADMISSION_GUIDELINE, COLUMBIA_SEAS)],
                [
                    IntakeSpec(
                        2027, 9, "Fall 2027",
                        [
                            RoundSpec("Fall priority", deadline=date(2027, 1, 15), applicant_group="all", notes="CS admissions page: fall priority deadline January 15."),
                            RoundSpec("Fall final", deadline=date(2027, 2, 15), applicant_group="all", notes="CS admissions page: fall final deadline February 15. The page lists the month and day; the year is the 2027 fall cycle."),
                        ],
                        gre=RequirementStatus.OPTIONAL,
                        gre_note="SEAS marks GRE optional for the 2026 admission cycle. The CS FAQ says GRE is currently optional and omitting it is not penalized.",
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        interview=RequirementStatus.OPTIONAL,
                        languages=[
                            LanguageSpec(LanguageTestType.TOEFL_IBT, Decimal("101"), notes="CS FAQ recommends 101 and says this is not a strict cutoff. SEAS also accepts TOEFL iBT Home Edition, IELTS, PTE, or Duolingo.", requirement_status=RequirementStatus.RECOMMENDED),
                            LanguageSpec(LanguageTestType.IELTS, Decimal("7.0"), notes="CS FAQ recommends IELTS 7 and says this is not a strict cutoff.", requirement_status=RequirementStatus.RECOMMENDED),
                        ],
                        gpa_note="No published numeric GPA cutoff was on the CS FAQ. SEAS requires three recommendation letters and says an interview may be requested.",
                    ),
                    IntakeSpec(
                        2027, 1, "Spring 2027",
                        [RoundSpec("Spring deadline", deadline=date(2026, 10, 15), applicant_group="all", notes="CS admissions page: spring deadline October 15.")],
                        gre=RequirementStatus.OPTIONAL,
                        gre_note="SEAS marks GRE optional for the 2026 admission cycle. The CS FAQ says GRE is currently optional and omitting it is not penalized.",
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        interview=RequirementStatus.OPTIONAL,
                        languages=[
                            LanguageSpec(LanguageTestType.TOEFL_IBT, Decimal("101"), notes="CS FAQ recommends 101 and says this is not a strict cutoff.", requirement_status=RequirementStatus.RECOMMENDED),
                            LanguageSpec(LanguageTestType.IELTS, Decimal("7.0"), notes="CS FAQ recommends IELTS 7 and says this is not a strict cutoff.", requirement_status=RequirementStatus.RECOMMENDED),
                        ],
                    ),
                ],
            ),
            (
                "new-york-university",
                "ms-computer-science",
                NYU_GSAS,
                None,
                [(SourceType.ADMISSION_GUIDELINE, NYU_GSAS), (SourceType.DEPARTMENT_PAGE, NYU_CS)],
                [
                    IntakeSpec(
                        2027, 9, "Fall 2027",
                        [RoundSpec("Fall admission", deadline=date(2027, 2, 14), applicant_group="all", notes="GSAS Computer Science page: February 14 for fall admission. Materials are due by 5 p.m. Eastern Time.")],
                        gre=RequirementStatus.OPTIONAL,
                        gre_note="GSAS says applicants are not expected or required to submit GRE scores. The department page says GRE is recommended but not required.",
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        languages=[
                            LanguageSpec(LanguageTestType.TOEFL_IBT, Decimal("100"), notes="Department page: successful applicants generally have TOEFL iBT above 100 when a score is required. GSAS requires TOEFL or IELTS unless the applicant is exempt."),
                            LanguageSpec(LanguageTestType.IELTS, Decimal("7.0"), notes="Department page: IELTS minimum band 7.0 when a score is required."),
                        ],
                    ),
                    IntakeSpec(
                        2027, 1, "Spring 2027",
                        [RoundSpec("Spring admission", deadline=date(2026, 11, 1), applicant_group="all", notes="GSAS Computer Science page: November 1 for spring admission.")],
                        gre=RequirementStatus.OPTIONAL,
                        gre_note="GSAS says applicants are not expected or required to submit GRE scores. The department page says GRE is recommended but not required.",
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        languages=[
                            LanguageSpec(LanguageTestType.TOEFL_IBT, Decimal("100"), notes="Department page: successful applicants generally have TOEFL iBT above 100 when a score is required."),
                            LanguageSpec(LanguageTestType.IELTS, Decimal("7.0"), notes="Department page: IELTS minimum band 7.0 when a score is required."),
                        ],
                    ),
                ],
            ),
            (
                "university-of-california-berkeley",
                "meng-eecs",
                BERKELEY_PROGRAM,
                12,
                [
                    (SourceType.PROGRAM_PAGE, BERKELEY_PROGRAM),
                    (SourceType.ADMISSION_GUIDELINE, BERKELEY_GRAD),
                    (SourceType.DEPARTMENT_PAGE, BERKELEY_EECS),
                ],
                [
                    IntakeSpec(
                        2027, 8, "Fall 2027",
                        [RoundSpec("Fall admission", deadline=date(2027, 1, 6), applicant_group="all", notes="Graduate Division program page: fall deadline January 6, 2027. The application opens September 24, 2026 at 12:00 Pacific Time.")],
                        gre=RequirementStatus.NOT_REQUIRED,
                        gre_note="Graduate Division lists GRE as No for this program. The EECS apply page says the department does not require, accept, or consider GRE scores; that page still shows an older deadline.",
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        interview=RequirementStatus.OPTIONAL,
                        gpa_note="Graduate Division minimum is usually GPA 3.0 on a 4.0 scale. The EECS program page also states a 3.0 minimum and an average admitted GPA of 3.7. The program is one academic year.",
                        languages=[
                            LanguageSpec(
                                LanguageTestType.TOEFL_IBT,
                                notes=(
                                    "Graduate Division, for admission starting Fall 2027: tests from 1 June 2025 through 20 January 2026 need 90 total; "
                                    "tests on or after 21 January 2026 need 5 overall on the 1-6 scale, with Speaking and Writing at least 4.5. "
                                    "The EECS program page also says iBT 90 or IELTS 7, and that admitted students average above 100 on the older scale."
                                ),
                            ),
                            LanguageSpec(LanguageTestType.IELTS, Decimal("7.0"), notes="EECS program page: IELTS 7. The same page also says there is no separate minimum beyond the stated iBT 90 / IELTS 7 bar."),
                        ],
                    ),
                ],
            ),
            (
                "university-of-toronto",
                "mscac-computer-science",
                TORONTO_APPLY,
                16,
                [(SourceType.PROGRAM_PAGE, TORONTO_APPLY), (SourceType.ADMISSION_GUIDELINE, TORONTO_CALENDAR)],
                [
                    IntakeSpec(
                        2027, 9, "Fall 2027",
                        [RoundSpec("Fall 2027 application", opens_on=date(2026, 10, 1), deadline=date(2026, 12, 1), applicant_group="all", notes="Applications open 1 October 2026 and close 1 December 2026 at 11:59 p.m. Eastern Time.")],
                        gre=RequirementStatus.RECOMMENDED,
                        gre_note="GRE is not mandatory. Unless the applicant has or is about to receive a Canadian degree, the program strongly recommends submitting GRE scores.",
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        interview=RequirementStatus.OPTIONAL,
                        gpa_note="Calendar: a bachelor's degree in computer science or a related discipline, with standing equivalent to at least B+ in the final year. The program is 16 months. Interviews, if held, run from December through April.",
                        languages=[
                            LanguageSpec(
                                LanguageTestType.TOEFL_IBT,
                                Decimal("4.5"),
                                minimum_writing=Decimal("4.5"),
                                minimum_speaking=Decimal("4.0"),
                                notes="SGS calendar: internet-based TOEFL 4.5/6.0 overall, writing 4.5/6.0, speaking 4.0/6.0. This is the 1-6 scale, not the former 0-120 total.",
                            ),
                            LanguageSpec(
                                LanguageTestType.IELTS,
                                Decimal("7.0"),
                                Decimal("6.5"),
                                Decimal("6.5"),
                                Decimal("6.5"),
                                Decimal("6.5"),
                                notes="SGS calendar: IELTS overall 7.0 with at least 6.5 in each component.",
                            ),
                        ],
                        tuitions=[
                            TuitionSpec(
                                StudentCategory.DOMESTIC,
                                Decimal("33325"),
                                "CAD",
                                BillingPeriod.TOTAL_PROGRAM,
                                notes="Estimate published for the September 2026 start of the full 16-month program, including a CAD 2,200 pre-program fee. The page says registrar fees are posted in mid-July and can change, so this is not a 2027 invoice.",
                            ),
                            TuitionSpec(
                                StudentCategory.INTERNATIONAL,
                                Decimal("90050"),
                                "CAD",
                                BillingPeriod.TOTAL_PROGRAM,
                                notes="Estimate published for the September 2026 start of the full 16-month program, including a CAD 2,200 pre-program fee. The page says registrar fees can change.",
                            ),
                        ],
                    ),
                ],
            ),
            (
                "technical-university-of-munich",
                "msc-data-engineering-and-analytics",
                TUM_PAGE,
                24,
                [(SourceType.PROGRAM_PAGE, TUM_PAGE), (SourceType.ADMISSION_GUIDELINE, TUM_FPSO)],
                [
                    IntakeSpec(
                        2027, 4, "Summer semester 2027",
                        [RoundSpec("Summer semester application", opens_on=date(2026, 10, 1), deadline=date(2026, 11, 30), applicant_group="all", notes="TUM degree page lists the summer-semester window as 1 October to 30 November. Admission is by aptitude assessment, not a written entrance exam.")],
                        gre=RequirementStatus.REQUIRED,
                        gre_note="FPSO: GRE General or GATE is mandatory if the first degree is from China, Bangladesh, India, Iran, or Pakistan. It is recommended for other applicants whose first degree is outside the Lisbon Recognition Convention.",
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        gpa_note="120 ECTS, four semesters, English. A bachelor's in informatics or a comparable program is required. Aptitude assessment applies. Semester student fee listed on the degree page is EUR 97.",
                        languages=[
                            LanguageSpec(LanguageTestType.TOEFL_IBT, Decimal("88"), notes="FPSO: TOEFL at least 88. The regulation does not give the post-January 2026 1-6 scale equivalent. A bachelor's thesis written in English also demonstrates proficiency."),
                            LanguageSpec(LanguageTestType.IELTS, Decimal("6.5"), notes="FPSO: IELTS at least 6.5. Cambridge Main Suite is also accepted; the sentence does not give a Cambridge score."),
                        ],
                        tuitions=[
                            TuitionSpec(StudentCategory.NON_EU, Decimal("6000"), "EUR", BillingPeriod.PER_SEMESTER, Decimal("12000"), notes="Degree page: tuition for international students from third countries is EUR 6,000 per semester."),
                            TuitionSpec(StudentCategory.EU_EEA, Decimal("0"), "EUR", BillingPeriod.PER_SEMESTER, Decimal("0"), notes="The EUR 6,000 charge is stated for students from third countries. EU/EEA students are not in that category. A semester student fee of EUR 97 is listed separately."),
                        ],
                    ),
                    IntakeSpec(
                        2027, 10, "Winter semester 2027/28",
                        [RoundSpec("Winter semester application", opens_on=date(2027, 2, 1), deadline=date(2027, 5, 31), applicant_group="all", notes="TUM degree page lists the winter-semester window as 1 February to 31 May.")],
                        gre=RequirementStatus.REQUIRED,
                        gre_note="FPSO: GRE General or GATE is mandatory if the first degree is from China, Bangladesh, India, Iran, or Pakistan. It is recommended for other applicants whose first degree is outside the Lisbon Recognition Convention.",
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        gpa_note="120 ECTS, four semesters, English. Aptitude assessment applies.",
                        languages=[
                            LanguageSpec(LanguageTestType.TOEFL_IBT, Decimal("88"), notes="FPSO: TOEFL at least 88. A bachelor's thesis written in English also demonstrates proficiency."),
                            LanguageSpec(LanguageTestType.IELTS, Decimal("6.5"), notes="FPSO: IELTS at least 6.5."),
                        ],
                        tuitions=[
                            TuitionSpec(StudentCategory.NON_EU, Decimal("6000"), "EUR", BillingPeriod.PER_SEMESTER, Decimal("12000"), notes="Degree page: EUR 6,000 per semester for international students from third countries."),
                            TuitionSpec(StudentCategory.EU_EEA, Decimal("0"), "EUR", BillingPeriod.PER_SEMESTER, Decimal("0"), notes="The EUR 6,000 charge is stated for students from third countries."),
                        ],
                    ),
                ],
            ),
            (
                "university-of-melbourne",
                "master-of-computer-science",
                MELBOURNE_ENTRY,
                24,
                [
                    (SourceType.PROGRAM_PAGE, MELBOURNE_ENTRY),
                    (SourceType.ADMISSION_GUIDELINE, MELBOURNE_APPLY),
                    (SourceType.OTHER, MELBOURNE_ENGLISH),
                ],
                [
                    IntakeSpec(
                        2027, 3, "March 2027",
                        [RoundSpec("February/March start", deadline=date(2026, 11, 30), applicant_group="all", notes="How to apply: start-year (February intake) applications are due 30 November 2026. The course page lists a March intake and a two-year full-time duration.")],
                        gre=RequirementStatus.NOT_STATED,
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        gpa_note="Entry page: a bachelor's degree in a cognate discipline, weighted average mark 75% or equivalent, plus at least 25 points of university-level mathematics or statistics. Cognate disciplines named there are computer science or equivalent. International tuition was not copied because the fetched pages did not give a program fee amount.",
                        languages=[
                            LanguageSpec(
                                LanguageTestType.IELTS,
                                Decimal("6.5"),
                                Decimal("6.0"),
                                Decimal("6.0"),
                                Decimal("6.0"),
                                Decimal("6.0"),
                                notes="Course entry page: IELTS Academic 6.5 with writing, speaking, reading, and listening 6.0.",
                            ),
                            LanguageSpec(
                                LanguageTestType.TOEFL_IBT,
                                Decimal("81"),
                                minimum_reading=Decimal("16"),
                                minimum_writing=Decimal("19"),
                                minimum_listening=Decimal("16"),
                                minimum_speaking=Decimal("19"),
                                notes="Graduate English table for the 6.5 coursework level used by this course: TOEFL iBT 81, writing 19, speaking 19, reading 16, listening 16.",
                            ),
                        ],
                    ),
                ],
            ),
            (
                "nanyang-technological-university",
                "msc-artificial-intelligence",
                NTU_PAGE,
                None,
                [(SourceType.PROGRAM_PAGE, NTU_PAGE), (SourceType.FAQ, NTU_FAQ)],
                [
                    IntakeSpec(
                        2027, 8, "August 2027",
                        [RoundSpec("August intake", opens_on=date(2026, 11, 1), applicant_group="all", notes="College FAQ: applications open in November for the August intake. The MSAI page that was checked did not state a closing date, so none is stored.")],
                        gre=RequirementStatus.OPTIONAL,
                        gre_note="The MSAI page lists GRE scores as optional. The coursework FAQ says GRE is not required for an MSc by coursework.",
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        gpa_note="A good bachelor's degree in a relevant discipline is required. Reference letters are listed as optional. Full-time students are billed over two semesters; the page does not state the length in months.",
                        languages=[
                            LanguageSpec(LanguageTestType.TOEFL_IBT, Decimal("100"), notes="MSAI page: TOEFL iBT at least 100, or a medium-of-instruction letter. The coursework FAQ uses the same 100 / IELTS 6.5 cutoff when English was not the medium of instruction."),
                            LanguageSpec(LanguageTestType.IELTS, Decimal("6.5"), notes="MSAI page: IELTS at least 6.5, or a medium-of-instruction letter."),
                        ],
                        tuitions=[
                            TuitionSpec(
                                StudentCategory.ALL,
                                Decimal("63220"),
                                "SGD",
                                BillingPeriod.TOTAL_PROGRAM,
                                mandatory_fee=Decimal("5000"),
                                notes="MSAI page: tuition for AY2025/26 and after is SGD 63,220. Deposit SGD 5,000 is deducted from the first bill and is not refundable. Fees include the prevailing GST. Full-time students are billed across two semesters.",
                            )
                        ],
                    ),
                ],
            ),
        ]
        for uni_slug, prog_slug, url, duration, sources, intakes in records:
            program = _program(session, uni_slug, prog_slug)
            _save(session, program, official_url=url, duration_months=duration, sources=sources, intakes=intakes)
        session.commit()
        print("Done. Verified intakes saved for Cornell, Columbia, NYU, Berkeley, Toronto MScAC, TUM Data Engineering and Analytics, Melbourne, and NTU AI.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
