import json
import logging
from collections.abc import Iterator
from decimal import Decimal, InvalidOperation
from enum import Enum

import app.models  # noqa: F401  # register Source and other mappers used by relationships
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.database import SessionLocal, get_db
from app.models.admissions import AdmissionRequirement, ApplicationRound, LanguageRequirement
from app.models.enums import LanguageTestType, RequirementStatus
from app.models.catalog import Department, Field, Program, ProgramField, ProgramIntake, University
from app.models.provenance import Document, Source, SourceSnapshot
from app.models.rag import DocumentChunk
from app.rag.answer import ask_compare, ask_intake, plan_compare, plan_intake, stream_plan
from app.rag.clients import ModelConfigError
from app.schemas.programs import (
    ApplicationRoundOut,
    AskIn,
    AskOut,
    CompareAskIn,
    CatalogProgramItem,
    CatalogProgramResponse,
    ExamSubjectOut,
    FieldOption,
    IntakeDetail,
    IntakeDocumentOut,
    LanguageOut,
    ProgramFilterOptions,
    ProgramListItem,
    ProgramListResponse,
    SourceOut,
    TuitionOut,
    UniversityOption,
)

router = APIRouter(tags=["programs"])
logger = logging.getLogger(__name__)


def _enum_value(value: Enum | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def _blank(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _base_query():
    return (
        select(ProgramIntake)
        .join(Program, ProgramIntake.program_id == Program.id)
        .join(Department, Program.department_id == Department.id)
        .join(University, Department.university_id == University.id)
        .where(Program.is_active.is_(True))
    )


def _parse_language_scores(raw: list[str]) -> list[tuple[LanguageTestType, Decimal]]:
    parsed: dict[LanguageTestType, Decimal] = {}
    allowed = {item.value: item for item in LanguageTestType}
    for item in raw:
        test_name, separator, score_text = item.partition(":")
        test = allowed.get(test_name.strip())
        if separator != ":" or test is None:
            raise HTTPException(status_code=422, detail="Invalid language score")
        try:
            score = Decimal(score_text.strip())
        except InvalidOperation:
            raise HTTPException(status_code=422, detail="Invalid language score")
        if score < 0 or score > Decimal("999.9"):
            raise HTTPException(status_code=422, detail="Invalid language score")
        parsed[test] = score
    return list(parsed.items())


def _language_match(test: LanguageTestType, score: Decimal):
    """A listed test counts when the user's score meets a comparable overall minimum.

    A row with no overall minimum, or a TOEFL minimum on the other score scale,
    still counts: the program accepts the test and did not publish a number
    that can be compared with this score.
    """
    meets_score = LanguageRequirement.minimum_overall.is_(None) | (
        LanguageRequirement.minimum_overall <= score
    )
    if test == LanguageTestType.TOEFL_IBT:
        different_scale = (
            LanguageRequirement.minimum_overall <= 9
            if score > 9
            else LanguageRequirement.minimum_overall > 9
        )
        meets_score = LanguageRequirement.minimum_overall.is_(None) | different_scale | (
            LanguageRequirement.minimum_overall <= score
        )
    return (
        select(LanguageRequirement.id)
        .where(
            LanguageRequirement.intake_id == ProgramIntake.id,
            LanguageRequirement.test_type == test,
            LanguageRequirement.requirement_status != RequirementStatus.NOT_REQUIRED,
            meets_score,
        )
        .exists()
    )


def _apply_filters(
    stmt,
    *,
    country: str | None,
    university: str | None,
    field: str | None,
    admission_year: int | None,
    entry_month: int | None,
    language_scores: list[tuple[LanguageTestType, Decimal]] | None = None,
):
    if country:
        stmt = stmt.where(University.country_code == country.upper())
    if university:
        stmt = stmt.where(University.slug == university)
    if admission_year is not None:
        stmt = stmt.where(ProgramIntake.admission_year == admission_year)
    if entry_month is not None:
        stmt = stmt.where(ProgramIntake.entry_month == entry_month)
    if field:
        field_match = (
            select(ProgramField.program_id)
            .join(Field, ProgramField.field_id == Field.id)
            .where(ProgramField.program_id == Program.id, Field.slug == field)
            .exists()
        )
        stmt = stmt.where(field_match)
    if language_scores:
        stmt = stmt.where(or_(*(_language_match(test, score) for test, score in language_scores)))
    return stmt


def _date(value) -> str | None:
    return value.isoformat() if value is not None else None


def _languages(intake: ProgramIntake, *, detailed: bool) -> list[LanguageOut]:
    return [
        LanguageOut(
            test_type=_enum_value(row.test_type) or "",
            minimum_overall=row.minimum_overall,
            minimum_reading=row.minimum_reading if detailed else None,
            minimum_writing=row.minimum_writing if detailed else None,
            minimum_listening=row.minimum_listening if detailed else None,
            minimum_speaking=row.minimum_speaking if detailed else None,
            requirement_status=_enum_value(row.requirement_status) or "",
            notes=row.notes,
        )
        for row in intake.language_requirements
    ]


def _tuitions(intake: ProgramIntake, *, detailed: bool) -> list[TuitionOut]:
    return [
        TuitionOut(
            student_category=_enum_value(row.student_category) or "",
            amount=row.amount,
            currency=row.currency,
            billing_period=_enum_value(row.billing_period) or "",
            normalized_annual_eur=row.normalized_annual_eur,
            mandatory_fee=row.mandatory_fee if detailed else None,
            notes=row.notes if detailed else None,
        )
        for row in intake.tuition_fees
    ]


def _to_item(intake: ProgramIntake) -> ProgramListItem:
    program = intake.program
    university = program.department.university
    requirement: AdmissionRequirement | None = intake.admission_requirement
    sources = [
        SourceOut(source_type=_enum_value(source.source_type) or "", url=source.url)
        for source in program.sources
        if source.is_active
    ]
    return ProgramListItem(
        intake_id=intake.id,
        university_name=university.name_en,
        city=university.city,
        country_code=university.country_code,
        verified=intake.last_verified_at is not None,
        program_name=program.name_en,
        program_slug=program.slug,
        degree_type=program.degree_type,
        fields=sorted(link.field.slug for link in program.fields),
        admission_year=intake.admission_year,
        entry_month=intake.entry_month,
        intake_label=intake.intake_label,
        gre_requirement=_enum_value(requirement.gre_requirement) if requirement else None,
        gre_note=requirement.gre_note if requirement else None,
        entrance_exam_status=_enum_value(requirement.entrance_exam_status) if requirement else None,
        languages=_languages(intake, detailed=False),
        tuitions=_tuitions(intake, detailed=False),
        sources=sources,
        official_url=program.official_url,
    )


@router.get("/programs/filters", response_model=ProgramFilterOptions)
def program_filters(db: Session = Depends(get_db)) -> ProgramFilterOptions:
    countries = list(
        db.scalars(select(University.country_code).distinct().order_by(University.country_code))
    )
    universities = list(db.scalars(select(University).order_by(University.name_en)))
    fields = list(db.scalars(select(Field).order_by(Field.name)))
    years = list(
        db.scalars(
            select(ProgramIntake.admission_year).distinct().order_by(ProgramIntake.admission_year)
        )
    )
    months = list(
        db.scalars(select(ProgramIntake.entry_month).distinct().order_by(ProgramIntake.entry_month))
    )
    return ProgramFilterOptions(
        countries=countries,
        universities=[
            UniversityOption(slug=row.slug, name=row.name_en, country_code=row.country_code)
            for row in universities
        ],
        fields=[FieldOption(slug=row.slug, name=row.name) for row in fields],
        admission_years=years,
        entry_months=months,
    )


@router.get("/programs", response_model=ProgramListResponse)
def list_programs(
    country: str | None = Query(default=None, min_length=2, max_length=2),
    university: str | None = Query(default=None, max_length=128),
    field: str | None = Query(default=None, max_length=64),
    admission_year: int | None = Query(default=None, ge=2000, le=2100),
    entry_month: int | None = Query(default=None, ge=1, le=12),
    lang: list[str] = Query(default=[]),
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> ProgramListResponse:
    country = _blank(country)
    university = _blank(university)
    field = _blank(field)
    filtered = _apply_filters(
        _base_query(),
        country=country,
        university=university,
        field=field,
        admission_year=admission_year,
        entry_month=entry_month,
        language_scores=_parse_language_scores(lang),
    )
    total = db.scalar(select(func.count()).select_from(filtered.subquery())) or 0
    stmt = (
        filtered.options(
            selectinload(ProgramIntake.admission_requirement),
            selectinload(ProgramIntake.language_requirements),
            selectinload(ProgramIntake.tuition_fees),
            selectinload(ProgramIntake.program)
            .selectinload(Program.department)
            .selectinload(Department.university),
            selectinload(ProgramIntake.program)
            .selectinload(Program.fields)
            .selectinload(ProgramField.field),
            selectinload(ProgramIntake.program).selectinload(Program.sources),
        )
        .order_by(
            University.country_code,
            University.name_en,
            Program.name_en,
            ProgramIntake.admission_year,
            ProgramIntake.entry_month,
        )
        .limit(limit)
        .offset(offset)
    )
    intakes = list(db.scalars(stmt).unique())
    return ProgramListResponse(total=total, items=[_to_item(row) for row in intakes])


def _load_options():
    return (
        selectinload(ProgramIntake.admission_requirement),
        selectinload(ProgramIntake.language_requirements),
        selectinload(ProgramIntake.tuition_fees),
        selectinload(ProgramIntake.application_rounds).selectinload(ApplicationRound.exam_subjects),
        selectinload(ProgramIntake.program).selectinload(Program.department).selectinload(Department.university),
        selectinload(ProgramIntake.program).selectinload(Program.fields).selectinload(ProgramField.field),
        selectinload(ProgramIntake.program).selectinload(Program.sources),
    )


@router.get("/intakes/{intake_id}", response_model=IntakeDetail)
def get_intake(intake_id: int, db: Session = Depends(get_db)) -> IntakeDetail:
    intake = db.scalar(
        _base_query().where(ProgramIntake.id == intake_id).options(*_load_options())
    )
    if intake is None:
        raise HTTPException(status_code=404, detail="Intake not found")
    item = _to_item(intake)
    requirement = intake.admission_requirement
    rounds = [
        ApplicationRoundOut(
            name=row.name,
            applicant_group=row.applicant_group,
            opens_on=_date(row.opens_on),
            deadline=_date(row.deadline),
            exam_date=_date(row.exam_date),
            notes=row.notes,
            exam_subjects=[
                ExamSubjectOut(subject=subject.subject, notes=subject.notes)
                for subject in row.exam_subjects
            ],
        )
        for row in intake.application_rounds
    ]
    payload = item.model_dump()
    payload.update(
        department_name=intake.program.department.name_en,
        gpa_note=requirement.gpa_note if requirement else None,
        gre_note=requirement.gre_note if requirement else None,
        recommendation_letter_count=requirement.recommendation_letter_count if requirement else None,
        professor_contact_status=_enum_value(requirement.professor_contact_status) if requirement else None,
        interview_status=_enum_value(requirement.interview_status) if requirement else None,
        languages=_languages(intake, detailed=True),
        tuitions=_tuitions(intake, detailed=True),
        rounds=rounds,
        documents=_documents(db, intake.id),
    )
    return IntakeDetail(**payload)


def _documents(db: Session, intake_id: int) -> list[IntakeDocumentOut]:
    rows = db.execute(
        select(
            Document.id,
            Document.title,
            Document.document_type,
            Document.language,
            Document.admission_year,
            Source.url,
            func.count(DocumentChunk.id),
        )
        .join(SourceSnapshot, Document.source_snapshot_id == SourceSnapshot.id)
        .join(Source, SourceSnapshot.source_id == Source.id)
        .outerjoin(DocumentChunk, DocumentChunk.document_id == Document.id)
        .where(Document.intake_id == intake_id)
        .group_by(
            Document.id,
            Document.title,
            Document.document_type,
            Document.language,
            Document.admission_year,
            Source.url,
        )
        .order_by(Document.id)
    ).all()
    return [
        IntakeDocumentOut(
            id=row[0],
            title=row[1],
            document_type=_enum_value(row[2]) or "",
            language=row[3],
            admission_year=row[4],
            source_url=row[5],
            chunk_count=row[6],
        )
        for row in rows
    ]


@router.get("/intakes/{intake_id}/documents", response_model=list[IntakeDocumentOut])
def list_intake_documents(intake_id: int, db: Session = Depends(get_db)) -> list[IntakeDocumentOut]:
    intake = db.scalar(_base_query().where(ProgramIntake.id == intake_id))
    if intake is None:
        raise HTTPException(status_code=404, detail="Intake not found")
    return _documents(db, intake_id)


@router.post("/intakes/compare", response_model=AskOut)
def ask_compare_question(body: CompareAskIn, db: Session = Depends(get_db)) -> AskOut:
    if len(set(body.intake_ids)) != len(body.intake_ids):
        raise HTTPException(status_code=422, detail="重复的入学季")
    intakes = []
    for intake_id in body.intake_ids:
        intake = db.scalar(_base_query().where(ProgramIntake.id == intake_id))
        if intake is None:
            raise HTTPException(status_code=404, detail="Intake not found")
        intakes.append(intake)
    try:
        return ask_compare(db, intakes, body.question.strip())
    except ModelConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/intakes/{intake_id}/ask", response_model=AskOut)
def ask_intake_question(intake_id: int, body: AskIn, db: Session = Depends(get_db)) -> AskOut:
    intake = db.scalar(_base_query().where(ProgramIntake.id == intake_id))
    if intake is None:
        raise HTTPException(status_code=404, detail="Intake not found")
    try:
        return ask_intake(db, intake, body.question.strip())
    except ModelConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _event(kind: str, **data) -> str:
    return json.dumps({"event": kind, **data}, ensure_ascii=False) + "\n"


def _stream_events(intake_ids: list[int], question: str, compare: bool) -> Iterator[str]:
    """NDJSON: retrieving → citations → answering → delta… → done, or final / error."""
    yield _event("retrieving")
    db = SessionLocal()
    try:
        intakes = [db.scalar(_base_query().where(ProgramIntake.id == intake_id)) for intake_id in intake_ids]
        plan = plan_compare(db, intakes, question) if compare else plan_intake(db, intakes[0], question)
        if isinstance(plan, AskOut):
            yield _event("final", **plan.model_dump())
            return
        yield _event("citations", citations=[item.model_dump() for item in plan.citations])
        yield _event("answering")
        for piece in stream_plan(plan):
            yield _event("delta", text=piece)
        yield _event("done", status="answered")
    except ModelConfigError as exc:
        yield _event("error", message=str(exc))
    except Exception:
        logger.exception("streamed answer failed")
        yield _event("error", message="回答中断：模型或检索服务出错，请稍后重试。")
    finally:
        db.close()


def _ndjson(events: Iterator[str]) -> StreamingResponse:
    return StreamingResponse(
        events,
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
    )


@router.post("/intakes/compare/stream")
def stream_compare_question(body: CompareAskIn, db: Session = Depends(get_db)) -> StreamingResponse:
    if len(set(body.intake_ids)) != len(body.intake_ids):
        raise HTTPException(status_code=422, detail="重复的入学季")
    for intake_id in body.intake_ids:
        if db.scalar(_base_query().where(ProgramIntake.id == intake_id)) is None:
            raise HTTPException(status_code=404, detail="Intake not found")
    return _ndjson(_stream_events(body.intake_ids, body.question.strip(), compare=True))


@router.post("/intakes/{intake_id}/ask/stream")
def stream_intake_question(intake_id: int, body: AskIn, db: Session = Depends(get_db)) -> StreamingResponse:
    if db.scalar(_base_query().where(ProgramIntake.id == intake_id)) is None:
        raise HTTPException(status_code=404, detail="Intake not found")
    return _ndjson(_stream_events([intake_id], body.question.strip(), compare=False))


def _catalog_query():
    return (
        select(Program)
        .join(Department, Program.department_id == Department.id)
        .join(University, Department.university_id == University.id)
        .where(Program.is_active.is_(True))
    )


def _catalog_filters(stmt, *, country: str | None, university: str | None, field: str | None, priority: str | None):
    if country:
        stmt = stmt.where(University.country_code == country.upper())
    if university:
        stmt = stmt.where(University.slug == university)
    if priority == "none":
        stmt = stmt.where(Program.ingestion_priority.is_(None))
    elif priority:
        stmt = stmt.where(Program.ingestion_priority == priority)
    if field:
        field_match = (
            select(ProgramField.program_id)
            .join(Field, ProgramField.field_id == Field.id)
            .where(ProgramField.program_id == Program.id, Field.slug == field)
            .exists()
        )
        stmt = stmt.where(field_match)
    return stmt


@router.get("/catalog/programs", response_model=CatalogProgramResponse)
def list_catalog(
    country: str | None = Query(default=None, min_length=2, max_length=2),
    university: str | None = Query(default=None, max_length=128),
    field: str | None = Query(default=None, max_length=64),
    priority: str | None = Query(default=None, max_length=8),
    limit: int = Query(default=1000, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> CatalogProgramResponse:
    filtered = _catalog_filters(
        _catalog_query(),
        country=_blank(country),
        university=_blank(university),
        field=_blank(field),
        priority=_blank(priority),
    )
    total = db.scalar(select(func.count()).select_from(filtered.subquery())) or 0
    priority_rank = case(
        (Program.ingestion_priority == "P0", 0),
        (Program.ingestion_priority == "P1", 1),
        (Program.ingestion_priority == "P2", 2),
        else_=3,
    )
    stmt = (
        filtered.options(
            selectinload(Program.department).selectinload(Department.university),
            selectinload(Program.fields).selectinload(ProgramField.field),
            selectinload(Program.intakes),
        )
        .order_by(University.country_code, priority_rank, University.name_en, Program.name_en)
        .limit(limit)
        .offset(offset)
    )
    programs = list(db.scalars(stmt).unique())
    items = []
    for program in programs:
        university_row = program.department.university
        items.append(
            CatalogProgramItem(
                university_slug=university_row.slug,
                university_name=university_row.name_en,
                country_code=university_row.country_code,
                website_url=university_row.website_url,
                program_slug=program.slug,
                program_name=program.name_en,
                degree_type=program.degree_type,
                fields=[row.field.slug for row in program.fields],
                priority=program.ingestion_priority,
                official_url=program.official_url,
                intake_count=len(program.intakes),
            )
        )
    return CatalogProgramResponse(total=total, items=items)
