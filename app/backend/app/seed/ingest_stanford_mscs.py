"""
Fetch the official pages already cited for Stanford MS Computer Science
and store the parsed text for the Autumn 2027 intake.

Run: docker compose run --rm backend python -m app.seed.ingest_stanford_mscs

The same page bytes are stored once. This does not embed or answer questions.
"""

from __future__ import annotations

import urllib.request

from sqlalchemy import select
from sqlalchemy.orm import selectinload

import app.models  # noqa: F401
from app.database import SessionLocal
from app.ingest.store import store_html_page, sync_sources
from app.models.catalog import Department, Program, ProgramIntake, University
from app.models.enums import DocumentType, SourceType
from app.models.provenance import Source

PAGES: list[tuple[SourceType, DocumentType, str]] = [
    (
        SourceType.ADMISSION_GUIDELINE,
        DocumentType.ADMISSION_GUIDELINE,
        "https://www.cs.stanford.edu/admissions-graduate-application-deadlines",
    ),
    (
        SourceType.ADMISSION_GUIDELINE,
        DocumentType.ADMISSION_GUIDELINE,
        "https://www.cs.stanford.edu/admissions/graduate-application-checklists",
    ),
    (
        SourceType.FAQ,
        DocumentType.FAQ,
        "https://www.cs.stanford.edu/admissions/masters-admissions-frequently-asked-questions",
    ),
    (
        SourceType.ADMISSION_GUIDELINE,
        DocumentType.ADMISSION_GUIDELINE,
        "https://gradadmissions.stanford.edu/apply/test-scores",
    ),
]


def _fetch(url: str) -> tuple[int, str | None, bytes]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "GradAtlas/0.1 (official-page archive)"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        content_type = response.headers.get("Content-Type")
        return response.status, content_type, response.read()


def main() -> None:
    session = SessionLocal()
    try:
        program = session.scalar(
            select(Program)
            .join(Department, Program.department_id == Department.id)
            .join(University, Department.university_id == University.id)
            .where(University.slug == "stanford-university", Program.slug == "ms-computer-science")
            .options(selectinload(Program.department))
        )
        if program is None:
            raise RuntimeError("Stanford MS Computer Science is not in the catalog")
        intake = session.scalar(
            select(ProgramIntake).where(
                ProgramIntake.program_id == program.id,
                ProgramIntake.admission_year == 2027,
                ProgramIntake.entry_month == 9,
            )
        )
        if intake is None or intake.last_verified_at is None:
            raise RuntimeError("Autumn 2027 intake is missing or still a sample")

        sync_sources(
            session,
            university_id=program.department.university_id,
            department_id=program.department_id,
            program_id=program.id,
            sources=[(source_type, url) for source_type, _, url in PAGES],
        )
        session.commit()

        for _, document_type, url in PAGES:
            status, content_type, body = _fetch(url)
            if status != 200 or not body:
                raise RuntimeError(f"fetch failed for {url}: HTTP {status}")
            source = session.scalar(
                select(Source).where(Source.program_id == program.id, Source.url == url)
            )
            if source is None:
                raise RuntimeError(f"source row missing for {url}")
            document, action = store_html_page(
                session,
                source,
                body=body,
                http_status=status,
                content_type=content_type,
                intake_id=intake.id,
                admission_year=intake.admission_year,
                document_type=document_type,
                language="en",
            )
            session.commit()
            print(f"  {action}: document {document.id} <- {url}")
        print(f"intake {intake.id} Stanford MS Computer Science Autumn 2027")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
