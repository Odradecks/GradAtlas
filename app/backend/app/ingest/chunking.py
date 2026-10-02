"""Split extracted page text into citation-sized chunks."""

from __future__ import annotations

from app.ingest.html_text import TextBlock

_TARGET = 900
_MAX = 1400


class ChunkDraft:
    def __init__(self, heading_path: str | None, text: str, char_start: int, char_end: int) -> None:
        self.heading_path = heading_path
        self.text = text
        self.char_start = char_start
        self.char_end = char_end
        self.token_count = len(text.split())


def _split_long(text: str) -> list[str]:
    if len(text) <= _MAX:
        return [text]
    parts: list[str] = []
    remaining = text
    while len(remaining) > _MAX:
        window = remaining[:_MAX]
        cut = window.rfind(". ")
        if cut < _TARGET // 2:
            cut = window.rfind(" ")
        if cut < _TARGET // 2:
            cut = _MAX
        parts.append(remaining[: cut + 1].strip())
        remaining = remaining[cut + 1 :].strip()
    if remaining:
        parts.append(remaining)
    return parts


def build_chunks(blocks: list[TextBlock]) -> tuple[str, list[ChunkDraft]]:
    """Join blocks into one document body and return non-overlapping chunks."""
    pieces: list[str] = []
    grouped: list[tuple[str | None, str]] = []
    current_heading: str | None = None
    current: list[str] = []

    def flush_group() -> None:
        if not current:
            return
        grouped.append((current_heading, list(current)))

    for block in blocks:
        if block.heading_path != current_heading and current:
            flush_group()
            current = []
        current_heading = block.heading_path
        current.extend(part for part in _split_long(block.text) if part)
    flush_group()

    packed: list[tuple[str | None, str]] = []
    bucket_heading: str | None = None
    bucket: list[str] = []
    bucket_len = 0

    def flush_bucket() -> None:
        nonlocal bucket, bucket_len
        if not bucket:
            return
        body = "\n\n".join(bucket)
        label = bucket_heading.split(" / ")[-1] if bucket_heading else None
        if label and not body.startswith(label):
            body = f"{label}\n\n{body}"
        packed.append((bucket_heading, body))
        bucket = []
        bucket_len = 0

    for heading, parts in grouped:
        for text in parts:
            if bucket and (heading != bucket_heading or bucket_len + len(text) + 2 > _TARGET):
                flush_bucket()
            bucket_heading = heading
            bucket.append(text)
            bucket_len += len(text) + 2
    flush_bucket()

    drafts: list[ChunkDraft] = []
    cursor = 0
    for heading, text in packed:
        if pieces:
            pieces.append("\n\n")
            cursor += 2
        start = cursor
        pieces.append(text)
        cursor += len(text)
        drafts.append(ChunkDraft(heading, text, start, cursor))
    return "".join(pieces), drafts
