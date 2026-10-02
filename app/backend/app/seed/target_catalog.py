"""
Insert the target university and program catalog.

Existing universities and programs are kept. This command does not create
intakes, tuition, language scores, or deadlines. MIT is stored as a university
only, because EECS does not offer a public terminal master's in computer science.

Run: docker compose run --rm backend python -m app.seed.target_catalog
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.catalog import Department, Field, Program, ProgramField, University, UniversityAlias
from app.seed.catalog_targets import TARGETS

FIELD_SPECS = (
    ("cs", "Computer Science"),
    ("ai", "Artificial Intelligence"),
    ("data-science", "Data Science"),
    ("software-engineering", "Software Engineering"),
    ("information-technology", "Information Technology"),
)


def ensure_fields(session: Session) -> dict[str, Field]:
    out: dict[str, Field] = {}
    for slug, name in FIELD_SPECS:
        row = session.scalar(select(Field).where(Field.slug == slug))
        if row is None:
            row = Field(slug=slug, name=name)
            session.add(row)
            session.flush()
        out[slug] = row
    return out


def ensure_university(session: Session, spec: dict) -> University:
    uni = session.scalar(select(University).where(University.slug == spec["slug"]))
    if uni is None:
        uni = University(
            slug=spec["slug"],
            name_en=spec["name_en"],
            name_local=spec["name_local"],
            country_code=spec["country_code"],
            city=spec["city"],
            website_url=spec["website_url"],
        )
        session.add(uni)
        session.flush()
    for alias in spec["aliases"]:
        exists = session.scalar(
            select(UniversityAlias).where(
                UniversityAlias.university_id == uni.id,
                UniversityAlias.alias == alias,
            )
        )
        if exists is None:
            session.add(UniversityAlias(university_id=uni.id, alias=alias))
    return uni


def ensure_department(session: Session, uni: University, name: str) -> Department:
    dept = session.scalar(
        select(Department).where(
            Department.university_id == uni.id,
            Department.name_en == name,
        )
    )
    if dept is None:
        dept = Department(university_id=uni.id, name_en=name)
        session.add(dept)
        session.flush()
    return dept


def ensure_program(
    session: Session,
    uni: University,
    spec: dict,
    fields: dict[str, Field],
    priority: str | None,
) -> str:
    existing = session.scalar(
        select(Program)
        .join(Department, Program.department_id == Department.id)
        .where(Department.university_id == uni.id, Program.slug == spec["slug"])
    )
    if existing is not None:
        if priority and existing.ingestion_priority != priority:
            existing.ingestion_priority = priority
        return "kept"
    dept = ensure_department(session, uni, spec.get("department") or spec["_department"])
    program = Program(
        department_id=dept.id,
        slug=spec["slug"],
        name_en=spec["name_en"],
        degree_type=spec["degree_type"],
        ingestion_priority=priority,
        is_active=True,
    )
    session.add(program)
    session.flush()
    for slug in spec["fields"]:
        session.add(ProgramField(program_id=program.id, field_id=fields[slug].id))
    return "created"


def apply_priority(session: Session, uni: University, priority: str | None) -> None:
    if not priority:
        return
    rows = session.scalars(
        select(Program)
        .join(Department, Program.department_id == Department.id)
        .where(Department.university_id == uni.id)
    )
    for program in rows:
        program.ingestion_priority = priority


def main() -> None:
    session = SessionLocal()
    created = 0
    kept = 0
    try:
        fields = ensure_fields(session)
        for spec in TARGETS:
            uni = ensure_university(session, spec)
            if not spec["programs"]:
                print(f"  university only: {spec['slug']} (no terminal master's row)")
                continue
            for program in spec["programs"]:
                program["_department"] = spec["department"]
                result = ensure_program(session, uni, program, fields, spec["priority"])
                if result == "created":
                    created += 1
                else:
                    kept += 1
            apply_priority(session, uni, spec["priority"])
        session.commit()
        print(f"Done. Created {created} programs, left {kept} existing programs unchanged except priority.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
