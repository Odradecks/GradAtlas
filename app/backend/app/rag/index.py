"""Embed chunks for one verified intake. Re-running skips vectors that already exist."""

from __future__ import annotations

import argparse

from sqlalchemy import select
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.config import settings
from app.database import SessionLocal
from app.models.catalog import ProgramIntake
from app.models.rag import ChunkEmbedding, DocumentChunk
from app.rag.clients import ModelConfigError, embed_texts


def embed_intake(session: Session, intake_id: int) -> tuple[int, int]:
    intake = session.get(ProgramIntake, intake_id)
    if intake is None:
        raise RuntimeError(f"没有入学季 {intake_id}")
    if intake.last_verified_at is None:
        raise RuntimeError(f"入学季 {intake_id} 仍是样例，不嵌入")

    chunks = list(
        session.scalars(
            select(DocumentChunk)
            .where(
                DocumentChunk.intake_id == intake.id,
                DocumentChunk.admission_year == intake.admission_year,
            )
            .order_by(DocumentChunk.id)
        )
    )
    if not chunks:
        raise RuntimeError(f"入学季 {intake_id} 没有可嵌入的官网片段")

    model = settings.embedding_model
    existing = set(
        session.scalars(
            select(ChunkEmbedding.chunk_id).where(
                ChunkEmbedding.chunk_id.in_([chunk.id for chunk in chunks]),
                ChunkEmbedding.embedding_model == model,
            )
        )
    )
    pending = [chunk for chunk in chunks if chunk.id not in existing]
    if not pending:
        return len(chunks), 0

    vectors = embed_texts([chunk.text for chunk in pending])
    for chunk, vector in zip(pending, vectors, strict=True):
        session.add(
            ChunkEmbedding(
                chunk_id=chunk.id,
                embedding_model=model,
                embedding=vector,
            )
        )
    session.flush()
    return len(chunks), len(pending)


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed one intake's document chunks")
    parser.add_argument("--intake", type=int, required=True)
    args = parser.parse_args()
    session = SessionLocal()
    try:
        total, created = embed_intake(session, args.intake)
        session.commit()
        print(f"intake {args.intake}: {total} chunks, {created} new embeddings ({settings.embedding_model})")
    except ModelConfigError as exc:
        session.rollback()
        raise SystemExit(str(exc)) from exc
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
