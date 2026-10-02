from decimal import Decimal

from pydantic import BaseModel, Field


class LanguageOut(BaseModel):
    test_type: str
    minimum_overall: Decimal | None
    minimum_reading: Decimal | None = None
    minimum_writing: Decimal | None = None
    minimum_listening: Decimal | None = None
    minimum_speaking: Decimal | None = None
    requirement_status: str
    notes: str | None = None


class TuitionOut(BaseModel):
    student_category: str
    amount: Decimal | None
    currency: str | None
    billing_period: str
    normalized_annual_eur: Decimal | None
    mandatory_fee: Decimal | None = None
    notes: str | None = None


class ExamSubjectOut(BaseModel):
    subject: str
    notes: str | None


class ApplicationRoundOut(BaseModel):
    name: str
    applicant_group: str | None
    opens_on: str | None
    deadline: str | None
    exam_date: str | None
    notes: str | None
    exam_subjects: list[ExamSubjectOut]


class SourceOut(BaseModel):
    source_type: str
    url: str


class ProgramListItem(BaseModel):
    intake_id: int
    university_name: str
    city: str | None = None
    country_code: str
    verified: bool = False
    program_name: str
    program_slug: str
    degree_type: str | None
    fields: list[str]
    admission_year: int
    entry_month: int
    intake_label: str | None
    gre_requirement: str | None
    gre_note: str | None = None
    entrance_exam_status: str | None
    languages: list[LanguageOut]
    tuitions: list[TuitionOut]
    sources: list[SourceOut]
    official_url: str | None


class ProgramListResponse(BaseModel):
    total: int
    items: list[ProgramListItem]


class IntakeDocumentOut(BaseModel):
    id: int
    title: str | None
    document_type: str
    language: str | None
    admission_year: int | None
    source_url: str
    chunk_count: int


class CitationOut(BaseModel):
    chunk_id: int
    heading_path: str | None
    text: str
    source_url: str
    document_title: str | None
    admission_year: int | None
    page_start: int | None = None
    page_end: int | None = None
    university_name: str | None = None
    program_name: str | None = None


class AskIn(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class CompareAskIn(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    intake_ids: list[int] = Field(min_length=2, max_length=4)


class AskOut(BaseModel):
    status: str
    answer: str
    citations: list[CitationOut]


class IntakeDetail(ProgramListItem):
    department_name: str
    gpa_note: str | None
    gre_note: str | None
    recommendation_letter_count: int | None
    professor_contact_status: str | None
    interview_status: str | None
    rounds: list[ApplicationRoundOut]
    documents: list[IntakeDocumentOut]


class FieldOption(BaseModel):
    slug: str
    name: str


class UniversityOption(BaseModel):
    slug: str
    name: str
    country_code: str


class ProgramFilterOptions(BaseModel):
    countries: list[str]
    universities: list[UniversityOption]
    fields: list[FieldOption]
    admission_years: list[int]
    entry_months: list[int] = Field(description="Calendar month of entry, 1-12")


class CatalogProgramItem(BaseModel):
    university_slug: str
    university_name: str
    country_code: str
    website_url: str | None
    program_slug: str
    program_name: str
    degree_type: str | None
    fields: list[str]
    priority: str | None
    official_url: str | None
    intake_count: int


class CatalogProgramResponse(BaseModel):
    total: int
    items: list[CatalogProgramItem]
