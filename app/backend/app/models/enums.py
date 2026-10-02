import enum


class IntakeStatus(str, enum.Enum):
    PUBLISHED = "published"
    TBD = "tbd"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class RequirementStatus(str, enum.Enum):
    REQUIRED = "required"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"
    NOT_REQUIRED = "not_required"
    NOT_STATED = "not_stated"
    UNKNOWN = "unknown"


class GpaRequirementType(str, enum.Enum):
    MINIMUM = "minimum"
    RECOMMENDED = "recommended"
    RANGE = "range"
    PERCENTILE = "percentile"
    NOT_STATED = "not_stated"
    UNKNOWN = "unknown"


class LanguageTestType(str, enum.Enum):
    IELTS = "ielts"
    TOEFL_IBT = "toefl_ibt"
    TOEFL_PBT = "toefl_pbt"
    CAMBRIDGE = "cambridge"
    PTE = "pte"
    DUOLINGO = "duolingo"
    OTHER = "other"


class StudentCategory(str, enum.Enum):
    ALL = "all"
    EU_EEA = "eu_eea"
    NON_EU = "non_eu"
    DOMESTIC = "domestic"
    INTERNATIONAL = "international"


class BillingPeriod(str, enum.Enum):
    PER_YEAR = "per_year"
    PER_SEMESTER = "per_semester"
    PER_TERM = "per_term"
    TOTAL_PROGRAM = "total_program"


class SourceType(str, enum.Enum):
    ADMISSION_GUIDELINE = "admission_guideline"
    PROGRAM_PAGE = "program_page"
    FAQ = "faq"
    CURRICULUM = "curriculum"
    DEPARTMENT_PAGE = "department_page"
    LAB_PAGE = "lab_page"
    OTHER = "other"


class DocumentType(str, enum.Enum):
    ADMISSION_GUIDELINE = "admission_guideline"
    PROGRAM_PAGE = "program_page"
    FAQ = "faq"
    CURRICULUM = "curriculum"
    DEPARTMENT_PAGE = "department_page"
    LAB_PAGE = "lab_page"
    OTHER = "other"


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class ExtractorType(str, enum.Enum):
    MANUAL = "manual"
    RULE = "rule"
    LLM = "llm"
