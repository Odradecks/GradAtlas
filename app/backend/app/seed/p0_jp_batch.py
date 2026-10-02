"""
April 2027 requirements from official Japanese master's guides checked on 2026-09-29.

The stored rows are the selections named below. Other selections at the same
graduate school are not copied across.

Run: docker compose run --rm backend python -m app.seed.p0_jp_batch
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.database import SessionLocal
from app.models.enums import BillingPeriod, LanguageTestType, RequirementStatus, SourceType, StudentCategory
from app.seed.ku_utokyo import IntakeSpec, LanguageSpec, RoundSpec, TuitionSpec
from app.seed.verified_intakes import _program, _save

KYOTO_PDF = "https://www.i.kyoto-u.ac.jp/assets/pdf/admission/application/master-2027-4-en.pdf"
KYOTO_PAGE = "https://www.i.kyoto-u.ac.jp/en/admission/application/"
OSAKA_PDF = "https://www.ist.osaka-u.ac.jp/files/examinees/admission/2027/16_a_EN2027.pdf"
OSAKA_PAGE = "https://www.ist.osaka-u.ac.jp/english/examinees/admission/guidelines2027.php"
NAIST_PDF = "https://www.naist.jp/en/international_students/prospective_students/admission_information/file/2027_Master's_course.pdf"
NAIST_PAGE = "https://www.naist.jp/en/international_students/prospective_students/admission_information/guidelines.html"
JAIST_PDF = "https://www.jaist.ac.jp/admissions/data/0.clickhere_Me_2027.4.pdf"
JAIST_PAGE = "https://www.jaist.ac.jp/english/admissions/application-guide/guide-m.html"
ISCT_PAGE = "https://admissions.isct.ac.jp/en/013/graduate/programs/science-and-engineering/igp-c"
ISCT_PDF = "https://admissions.isct.ac.jp/plugins/cms/component_download_file.php?contentsDataId=&contentsId=&fileName=Application+Guide_IGP%28C%29_2027+spring&key=8c14c37a165da34e08cbe525e60a22ba.pdf&pageId=5837&prevId=&type=1"


def tuition(annual: str, admission: str, notes: str) -> list[TuitionSpec]:
    return [
        TuitionSpec(
            StudentCategory.ALL,
            Decimal(annual),
            "JPY",
            BillingPeriod.PER_YEAR,
            mandatory_fee=Decimal(admission),
            notes=notes,
        )
    ]


def kyoto() -> list[IntakeSpec]:
    return [
        IntakeSpec(
            2027,
            4,
            "April 2027",
            [
                RoundSpec(
                    "August 2026 entrance examination",
                    opens_on=date(2026, 6, 5),
                    deadline=date(2026, 6, 19),
                    exam_date=date(2026, 8, 1),
                    applicant_group="all",
                    notes=(
                        "Postal applications must arrive between 5 June and 17:00 on 19 June 2026. "
                        "In-person submission is 19 June 2026, 10:00-17:00, closed 12:00-13:30. "
                        "Written examinations are on 1 August 2026. Oral examinations are on 2 August. "
                        "3 August is the alternative date. The examination fee is 30,000 yen, plus a 671 yen transaction fee. "
                        "Subjects differ by course. This row does not copy one course's subject list onto the others."
                    ),
                )
            ],
            gre=RequirementStatus.NOT_STATED,
            recommendation_letters=None,
            entrance_exam=RequirementStatus.REQUIRED,
            interview=RequirementStatus.REQUIRED,
            professor_contact=RequirementStatus.NOT_STATED,
            gpa_note=(
                "Master's program, April 2027, August 2026 examination. "
                "Courses include Intelligence Science and Technology, Social Informatics, Advanced Mathematical Sciences, "
                "Applied Mathematics and Physics, Systems Science, Communications and Computer Engineering, and Data Science. "
                "For Intelligence Science and Technology, Social Informatics, Advanced Mathematical Sciences, and Systems Science, "
                "only some applicants proceed to the oral examination. "
                "The Japanese guideline is the authoritative text."
            ),
            languages=[
                LanguageSpec(
                    LanguageTestType.TOEFL_IBT,
                    notes=(
                        "TOEFL iBT or TOEIC, taken within two years before the application deadline. "
                        "TOEFL iBT Home Edition is accepted. TOEFL ITP is not. "
                        "No minimum score is published. A missing score is recorded as zero. IELTS is not listed."
                    ),
                )
            ],
            tuitions=tuition(
                "535800",
                "282000",
                "Admission fee 282,000 yen and annual tuition 535,800 yen, both marked tentative. "
                "The examination fee is separate and is not this admission fee. MEXT scholarship students are exempt.",
            ),
        )
    ]


def osaka() -> list[IntakeSpec]:
    return [
        IntakeSpec(
            2027,
            4,
            "April 2027, ITSCE",
            [
                RoundSpec(
                    "Pre-application screening",
                    opens_on=date(2026, 9, 28),
                    deadline=date(2026, 10, 2),
                    applicant_group="all",
                    notes="Results are sent on 14 October 2026. Every applicant needs this screening, and must already have confirmation from the expected supervisor.",
                ),
                RoundSpec(
                    "Application and interview",
                    opens_on=date(2026, 10, 26),
                    deadline=date(2026, 10, 30),
                    exam_date=date(2026, 11, 24),
                    applicant_group="all",
                    notes=(
                        "Application documents arrive 26-30 October 2026. "
                        "The interview is scheduled on one day from 24 November through 5 December 2026, online or in person. "
                        "Results are posted at 14:00 on 18 December 2026. The examination fee is 30,000 yen."
                    ),
                ),
            ],
            gre=RequirementStatus.NOT_STATED,
            recommendation_letters=2,
            entrance_exam=RequirementStatus.REQUIRED,
            interview=RequirementStatus.REQUIRED,
            professor_contact=RequirementStatus.REQUIRED,
            gpa_note=(
                "This row is the Information Technology Special Course in English for April 2027, the December selection. "
                "Classes are conducted in English. It is not the Japanese-language general selection, and not the summer special selection for international applicants. "
                "The graduate school plans to merge several departments into one Department of Information Science and Technology on 1 April 2027."
            ),
            languages=[
                LanguageSpec(
                    LanguageTestType.TOEFL_IBT,
                    notes=(
                        "Submit one of TOEIC, TOEFL, or IELTS dated from October 2024. "
                        "TOEFL iBT must be from a single test date. MyBest scores are not accepted. "
                        "TOEFL ITP, TOEIC Institutional Program, and IELTS General Training are not accepted. "
                        "No numeric minimum is published. A supervisor may confirm that a native speaker, or a graduate of an English-medium institution, need not submit a score."
                    ),
                ),
                LanguageSpec(
                    LanguageTestType.IELTS,
                    notes="IELTS Academic Test Report Form must be an original, not a copy. The same waiver as TOEFL may apply after consulting the supervisor.",
                ),
            ],
            tuitions=tuition(
                "535800",
                "282000",
                "Admission fee 282,000 yen. Annual tuition 535,800 yen, withdrawn as two installments of 267,900 yen. "
                "Figures are those valid as of April 2026 and may change. MEXT scholarship students are exempt at entrance.",
            ),
        )
    ]


def naist_languages() -> list[LanguageSpec]:
    return [
        LanguageSpec(
            LanguageTestType.TOEFL_IBT,
            notes=(
                "English scores are optional. Omitting them records the English score as zero. "
                "Accepted TOEFL types include iBT, ITP, Essentials, and iBT Home Edition. "
                "TOEIC, IELTS, and Duolingo are also accepted. No numeric minimum is published."
            ),
            requirement_status=RequirementStatus.OPTIONAL,
        )
    ]


def naist_exam(name: str, opens: date, deadline: date, exam: date, notes: str) -> RoundSpec:
    return RoundSpec(
        name,
        opens_on=opens,
        deadline=deadline,
        exam_date=exam,
        applicant_group="all",
        exam_subjects=[
            "Mathematics: algebra and analysis",
            "Research proposal and the applicant's area of information science",
        ],
        notes=notes,
    )


def naist() -> list[IntakeSpec]:
    shared = (
        "The guide titles these Spring 2027 and Fall 2027. It does not print the words April or October. "
        "Information Science oral examination is about 20 minutes, in Japanese or English, online. "
        "Foreign nationals who are not permanent residents must finish a pre-application at least two months before the application period. "
        "The examination fee is 30,000 yen. Biological Science and Materials Science use different oral formats and are not stored here."
    )
    fees = tuition(
        "535800",
        "282000",
        "Provisional admission fee 282,000 yen. Provisional tuition 267,900 yen per semester, 535,800 yen for the year.",
    )
    return [
        IntakeSpec(
            2027,
            4,
            "Spring 2027",
            [
                naist_exam(
                    "1st examination",
                    date(2026, 6, 8),
                    date(2026, 6, 10),
                    date(2026, 7, 6),
                    "Online registration closes at 23:59 JST on the last day. Interview window 6-11 July 2026. Results at 10:00 on 21 July 2026. " + shared,
                ),
                naist_exam(
                    "2nd examination",
                    date(2026, 9, 28),
                    date(2026, 9, 30),
                    date(2026, 10, 27),
                    "Interview window 27-29 October 2026. Results at 10:00 on 6 November 2026. " + shared,
                ),
            ],
            gre=RequirementStatus.NOT_STATED,
            entrance_exam=RequirementStatus.REQUIRED,
            interview=RequirementStatus.REQUIRED,
            professor_contact=RequirementStatus.NOT_STATED,
            gpa_note="Information Science capacity in the guide is 175, including fall entrants and the Advanced Information Specialist Course. No GPA cutoff is published.",
            languages=naist_languages(),
            tuitions=fees,
        ),
        IntakeSpec(
            2027,
            10,
            "Fall 2027",
            [
                naist_exam(
                    "1st examination for fall admission",
                    date(2027, 2, 8),
                    date(2027, 2, 10),
                    date(2027, 3, 10),
                    "The guide also calls this the Spring 3rd examination. Interview date 10 March 2027. Results at 10:00 on 15 March 2027. Enrollment procedures are in late September 2027. " + shared,
                )
            ],
            gre=RequirementStatus.NOT_STATED,
            entrance_exam=RequirementStatus.REQUIRED,
            interview=RequirementStatus.REQUIRED,
            professor_contact=RequirementStatus.NOT_STATED,
            gpa_note="The second fall 2027 examination guide was not published when this page was checked. It is not stored.",
            languages=naist_languages(),
            tuitions=fees,
        ),
    ]


def jaist() -> list[IntakeSpec]:
    oral = [
        "Short essay presentation, within 7 minutes",
        "Questions on the short essay and entry form, within 23 minutes",
    ]
    regular_note = (
        "Regular examination. One designated day in the examination window, online, within 30 minutes. "
        "Applicants living outside Japan cannot use this examination. "
        "The screening fee is 30,000 yen. Applicants choose Knowledge Science, Information Science, or Materials Science. This row is the Information Science choice."
    )
    return [
        IntakeSpec(
            2027,
            4,
            "April 2027",
            [
                RoundSpec(
                    "Regular examination, 1st",
                    opens_on=date(2026, 5, 27),
                    deadline=date(2026, 6, 8),
                    exam_date=date(2026, 7, 4),
                    applicant_group="in_japan",
                    exam_subjects=oral,
                    notes=regular_note + " Examination window 4-5 July 2026. Decision date 17 July 2026.",
                ),
                RoundSpec(
                    "Regular examination, 2nd",
                    opens_on=date(2026, 9, 4),
                    deadline=date(2026, 9, 16),
                    exam_date=date(2026, 10, 17),
                    applicant_group="in_japan",
                    exam_subjects=list(oral),
                    notes=regular_note + " Examination window 17-18 October 2026. Decision date 30 October 2026.",
                ),
                RoundSpec(
                    "Regular examination, 3rd",
                    opens_on=date(2026, 11, 19),
                    deadline=date(2026, 12, 1),
                    exam_date=date(2027, 1, 9),
                    applicant_group="in_japan",
                    exam_subjects=list(oral),
                    notes=regular_note + " Examination window 9-10 January 2027. Decision date 26 January 2027.",
                ),
                RoundSpec(
                    "Examination for overseas residents",
                    opens_on=date(2026, 11, 4),
                    deadline=date(2026, 11, 26),
                    applicant_group="outside_japan",
                    notes=(
                        "Postmark within 4-26 November 2026. Informal consent from the intended supervisor is required before applying. "
                        "Optional document pre-check closes 12 November 2026. "
                        "The interview date is assigned individually and may be online, in English or Japanese. "
                        "Decision date 26 January 2027. Admission procedures in late February 2027. "
                        "The screening fee is 30,000 yen."
                    ),
                ),
            ],
            gre=RequirementStatus.NOT_STATED,
            entrance_exam=RequirementStatus.REQUIRED,
            interview=RequirementStatus.REQUIRED,
            professor_contact=RequirementStatus.REQUIRED,
            gpa_note=(
                "Prior laboratory consent is required for the overseas-residents examination. "
                "The regular examination does not use that consent step, and it is closed to applicants living outside Japan. "
                "The recommendation track and the rolling examination are separate and are not stored."
            ),
            languages=[
                LanguageSpec(
                    LanguageTestType.TOEFL_IBT,
                    notes=(
                        "Applicants who graduated outside Japan must submit one English or Japanese certificate. "
                        "English options are TOEIC Listening and Reading, TOEFL iBT, or IELTS Academic. "
                        "No numeric minimum is published."
                    ),
                )
            ],
            tuitions=tuition(
                "535800",
                "282000",
                "Entrance fee 282,000 yen. Tuition 267,900 yen for a half year and 535,800 yen for a year. "
                "If the fees change before enrollment, the new amounts apply. MEXT scholarship students are exempt.",
            ),
        )
    ]


def isct() -> list[IntakeSpec]:
    return [
        IntakeSpec(
            2027,
            4,
            "April 2027, IGP(C)",
            [
                RoundSpec(
                    "IGP(C) application",
                    opens_on=date(2026, 8, 3),
                    deadline=date(2026, 10, 11),
                    applicant_group="all",
                    notes=(
                        "Online application closes at 23:59 JST on 11 October 2026. "
                        "A copy of the supervisor's consent letter must reach the Admissions Division by 23:59 JST on 4 October 2026. "
                        "The application fee is 30,000 yen. A system usage fee is charged on top, and the guide does not state its amount. "
                        "The program page lists a result time of 15:00 on 3 December 2026."
                    ),
                )
            ],
            gre=RequirementStatus.NOT_STATED,
            recommendation_letters=1,
            entrance_exam=RequirementStatus.NOT_STATED,
            interview=RequirementStatus.NOT_STATED,
            professor_contact=RequirementStatus.REQUIRED,
            gpa_note=(
                "The program page says there is no Japanese-language requirement and that lectures and seminars are in English. "
                "Master's students are expected to finish within two years and take at least 30 credits. "
                "The guide does not publish a TOEFL, IELTS, or GRE score, and it does not describe a written examination or an interview. "
                "This row is the April 2027 IGP(C) master's application. The fall intake is a different call and is not stored."
            ),
            tuitions=tuition(
                "635400",
                "282000",
                "Enrollment fee 282,000 yen. Annual tuition 635,400 yen. Both are subject to change. "
                "This is the figure in the IGP(C) guide, not the 535,800 yen figure used by the other national universities in this batch.",
            ),
        )
    ]


def main() -> None:
    session = SessionLocal()
    try:
        osaka_program = _program(session, "osaka-university", "graduate-school-of-information-science-and-technology")
        osaka_program.name_en = "Information Technology Special Course in English"
        computing = _program(session, "institute-of-science-tokyo", "school-of-computing")
        computing.name_en = "School of Computing (IGP C)"
        ice = _program(session, "institute-of-science-tokyo", "information-and-communications")
        ice.name_en = "Information and Communications Engineering (IGP C)"

        records = [
            (
                "kyoto-university",
                "graduate-school-of-informatics",
                KYOTO_PDF,
                None,
                [(SourceType.ADMISSION_GUIDELINE, KYOTO_PDF), (SourceType.ADMISSION_GUIDELINE, KYOTO_PAGE)],
                kyoto(),
            ),
            (
                "osaka-university",
                "graduate-school-of-information-science-and-technology",
                OSAKA_PDF,
                None,
                [(SourceType.PROGRAM_PAGE, OSAKA_PDF), (SourceType.ADMISSION_GUIDELINE, OSAKA_PAGE)],
                osaka(),
            ),
            (
                "nara-institute-of-science-and-technology",
                "information-science",
                NAIST_PAGE,
                None,
                [(SourceType.ADMISSION_GUIDELINE, NAIST_PDF), (SourceType.ADMISSION_GUIDELINE, NAIST_PAGE)],
                naist(),
            ),
            (
                "japan-advanced-institute-of-science-and-technology",
                "information-science",
                JAIST_PAGE,
                None,
                [(SourceType.ADMISSION_GUIDELINE, JAIST_PDF), (SourceType.ADMISSION_GUIDELINE, JAIST_PAGE)],
                jaist(),
            ),
            (
                "institute-of-science-tokyo",
                "school-of-computing",
                ISCT_PAGE,
                24,
                [(SourceType.PROGRAM_PAGE, ISCT_PAGE), (SourceType.ADMISSION_GUIDELINE, ISCT_PDF)],
                isct(),
            ),
            (
                "institute-of-science-tokyo",
                "information-and-communications",
                ISCT_PAGE,
                24,
                [(SourceType.PROGRAM_PAGE, ISCT_PAGE), (SourceType.ADMISSION_GUIDELINE, ISCT_PDF)],
                isct(),
            ),
        ]
        for uni_slug, prog_slug, url, duration, sources, intakes in records:
            program = _program(session, uni_slug, prog_slug)
            _save(session, program, official_url=url, duration_months=duration, sources=sources, intakes=intakes)
        session.commit()
        print("Done. Kyoto, Osaka ITSCE, NAIST, JAIST, and Science Tokyo IGP(C) saved.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
