"""Download the official HTML / PDF files already registered for each program.

    python -m app.ingest.collect --dry-run
    python -m app.ingest.collect --university university-of-tokyo
    python -m app.ingest.collect                      # everything

Only URLs the database already knows are fetched: `sources`, `programs.official_url`,
and rows of `app/seed/source_urls.csv`. Programs without any URL are listed in
`<snapshot_dir>/reports/missing-urls.csv` (full-scope runs only).

Manners: robots.txt is honoured, one request per host every `--delay` seconds,
size cap, no login pages, no crawling of links. Files are stored under
country / school / program / year and recorded in `source_snapshots`.
Same bytes are never stored twice. This script does not parse or embed anything.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from sqlalchemy import select
from sqlalchemy.orm import Session

import app.models  # noqa: F401  (register all tables)
from app.config import settings
from app.database import SessionLocal
from app.ingest.store import ensure_source, snapshot_file
from app.models.catalog import Department, Program, University
from app.models.enums import SourceType
from app.models.provenance import Source, SourceSnapshot

USER_AGENT = "GradAtlas/0.1 (official admissions page archive)"
DEFAULT_URL_CSV = Path(__file__).resolve().parents[1] / "seed" / "source_urls.csv"
BLOCK_MARKERS = (b"just a moment", b"cf-browser-verification", b"access denied", b"attention required")


@dataclass
class FetchResult:
    status: str
    http_status: int | None = None
    content_type: str | None = None
    etag: str | None = None
    last_modified: str | None = None
    body: bytes = b""
    kind: str | None = None


def detect_kind(body: bytes, content_type: str | None) -> str | None:
    if body[:5] == b"%PDF-":
        return "pdf"
    ctype = (content_type or "").lower()
    head = body[:2048].lstrip().lower()
    if "html" in ctype or head.startswith((b"<!doctype html", b"<html")) or b"<head" in head:
        return "html"
    return None


class Fetcher:
    def __init__(self, delay: float, timeout: float, max_bytes: int) -> None:
        self.delay = delay
        self.timeout = timeout
        self.max_bytes = max_bytes
        self._last: dict[str, float] = {}
        self._robots_cache: dict[tuple[str, str], RobotFileParser | None] = {}

    def _wait(self, host: str) -> None:
        gap = time.monotonic() - self._last.get(host, 0.0)
        if gap < self.delay:
            time.sleep(self.delay - gap)

    def _touch(self, host: str) -> None:
        self._last[host] = time.monotonic()

    def _robots(self, scheme: str, host: str) -> RobotFileParser | None:
        key = (scheme, host)
        if key in self._robots_cache:
            return self._robots_cache[key]
        parser: RobotFileParser | None = RobotFileParser()
        try:
            self._wait(host)
            request = urllib.request.Request(f"{scheme}://{host}/robots.txt", headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                parser.parse(response.read(500_000).decode("utf-8", "replace").splitlines())
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                parser.disallow_all = True
            elif 400 <= exc.code < 500:
                parser.allow_all = True
            else:
                parser = None
        except Exception:
            parser = None
        finally:
            self._touch(host)
        self._robots_cache[key] = parser
        return parser

    def _get(self, url: str, host: str):
        last_error = "network-error"
        for attempt in (1, 2):
            self._wait(host)
            try:
                request = urllib.request.Request(
                    url,
                    headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/pdf;q=0.9,*/*;q=0.5"},
                )
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    body = response.read(self.max_bytes + 1)
                    return response.status, response.headers, body, None
            except urllib.error.HTTPError as exc:
                last_error = f"http-{exc.code}"
                if exc.code < 500:
                    return exc.code, None, b"", last_error
            except Exception:
                last_error = "network-error"
            finally:
                self._touch(host)
            if attempt == 1:
                time.sleep(3)
        return None, None, b"", last_error

    def fetch(self, url: str) -> FetchResult:
        parts = urlparse(url)
        if parts.scheme not in ("http", "https") or not parts.netloc:
            return FetchResult("bad-url")
        robots = self._robots(parts.scheme, parts.netloc)
        if robots is None:
            return FetchResult("robots-unreachable")
        if not robots.can_fetch(USER_AGENT, url):
            return FetchResult("robots-disallowed")
        http_status, headers, body, error = self._get(url, parts.netloc)
        if error:
            return FetchResult(error, http_status=http_status)
        if len(body) > self.max_bytes:
            return FetchResult("too-large", http_status=http_status)
        content_type = headers.get("Content-Type")
        kind = detect_kind(body, content_type)
        if kind is None:
            return FetchResult("unsupported-type", http_status=http_status, content_type=content_type)
        if len(body) < (200 if kind == "pdf" else 500):
            return FetchResult("too-small", http_status=http_status, content_type=content_type)
        if kind == "html" and len(body) < 20_000 and any(m in body[:4000].lower() for m in BLOCK_MARKERS):
            return FetchResult("blocked-page", http_status=http_status, content_type=content_type)
        return FetchResult(
            "ok",
            http_status=http_status,
            content_type=content_type,
            etag=headers.get("ETag"),
            last_modified=headers.get("Last-Modified"),
            body=body,
            kind=kind,
        )


def load_csv_sources(session: Session, path: Path) -> list[str]:
    """Add rows from the URL sheet. Returns human-readable problems."""
    problems: list[str] = []
    if not path.exists():
        return problems
    with path.open(encoding="utf-8", newline="") as handle:
        for line_no, row in enumerate(csv.DictReader(handle), start=2):
            uni = (row.get("university_slug") or "").strip()
            prog = (row.get("program_slug") or "").strip()
            url = (row.get("url") or "").strip()
            if not uni or uni.startswith("#") or not prog or not url:
                continue
            if not url.startswith(("http://", "https://")):
                problems.append(f"line {line_no}: not an http(s) URL")
                continue
            try:
                source_type = SourceType((row.get("source_type") or "program_page").strip())
            except ValueError:
                problems.append(f"line {line_no}: unknown source_type {row.get('source_type')!r}")
                continue
            program = session.scalar(
                select(Program)
                .join(Department, Program.department_id == Department.id)
                .join(University, Department.university_id == University.id)
                .where(University.slug == uni, Program.slug == prog)
            )
            if program is None:
                problems.append(f"line {line_no}: unknown program {uni}/{prog}")
                continue
            department = session.get(Department, program.department_id)
            ensure_source(
                session,
                university_id=department.university_id,
                department_id=department.id,
                program_id=program.id,
                url=url,
                source_type=source_type,
                reactivate=True,
            )
    return problems


def save_result(session: Session, source: Source, result: FetchResult) -> tuple[str, Path]:
    digest = hashlib.sha256(result.body).hexdigest()
    path = snapshot_file(session, source, digest=digest, extension=result.kind or "html")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(result.body)
    snapshot = session.scalar(
        select(SourceSnapshot).where(SourceSnapshot.source_id == source.id, SourceSnapshot.content_hash == digest)
    )
    if snapshot is None:
        session.add(
            SourceSnapshot(
                source_id=source.id,
                fetched_at=datetime.now(timezone.utc),
                http_status=result.http_status,
                content_type=(result.content_type or "")[:128] or None,
                etag=(result.etag or "")[:256] or None,
                last_modified=(result.last_modified or "")[:128] or None,
                content_hash=digest,
                storage_path=str(path),
            )
        )
        status = "new"
    else:
        if not snapshot.storage_path or not Path(snapshot.storage_path).exists():
            snapshot.storage_path = str(path)
        status = "unchanged"
    source.last_crawled_at = datetime.now(timezone.utc)
    return status, path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--country", help="country code, e.g. US")
    parser.add_argument("--university", help="university slug")
    parser.add_argument("--program", help="program slug")
    parser.add_argument("--limit", type=int, help="fetch at most N distinct URLs")
    parser.add_argument("--refresh", action="store_true", help="fetch again even if a snapshot exists")
    parser.add_argument("--dry-run", action="store_true", help="list what would be fetched, write nothing")
    parser.add_argument("--delay", type=float, default=2.0, help="seconds between requests to one host")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--max-mb", type=float, default=50.0, help="skip files larger than this")
    parser.add_argument("--urls", type=Path, default=DEFAULT_URL_CSV, help="URL sheet (csv)")
    args = parser.parse_args()

    full_scope = not (args.country or args.university or args.program)
    session = SessionLocal()
    report: list[dict[str, str]] = []
    try:
        stmt = (
            select(Program, University)
            .join(Department, Program.department_id == Department.id)
            .join(University, Department.university_id == University.id)
            .where(Program.is_active.is_(True))
            .order_by(University.country_code, University.slug, Program.slug)
        )
        if args.country:
            stmt = stmt.where(University.country_code == args.country.upper())
        if args.university:
            stmt = stmt.where(University.slug == args.university)
        if args.program:
            stmt = stmt.where(Program.slug == args.program)
        rows = list(session.execute(stmt))
        if not rows:
            raise SystemExit("no program matches the filters")

        problems = load_csv_sources(session, args.urls)
        for program, university in rows:
            if program.official_url:
                ensure_source(
                    session,
                    university_id=university.id,
                    department_id=program.department_id,
                    program_id=program.id,
                    url=program.official_url,
                    source_type=SourceType.PROGRAM_PAGE,
                    reactivate=False,
                )

        by_program = {program.id: (program, university) for program, university in rows}
        sources = list(
            session.scalars(
                select(Source)
                .where(Source.program_id.in_(by_program), Source.is_active.is_(True))
                .order_by(Source.id)
            )
        )
        have_snapshot = set(
            session.scalars(select(SourceSnapshot.source_id).where(SourceSnapshot.source_id.in_([s.id for s in sources])))
        )
        with_url = {s.program_id for s in sources}
        missing = [(p, u) for p, u in rows if p.id not in with_url]

        groups: dict[str, list[Source]] = {}
        for source in sources:
            groups.setdefault(source.url, []).append(source)

        def label(source: Source) -> tuple[str, str, str]:
            program, university = by_program[source.program_id]
            return university.country_code, university.slug, program.slug

        print(
            f"programs {len(rows)} | with URL {len(with_url)} | without URL {len(missing)} | "
            f"distinct URLs {len(groups)}"
        )
        for problem in problems:
            print(f"URL sheet: {problem}")

        fetcher = Fetcher(args.delay, args.timeout, int(args.max_mb * 1024 * 1024))
        fetched = 0
        try:
            for url, group in groups.items():
                if not args.refresh and all(s.id in have_snapshot for s in group):
                    for s in group:
                        report.append(dict(zip(("country", "university", "program"), label(s))) | {"url": url, "status": "skipped-already-have", "file": ""})
                    continue
                if args.limit is not None and fetched >= args.limit:
                    break
                fetched += 1
                if args.dry_run:
                    for s in group:
                        report.append(dict(zip(("country", "university", "program"), label(s))) | {"url": url, "status": "would-fetch", "file": ""})
                    continue
                result = fetcher.fetch(url)
                print(f"[{fetched}] {result.status:20} {url}")
                for s in group:
                    base = dict(zip(("country", "university", "program"), label(s))) | {"url": url}
                    if result.status != "ok":
                        report.append(base | {"status": result.status, "file": ""})
                        continue
                    status, path = save_result(session, s, result)
                    report.append(base | {"status": status, "file": str(path)})
                session.commit()
        finally:
            if args.dry_run:
                session.rollback()
            else:
                session.commit()

        counts: dict[str, int] = {}
        for entry in report:
            counts[entry["status"]] = counts.get(entry["status"], 0) + 1
        print("summary:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())) or "nothing to do")

        if not args.dry_run:
            reports = Path(settings.snapshot_dir) / "reports"
            reports.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            run_file = reports / f"collect-{stamp}.csv"
            with run_file.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["country", "university", "program", "url", "status", "file"])
                writer.writeheader()
                writer.writerows(report)
            print("report:", run_file)
            if full_scope:
                missing_file = reports / "missing-urls.csv"
                with missing_file.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.writer(handle)
                    writer.writerow(["country", "university_slug", "program_slug", "program_name", "url", "source_type"])
                    for program, university in missing:
                        writer.writerow([university.country_code, university.slug, program.slug, program.name_en, "", "program_page"])
                print("programs without URL:", missing_file)
        else:
            print(f"dry run: {fetched} URLs would be fetched; nothing written")
    finally:
        session.close()


if __name__ == "__main__":
    main()
