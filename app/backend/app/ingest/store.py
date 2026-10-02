"""Idempotent snapshot, document, and chunk storage."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.ingest.chunking import build_chunks
from app.ingest.html_text import extract_html
from app.models.catalog import Program, ProgramIntake, University
from app.models.enums import DocumentType, SourceType
from app.models.provenance import Document, Source, SourceSnapshot
from app.models.rag import DocumentChunk


def sync_sources(
    session: Session,
    *,
    university_id: int,
    department_id: int,
    program_id: int,
    sources: list[tuple[SourceType, str]],
) -> None:
    """Keep one source row per URL. Missing URLs are deactivated, not deleted."""
    existing = {
        row.url: row
        for row in session.scalars(select(Source).where(Source.program_id == program_id))
    }
    wanted: set[str] = set()
    for source_type, url in sources:
        wanted.add(url)
        row = existing.get(url)
        if row is None:
            session.add(
                Source(
                    university_id=university_id,
                    department_id=department_id,
                    program_id=program_id,
                    url=url,
                    source_type=source_type,
                    is_active=True,
                )
            )
            continue
        row.source_type = source_type
        row.is_active = True
        row.university_id = university_id
        row.department_id = department_id
    program = session.get(Program, program_id)
    keep = {program.official_url} if program is not None and program.official_url else set()
    for url, row in existing.items():
        if url not in wanted and url not in keep:
            row.is_active = False
    session.flush()


def ensure_source(
    session: Session,
    *,
    university_id: int | None,
    department_id: int | None,
    program_id: int,
    url: str,
    source_type: SourceType,
    reactivate: bool,
) -> Source:
    """Add one source row if the program does not have this URL yet."""
    row = session.scalar(select(Source).where(Source.program_id == program_id, Source.url == url))
    if row is None:
        row = Source(
            university_id=university_id,
            department_id=department_id,
            program_id=program_id,
            url=url,
            source_type=source_type,
            is_active=True,
        )
        session.add(row)
    elif reactivate:
        row.is_active = True
    session.flush()
    return row


def store_html_page(
    session: Session,
    source: Source,
    *,
    body: bytes,
    http_status: int,
    content_type: str | None,
    intake_id: int,
    admission_year: int,
    document_type: DocumentType,
    language: str,
) -> tuple[Document, str]:
    """Store one fetched page. The same bytes do not create another document."""
    digest = hashlib.sha256(body).hexdigest()
    snapshot = session.scalar(
        select(SourceSnapshot).where(
            SourceSnapshot.source_id == source.id,
            SourceSnapshot.content_hash == digest,
        )
    )
    snapshot_path = snapshot_file(
        session, source, digest=digest, extension="html", document_year=admission_year
    )
    if snapshot is None:
        _write_snapshot(snapshot_path, body)
        snapshot = SourceSnapshot(
            source_id=source.id,
            fetched_at=datetime.now(timezone.utc),
            http_status=http_status,
            content_type=(content_type or "")[:128] or None,
            content_hash=digest,
            storage_path=str(snapshot_path),
        )
        session.add(snapshot)
        session.flush()
    else:
        _move_snapshot(snapshot, snapshot_path, body)

    document = session.scalar(select(Document).where(Document.source_snapshot_id == snapshot.id))
    if document is not None:
        chunk_count = session.scalar(
            select(func.count()).select_from(DocumentChunk).where(DocumentChunk.document_id == document.id)
        )
        source.last_crawled_at = datetime.now(timezone.utc)
        return document, "reused" if chunk_count else "document-without-chunks"

    html = body.decode("utf-8", errors="replace")
    title, blocks = extract_html(html)
    raw_text, drafts = build_chunks(blocks)
    if len(raw_text) < 200:
        raise RuntimeError(f"extracted text is too short for {source.url}")

    document = Document(
        source_snapshot_id=snapshot.id,
        university_id=source.university_id,
        department_id=source.department_id,
        program_id=source.program_id,
        intake_id=intake_id,
        title=(title or "")[:512] or None,
        document_type=document_type,
        language=language,
        admission_year=admission_year,
        mime_type="text/html",
        raw_text=raw_text,
    )
    session.add(document)
    session.flush()
    for index, draft in enumerate(drafts):
        session.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                heading_path=draft.heading_path,
                char_start=draft.char_start,
                char_end=draft.char_end,
                token_count=draft.token_count,
                text=draft.text,
                university_id=source.university_id,
                program_id=source.program_id,
                intake_id=intake_id,
                admission_year=admission_year,
                document_type=document_type,
                language=language,
            )
        )
    source.last_crawled_at = datetime.now(timezone.utc)
    session.flush()
    return document, "created"


def snapshot_file(
    session: Session,
    source: Source,
    *,
    digest: str,
    extension: str = "html",
    document_year: int | None = None,
) -> Path:
    """Path is country / school / program / year / name. A URL used by several
    programs goes to `_shared`. The year comes from the program's intakes when
    there is exactly one, otherwise `_undated`."""
    sibling_programs = {
        pid
        for pid in session.scalars(select(Source.program_id).where(Source.url == source.url))
        if pid is not None
    }
    if source.program_id is not None:
        sibling_programs.add(source.program_id)
    university = session.get(University, source.university_id) if source.university_id else None
    country = university.country_code if university else "_unknown"
    school = university.slug if university else "_unknown"
    program_slug = "_shared"
    if len(sibling_programs) == 1 and source.program_id is not None:
        program = session.get(Program, source.program_id)
        program_slug = program.slug if program else "_shared"
    year = "_undated"
    if document_year:
        year = str(document_year)
    elif sibling_programs:
        years = set(
            session.scalars(
                select(ProgramIntake.admission_year).where(ProgramIntake.program_id.in_(sibling_programs))
            )
        )
        if len(years) == 1:
            year = str(years.pop())
    return (
        Path(settings.snapshot_dir)
        / country
        / school
        / program_slug
        / year
        / f"{_url_stem(source.url)}-{digest[:12]}.{extension}"
    )


def relocate_snapshots(session: Session) -> int:
    """Move numbered snapshot folders into country / school / program / year."""
    rows = list(session.scalars(select(SourceSnapshot)))
    moved = 0
    for snapshot in rows:
        source = session.get(Source, snapshot.source_id)
        if source is None:
            continue
        document = session.scalar(select(Document).where(Document.source_snapshot_id == snapshot.id))
        year = document.admission_year if document is not None else None
        suffix = Path(snapshot.storage_path).suffix.lstrip(".") if snapshot.storage_path else ""
        destination = snapshot_file(
            session,
            source,
            digest=snapshot.content_hash,
            extension=suffix or "html",
            document_year=year,
        )
        current = Path(snapshot.storage_path) if snapshot.storage_path else None
        if current is not None and current.resolve() == destination.resolve() and destination.exists():
            continue
        if current is not None and current.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            current.replace(destination)
            _remove_empty_parents(current.parent)
        elif not destination.exists():
            raise RuntimeError(f"missing snapshot file for source {snapshot.source_id}")
        snapshot.storage_path = str(destination)
        moved += 1
    session.flush()
    return moved


def _url_stem(url: str) -> str:
    name = urlparse(url).path.rstrip("/").split("/")[-1] or "page"
    stem = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return stem[:80] or "page"


def _write_snapshot(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)


def _move_snapshot(snapshot: SourceSnapshot, destination: Path, body: bytes) -> None:
    current = Path(snapshot.storage_path) if snapshot.storage_path else None
    if destination.exists() and (current is None or current.resolve() == destination.resolve()):
        snapshot.storage_path = str(destination)
        return
    if current is not None and current.exists() and current.resolve() != destination.resolve():
        destination.parent.mkdir(parents=True, exist_ok=True)
        current.replace(destination)
        _remove_empty_parents(current.parent)
    elif not destination.exists():
        _write_snapshot(destination, body)
    snapshot.storage_path = str(destination)


def _remove_empty_parents(start: Path) -> None:
    root = Path(settings.snapshot_dir).resolve()
    current = start
    while current.resolve() != root and current != current.parent:
        if any(current.iterdir()):
            return
        current.rmdir()
        current = current.parent
