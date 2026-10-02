"""Move existing snapshots into country / school / program / year folders.

Run: docker compose run --rm backend python -m app.ingest.relocate_snapshots
"""

from __future__ import annotations

import app.models  # noqa: F401
from app.database import SessionLocal
from app.ingest.store import relocate_snapshots


def main() -> None:
    session = SessionLocal()
    try:
        moved = relocate_snapshots(session)
        session.commit()
        print(f"moved {moved} snapshots")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
