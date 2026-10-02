"""
Fall 2027 requirements for the next unchecked US P0 programs.

Checked against official pages on 2026-09-29. Scores and dates that those
pages do not state are left empty.

Run: docker compose run --rm backend python -m app.seed.p0_us_batch
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.database import SessionLocal
from app.models.enums import LanguageTestType, RequirementStatus, SourceType
from app.seed.ku_utokyo import IntakeSpec, LanguageSpec, RoundSpec
from app.seed.verified_intakes import _program, _save

CMU_SCS = "https://www.cs.cmu.edu/education/graduate-admissions"
CMU_MSCS = "https://csd.cmu.edu/academics/masters/admissions"
CMU_MSAII = "https://www.lti.cs.cmu.edu/academics/masters-programs/msaii.html"
CMU_MSML = "https://ml.cmu.edu/academics/primary-ms-machine-learning-masters"
CMU_MSE = "https://mse.s3d.cmu.edu/applicants/mse-as/apply.html"
GT_REQ = "https://www.cc.gatech.edu/ms-computer-science-admission-requirements"
UIUC_DEADLINES = "https://siebelschool.illinois.edu/admissions/graduate/application-deadlines"
UIUC_PROCESS = "https://siebelschool.illinois.edu/admissions/graduate/applications-process-requirements"
UIUC_MCS = "https://siebelschool.illinois.edu/academics/graduate/professional-mcs/app-info"
UIUC_MCS_CAMPUS = "https://siebelschool.illinois.edu/academics/graduate/professional-mcs/campus-master-computer-science"
UT_APPLY = "https://www.cs.utexas.edu/graduate/apply"
UT_GRAD = "https://www.gradschool.utexas.edu/degrees-programs"

CMU_EARLY = RoundSpec(
    "Early deadline",
    deadline=date(2026, 11, 18),
    opens_on=date(2026, 9, 9),
    applicant_group="all",
    notes="SCS early deadline is 18 November 2026 at 3 p.m. EST. The application opens 9 September 2026.",
)
CMU_FINAL = RoundSpec(
    "Final deadline",
    deadline=date(2026, 12, 9),
    applicant_group="all",
    notes="SCS final deadline is 9 December 2026 at 3 p.m. EST.",
)
CMU_LANG = [
    LanguageSpec(
        LanguageTestType.TOEFL_IBT,
        notes=(
            "Required for F-1 or J-1 applicants whose native language is not English. "
            "SCS does not publish a numeric minimum. It says most admitted applicants in recent years scored TOEFL iBT 105-114. "
            "TOEFL ITP Plus for China is discouraged because speaking is not scored. No waiver for prior English-medium study."
        ),
    ),
    LanguageSpec(
        LanguageTestType.IELTS,
        notes="Accepted. SCS says most admitted applicants in recent years scored IELTS 7-8. No numeric minimum is published.",
    ),
    LanguageSpec(
        LanguageTestType.DUOLINGO,
        notes="Accepted if TOEFL or IELTS is not possible. SCS says most admitted applicants in recent years scored 130-155. No numeric minimum is published.",
    ),
]


def main() -> None:
    session = SessionLocal()
    try:
        records = [
            (
                "carnegie-mellon-university",
                "ms-computer-science",
                CMU_MSCS,
                None,
                [(SourceType.PROGRAM_PAGE, CMU_MSCS), (SourceType.ADMISSION_GUIDELINE, CMU_SCS)],
                [
                    IntakeSpec(
                        2027, 8, "Fall 2027",
                        [CMU_EARLY, CMU_FINAL],
                        gre=RequirementStatus.RECOMMENDED,
                        gre_note="CSD says GRE is strongly recommended, especially without clear evidence of mathematical proficiency, and is waived for current or former Carnegie Mellon students. Applicants who omit it should explain why in the statement of purpose.",
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        gpa_note="Fall entry only; students cannot begin in the spring. The program does not offer scholarships. Tuition amounts were not copied because the linked bursar page was not the source of a figure stored here.",
                        languages=CMU_LANG,
                    ),
                ],
            ),
            (
                "carnegie-mellon-university",
                "ms-artificial-intelligence",
                CMU_MSAII,
                None,
                [(SourceType.PROGRAM_PAGE, CMU_MSAII), (SourceType.ADMISSION_GUIDELINE, CMU_SCS)],
                [
                    IntakeSpec(
                        2027, 8, "Fall 2027",
                        [CMU_EARLY, CMU_FINAL],
                        gre=RequirementStatus.REQUIRED,
                        gre_note="The LTI page for MS in Artificial Intelligence and Innovation says GRE is required. Institution code 2074, department code 0402.",
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        gpa_note="LTI page: GPA of 3.0 or higher, reported on the original scale rather than converted to a US GPA. SCS says this program has a required internship. The catalog name AI is this degree, not a separate MS Artificial Intelligence.",
                        languages=CMU_LANG,
                    ),
                ],
            ),
            (
                "carnegie-mellon-university",
                "ms-machine-learning",
                CMU_MSML,
                None,
                [(SourceType.PROGRAM_PAGE, CMU_MSML), (SourceType.ADMISSION_GUIDELINE, CMU_SCS)],
                [
                    IntakeSpec(
                        2027, 8, "August 2027",
                        [CMU_EARLY, CMU_FINAL],
                        gre=RequirementStatus.NOT_STATED,
                        gre_note="The MSML page says GRE was optional for the Fall 2025 application, which started in August 2026. It does not state the GRE rule for the August 2027 start, so no 2027 GRE status is stored.",
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        gpa_note="Students begin in August. Applications are accepted once a year. Profile statistics on the page are not stored as cutoffs.",
                        languages=CMU_LANG,
                    ),
                ],
            ),
            (
                "carnegie-mellon-university",
                "ms-software-engineering",
                CMU_MSE,
                None,
                [(SourceType.PROGRAM_PAGE, CMU_MSE), (SourceType.ADMISSION_GUIDELINE, CMU_SCS)],
                [
                    IntakeSpec(
                        2027, 8, "Fall 2027",
                        [
                            RoundSpec(
                                "Application deadline",
                                opens_on=date(2026, 9, 9),
                                deadline=date(2026, 12, 9),
                                applicant_group="all",
                                notes="MSE does not use the SCS early deadline. The fee is $100. Coding-assessment invitations go out on 11 December 2026, and the assessment is due 17 December 2026.",
                            )
                        ],
                        gre=RequirementStatus.OPTIONAL,
                        gre_note="GRE is optional. An application without scores is not at a disadvantage. Applicants who have scores are encouraged to submit them. The at-home GRE is accepted.",
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.REQUIRED,
                        gpa_note="Cumulative QPA higher than 2.5. A coding assessment is required after the deadline. The page says students are accepted with both strong and weak programming ability, and it does not publish a passing score. This row is the on-campus MSE Applied Study, not MSE Online.",
                        languages=CMU_LANG,
                    ),
                ],
            ),
            (
                "georgia-institute-of-technology",
                "ms-computer-science",
                GT_REQ,
                None,
                [(SourceType.ADMISSION_GUIDELINE, GT_REQ)],
                [
                    IntakeSpec(
                        2027, 8, "Fall 2027",
                        [
                            RoundSpec(
                                "Fall admission",
                                deadline=date(2027, 2, 1),
                                applicant_group="all",
                                notes="Atlanta-campus MSCS admits once a year. The deadline is 1 February for the following fall. The FAQ allows recommendation letters until 14 February. This is not the online OMSCS.",
                            )
                        ],
                        gre=RequirementStatus.OPTIONAL,
                        gre_note="The current admission-requirements page says GRE is not required and will be considered if provided. The 2025-26 handbook still says GRE is required and waivers are unavailable; the requirements page is the later statement because it also gives the 2026 TOEFL scale.",
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        gpa_note="Desirable minimum GPA is 3.0/4.0. Most admitted applicants are higher. No tuition figure is stored; the page points to the bursar schedule.",
                        languages=[
                            LanguageSpec(
                                LanguageTestType.TOEFL_IBT,
                                Decimal("100"),
                                notes="Department minimum is 100 on the older 0-120 scale. From January 2026 the six-point scale minimum is 5.0.",
                            ),
                            LanguageSpec(
                                LanguageTestType.IELTS,
                                Decimal("7.5"),
                                Decimal("6.5"),
                                Decimal("5.5"),
                                Decimal("6.5"),
                                Decimal("6.5"),
                                notes="Overall 7.5. Reading 6.5, listening 6.5, speaking 6.5, writing 5.5.",
                            ),
                        ],
                    ),
                ],
            ),
            (
                "university-of-illinois-urbana-champaign",
                "mscs",
                UIUC_DEADLINES,
                None,
                [(SourceType.ADMISSION_GUIDELINE, UIUC_DEADLINES), (SourceType.ADMISSION_GUIDELINE, UIUC_PROCESS)],
                [
                    IntakeSpec(
                        2027, 8, "Fall 2027",
                        [
                            RoundSpec(
                                "Fall admission",
                                deadline=date(2026, 12, 1),
                                applicant_group="all",
                                notes="M.S. in Computer Science is fall only. Deadline 1 December, 11:59 p.m. US Central Time. Decision target listed as 15 March.",
                            )
                        ],
                        gre=RequirementStatus.RECOMMENDED,
                        gre_note="The applications page says GRE general and subject scores are recommended but not required. Official ETS delivery is not required if a PDF of the score report is uploaded.",
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        gpa_note="The same page says applicants with TOEFL iBT speaking below 22 have a low chance of admission. That sentence is not stored as a minimum score. No numeric admission cutoff for TOEFL or IELTS was on the pages checked.",
                        languages=[
                            LanguageSpec(
                                LanguageTestType.TOEFL_IBT,
                                notes="No numeric admission minimum was published on the pages checked. Speaking below 22 is described as a low chance of admission, not as a cutoff.",
                            ),
                            LanguageSpec(
                                LanguageTestType.IELTS,
                                notes="IELTS is accepted. No numeric admission minimum was published on the pages checked.",
                            ),
                        ],
                    ),
                ],
            ),
            (
                "university-of-illinois-urbana-champaign",
                "mcs",
                UIUC_MCS,
                None,
                [
                    (SourceType.PROGRAM_PAGE, UIUC_MCS),
                    (SourceType.ADMISSION_GUIDELINE, UIUC_DEADLINES),
                    (SourceType.DEPARTMENT_PAGE, UIUC_MCS_CAMPUS),
                ],
                [
                    IntakeSpec(
                        2027, 8, "Fall 2027, Urbana-Champaign",
                        [
                            RoundSpec(
                                "Fall admission",
                                deadline=date(2027, 5, 1),
                                applicant_group="all",
                                notes="Master of Computer Science in Urbana-Champaign. Deadline 1 May, 11:59 p.m. US Central Time. This row is not the Chicago campus or the online MCS.",
                            )
                        ],
                        gre=RequirementStatus.NOT_REQUIRED,
                        gre_note="The MCS application page says the school does not require GRE scores for any of its graduate programs.",
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        gpa_note="Recommended undergraduate GPA is 3.2/4.0 or higher. Letters of recommendation are not required and are considered if submitted. The campus page says the degree can be completed in as little as three semesters and has no thesis.",
                    ),
                    IntakeSpec(
                        2027, 1, "Spring 2027, Urbana-Champaign",
                        [
                            RoundSpec(
                                "Spring admission",
                                deadline=date(2026, 10, 15),
                                applicant_group="all",
                                notes="Master of Computer Science in Urbana-Champaign. Deadline 15 October, 11:59 p.m. US Central Time.",
                            )
                        ],
                        gre=RequirementStatus.NOT_REQUIRED,
                        gre_note="The MCS application page says the school does not require GRE scores for any of its graduate programs.",
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        gpa_note="Recommended undergraduate GPA is 3.2/4.0 or higher. Letters of recommendation are not required.",
                    ),
                ],
            ),
            (
                "university-of-texas-at-austin",
                "ms-computer-science",
                UT_APPLY,
                None,
                [(SourceType.PROGRAM_PAGE, UT_APPLY), (SourceType.ADMISSION_GUIDELINE, UT_GRAD)],
                [
                    IntakeSpec(
                        2027, 8, "Fall 2027",
                        [
                            RoundSpec(
                                "Fall admission",
                                opens_on=date(2026, 10, 15),
                                deadline=date(2026, 12, 15),
                                applicant_group="all",
                                notes="CS apply page lists 15 October and 15 December without a year. The graduate school lists residential Computer Science MSCS as fall only, deadline 15 December. Recommendation letters are due 20 December. This is not the online MSCS.",
                            )
                        ],
                        gre=RequirementStatus.NOT_STATED,
                        gre_note="The CS apply page says GRE is optional for Fall 2025. It does not state the Fall 2027 rule, so this intake does not store a GRE status.",
                        recommendation_letters=3,
                        entrance_exam=RequirementStatus.NOT_REQUIRED,
                        gpa_note="GPA of 3.0 or higher on a 4.0 scale in upper-division coursework and any completed graduate work. At least three recommendation letters. No TOEFL or IELTS number was on the CS apply page.",
                    ),
                ],
            ),
        ]
        ai = _program(session, "carnegie-mellon-university", "ms-artificial-intelligence")
        ai.name_en = "MS in Artificial Intelligence and Innovation"
        for uni_slug, prog_slug, url, duration, sources, intakes in records:
            program = _program(session, uni_slug, prog_slug)
            _save(session, program, official_url=url, duration_months=duration, sources=sources, intakes=intakes)
        session.commit()
        print("Done. CMU, Georgia Tech, UIUC, and UT Austin intakes saved.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
