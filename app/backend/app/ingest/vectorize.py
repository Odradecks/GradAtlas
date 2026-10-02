"""Turn stored snapshots into document chunks and pgvector embeddings.

HTML uses the same heading splitter as verified intakes. PDF text is taken
page by page with pypdf. A chunk is tied to a verified intake only when the
snapshot folder year matches exactly one verified intake of that program.
Re-running skips snapshots that already have a document and chunks that
already have a vector for the current embedding model.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError
from sqlalchemy import select
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.config import settings
from app.database import SessionLocal
from app.ingest.chunking import build_chunks
from app.ingest.html_text import TextBlock, extract_html
from app.models.catalog import ProgramIntake
from app.models.enums import DocumentType
from app.models.provenance import Document, Source, SourceSnapshot
from app.models.rag import ChunkEmbedding, DocumentChunk
from app.rag.clients import ModelConfigError, embed_texts

_MIN_TEXT = 200


def _year_from_path(path: str | None) -> int | None:
    if not path:
        return None
    name = Path(path).parent.name
    return int(name) if name.isdigit() and len(name) == 4 else None


def _intake_for(session: Session, program_id: int | None, year: int | None) -> int | None:
    if program_id is None or year is None:
        return None
    ids = list(
        session.scalars(
            select(ProgramIntake.id).where(
                ProgramIntake.program_id == program_id,
                ProgramIntake.admission_year == year,
                ProgramIntake.last_verified_at.is_not(None),
            )
        )
    )
    return ids[0] if len(ids) == 1 else None


def _pdf_blocks(path: Path) -> tuple[list[TextBlock], int]:
    reader = PdfReader(str(path))
    blocks: list[TextBlock] = []
    for number, page in enumerate(reader.pages, start=1):
        text = " ".join((page.extract_text() or "").split())
        if text:
            blocks.append(TextBlock(f"Page {number}", text))
    return blocks, len(reader.pages)


def _blocks_for(path: Path) -> tuple[str | None, list[TextBlock], str, int | None]:
    if path.suffix.lower() == ".pdf":
        blocks, pages = _pdf_blocks(path)
        return None, blocks, "application/pdf", pages
    html = path.read_text(encoding="utf-8", errors="replace")
    title, blocks = extract_html(html)
    return title, blocks, "text/html", None


def index_snapshot(session: Session, snapshot: SourceSnapshot) -> str:
    source = session.get(Source, snapshot.source_id)
    if source is None or not snapshot.storage_path:
        return "missing-source"
    path = Path(snapshot.storage_path)
    if not path.is_file():
        return "missing-file"
    try:
        title, blocks, mime, pages = _blocks_for(path)
    except (PdfReadError, OSError, ValueError) as exc:
        return f"unreadable: {exc}"
    raw_text, drafts = build_chunks(blocks)
    if len(raw_text) < _MIN_TEXT or not drafts:
        return "too-short"
    year = _year_from_path(snapshot.storage_path)
    try:
        document_type = DocumentType(source.source_type.value)
    except ValueError:
        document_type = DocumentType.OTHER
    intake_id = _intake_for(session, source.program_id, year)
    document = Document(
        source_snapshot_id=snapshot.id,
        university_id=source.university_id,
        department_id=source.department_id,
        program_id=source.program_id,
        intake_id=intake_id,
        title=(title or "")[:512] or None,
        document_type=document_type,
        admission_year=year,
        mime_type=mime,
        raw_text=raw_text,
        page_count=pages,
    )
    session.add(document)
    session.flush()
    for index, draft in enumerate(drafts):
        page = None
        if draft.heading_path and draft.heading_path.startswith("Page "):
            head = draft.heading_path.split(" / ")[0].removeprefix("Page ")
            page = int(head) if head.isdigit() else None
        session.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                page_start=page,
                page_end=page,
                heading_path=draft.heading_path,
                char_start=draft.char_start,
                char_end=draft.char_end,
                token_count=draft.token_count,
                text=draft.text,
                university_id=source.university_id,
                program_id=source.program_id,
                intake_id=intake_id,
                admission_year=year,
                document_type=document_type,
            )
        )
    session.flush()
    return "created"


def embed_pending(session: Session) -> int:
    model = settings.embedding_model
    pending = list(
        session.scalars(
            select(DocumentChunk)
            .outerjoin(
                ChunkEmbedding,
                (ChunkEmbedding.chunk_id == DocumentChunk.id) & (ChunkEmbedding.embedding_model == model),
            )
            .where(ChunkEmbedding.chunk_id.is_(None))
            .order_by(DocumentChunk.id)
        )
    )
    created = 0
    for start in range(0, len(pending), 10):
        batch = pending[start : start + 10]
        vectors = embed_texts([chunk.text for chunk in batch])
        for chunk, vector in zip(batch, vectors, strict=True):
            session.add(ChunkEmbedding(chunk_id=chunk.id, embedding_model=model, embedding=vector))
        session.commit()
        created += len(batch)
        print(f"embedded {created}/{len(pending)}", flush=True)
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-embed", action="store_true", help="only create chunks")
    args = parser.parse_args()
    session = SessionLocal()
    created = 0
    skipped: dict[str, int] = {}
    try:
        snapshot_ids = list(session.scalars(select(SourceSnapshot.id).order_by(SourceSnapshot.id)))
        for snapshot_id in snapshot_ids:
            snapshot = session.get(SourceSnapshot, snapshot_id)
            if snapshot is None:
                continue
            exists = session.scalar(select(Document.id).where(Document.source_snapshot_id == snapshot.id))
            if exists is not None:
                continue
            try:
                status = index_snapshot(session, snapshot)
                session.commit()
                session.expunge_all()
            except Exception as exc:
                session.rollback()
                status = f"error: {exc}"
            if status == "created":
                created += 1
                print(f"chunked snapshot {snapshot_id}", flush=True)
            else:
                skipped[status] = skipped.get(status, 0) + 1
                print(f"skip snapshot {snapshot_id}: {status}", flush=True)
        print(f"documents created {created}; skipped {sum(skipped.values())} {skipped}", flush=True)
        if args.skip_embed:
            return
        embedded = embed_pending(session)
        print(f"embeddings created {embedded} ({settings.embedding_model})", flush=True)
    except ModelConfigError as exc:
        session.rollback()
        raise SystemExit(str(exc)) from exc
    finally:
        session.close()


if __name__ == "__main__":
    main()
