from app.models.admissions import (
    AdmissionRequirement,
    ApplicationRound,
    EntranceExamSubject,
    LanguageRequirement,
    TuitionFee,
)
from app.models.base import Base
from app.models.catalog import (
    Department,
    Field,
    Program,
    ProgramField,
    ProgramIntake,
    University,
    UniversityAlias,
)
from app.models.account import User, UserFavorite, UserSession
from app.models.provenance import Document, Source, SourceSnapshot
from app.models.rag import ChunkEmbedding, DocumentChunk, ExtractedFact

__all__ = [
    "Base",
    "University",
    "UniversityAlias",
    "Department",
    "Program",
    "Field",
    "ProgramField",
    "ProgramIntake",
    "AdmissionRequirement",
    "LanguageRequirement",
    "TuitionFee",
    "ApplicationRound",
    "EntranceExamSubject",
    "User",
    "UserSession",
    "UserFavorite",
    "Source",
    "SourceSnapshot",
    "Document",
    "DocumentChunk",
    "ChunkEmbedding",
    "ExtractedFact",
]
