"""Answer one question from a single intake's embedded chunks."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models.catalog import ProgramIntake
from app.models.provenance import Document, Source, SourceSnapshot
from app.models.rag import ChunkEmbedding, DocumentChunk
from app.rag.clients import (
    COMPARE_SYSTEM,
    INTAKE_SYSTEM,
    ModelConfigError,
    complete,
    embed_texts,
    require_chat,
    require_embedding,
    stream_complete,
)
from app.schemas.programs import AskOut, CitationOut

_TOP_K = 5
_EMPTY_ANSWER = "对话模型没有返回正文，当前没有生成回答。"


@dataclass
class _Hit:
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


@dataclass
class AnswerPlan:
    """Retrieved excerpts and the prompt that still needs a chat model."""

    system: str
    prompt: str
    hits: list[_Hit]

    @property
    def citations(self) -> list[CitationOut]:
        return _citations(self.hits)


def _citations(hits: list[_Hit]) -> list[CitationOut]:
    return [
        CitationOut(
            chunk_id=hit.chunk_id,
            heading_path=hit.heading_path,
            text=hit.text,
            source_url=hit.source_url,
            document_title=hit.document_title,
            admission_year=hit.admission_year,
            page_start=hit.page_start,
            page_end=hit.page_end,
            university_name=hit.university_name,
            program_name=hit.program_name,
        )
        for hit in hits
    ]


def _search(session: Session, intake: ProgramIntake, question: str, *, by_program: bool = False) -> list[_Hit]:
    require_embedding()
    vector = embed_texts([question])[0]
    distance = ChunkEmbedding.embedding.cosine_distance(vector)
    scope = (
        DocumentChunk.program_id == intake.program_id
        if by_program
        else DocumentChunk.intake_id == intake.id
    )
    rows = session.execute(
        select(
            DocumentChunk.id,
            DocumentChunk.heading_path,
            DocumentChunk.text,
            DocumentChunk.admission_year,
            DocumentChunk.page_start,
            DocumentChunk.page_end,
            Document.title,
            Source.url,
            distance.label("distance"),
        )
        .join(ChunkEmbedding, ChunkEmbedding.chunk_id == DocumentChunk.id)
        .join(Document, Document.id == DocumentChunk.document_id)
        .join(SourceSnapshot, SourceSnapshot.id == Document.source_snapshot_id)
        .join(Source, Source.id == SourceSnapshot.source_id)
        .where(
            scope,
            DocumentChunk.admission_year == intake.admission_year,
            ChunkEmbedding.embedding_model == settings.embedding_model,
        )
        .order_by(distance)
        .limit(_TOP_K)
    ).all()
    return [
        _Hit(
            chunk_id=row.id,
            heading_path=row.heading_path,
            text=row.text,
            source_url=row.url,
            document_title=row.title,
            admission_year=row.admission_year,
            page_start=row.page_start,
            page_end=row.page_end,
        )
        for row in rows
    ]


def _block(index: int, hit: _Hit) -> str:
    return (
        f"[{index}] {hit.document_title or '官网页面'} / {hit.heading_path or '无章节'}\n"
        f"适用年份：{hit.admission_year}\n"
        f"网址：{hit.source_url}\n"
        f"{hit.text}"
    )


def _prompt(intake: ProgramIntake, question: str, hits: list[_Hit]) -> str:
    program = intake.program
    university = program.department.university
    excerpts = "\n\n".join(_block(index, hit) for index, hit in enumerate(hits, start=1))
    return (
        f"学校：{university.name_en}\n"
        f"项目：{program.name_en}\n"
        f"入学季：{intake.admission_year} 年 {intake.entry_month} 月"
        f"（{intake.intake_label or '未标注'}）。\n"
        f"问题：{question}\n\n"
        f"请用中文回答。下面是英文官网片段，只作依据，不要把片段原文当作回答正文：\n\n{excerpts}"
    )


def plan_intake(session: Session, intake: ProgramIntake, question: str) -> AskOut | AnswerPlan:
    """Return a final AskOut when no model call is needed, otherwise the retrieved plan."""
    if intake.last_verified_at is None:
        return AskOut(
            status="sample",
            answer="这一入学季仍是样例，不能作为正式依据。",
            citations=[],
        )

    chunk_count = session.scalar(
        select(DocumentChunk.id)
        .where(
            DocumentChunk.intake_id == intake.id,
            DocumentChunk.admission_year == intake.admission_year,
        )
        .limit(1)
    )
    if chunk_count is None:
        return AskOut(
            status="insufficient",
            answer="这一入学季还没有官网原文，无法回答。这不表示没有招生要求。",
            citations=[],
        )

    embedded = session.scalar(
        select(ChunkEmbedding.chunk_id)
        .join(DocumentChunk, DocumentChunk.id == ChunkEmbedding.chunk_id)
        .where(
            DocumentChunk.intake_id == intake.id,
            DocumentChunk.admission_year == intake.admission_year,
            ChunkEmbedding.embedding_model == settings.embedding_model,
        )
        .limit(1)
    )
    if embedded is None:
        raise ModelConfigError(
            f"入学季 {intake.id} 的片段还没有 {settings.embedding_model} 向量，当前没有生成回答。"
        )

    hits = _search(session, intake, question)
    if not hits:
        return AskOut(
            status="insufficient",
            answer="这一入学季的原文里没有检索到相关片段，无法回答。这不表示没有招生要求。",
            citations=[],
        )

    require_chat()
    return AnswerPlan(system=INTAKE_SYSTEM, prompt=_prompt(intake, question, hits), hits=hits)


def _label(intake: ProgramIntake) -> tuple[str, str, str]:
    program = intake.program
    university = program.department.university
    month = f"{intake.entry_month} 月" if intake.entry_month else "入学月份未标注"
    heading = f"{university.name_en} / {program.name_en} / {intake.admission_year} 年 {month}"
    return university.name_en, program.name_en, heading


def plan_compare(session: Session, intakes: list[ProgramIntake], question: str) -> AskOut | AnswerPlan:
    """Compare 2–4 intakes. Each side is searched only within its own program and year."""
    if len(intakes) < 2 or len(intakes) > 4:
        raise ModelConfigError("对比需要 2 到 4 个入学季。")
    sections: list[str] = []
    citations: list[_Hit] = []
    found = 0
    for intake in intakes:
        university_name, program_name, heading = _label(intake)
        hits = _search(session, intake, question, by_program=True)
        if not hits:
            sections.append(f"## {heading}\n这一年的官网原文里没有检索到相关片段。")
            continue
        found += 1
        blocks = []
        for hit in hits:
            hit.university_name = university_name
            hit.program_name = program_name
            citations.append(hit)
            blocks.append(_block(len(citations), hit))
        sections.append(f"## {heading}\n" + "\n\n".join(blocks))
    if found == 0:
        return AskOut(
            status="insufficient",
            answer="这些项目在对应年份的官网原文里都没有检索到相关片段，无法比较。这不表示没有招生要求。",
            citations=[],
        )
    require_chat()
    names = "、".join(_label(intake)[2] for intake in intakes)
    prompt = (
        f"问题：{question}\n\n"
        f"请比较以下项目：{names}。\n"
        "每个二级标题下的片段只属于该项目。请说明它们的差别；某个项目没有片段或片段没写到的点，直接写资料没有写明。\n\n"
        + "\n\n".join(sections)
    )
    return AnswerPlan(system=COMPARE_SYSTEM, prompt=prompt, hits=citations)


def _answer(plan: AskOut | AnswerPlan) -> AskOut:
    if isinstance(plan, AskOut):
        return plan
    answer = complete(plan.system, plan.prompt)
    if not answer:
        raise ModelConfigError(_EMPTY_ANSWER)
    return AskOut(status="answered", answer=answer, citations=plan.citations)


def ask_intake(session: Session, intake: ProgramIntake, question: str) -> AskOut:
    return _answer(plan_intake(session, intake, question))


def ask_compare(session: Session, intakes: list[ProgramIntake], question: str) -> AskOut:
    return _answer(plan_compare(session, intakes, question))


def stream_plan(plan: AnswerPlan) -> Iterator[str]:
    """Yield answer text pieces; raise ModelConfigError if the model returns nothing."""
    produced = False
    for piece in stream_complete(plan.system, plan.prompt):
        produced = produced or bool(piece.strip())
        yield piece
    if not produced:
        raise ModelConfigError(_EMPTY_ANSWER)
