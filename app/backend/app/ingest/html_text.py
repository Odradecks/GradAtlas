"""Turn an official HTML page into heading-scoped text blocks."""

from __future__ import annotations

from html.parser import HTMLParser

_SKIP_TAGS = {"script", "style", "noscript", "svg", "nav", "footer", "header", "form"}
_SKIP_CLASS_PARTS = ("menu", "nav", "breadcrumb", "footer", "header", "brand-bar", "skip-link")
_HEADINGS = {"h1", "h2", "h3"}


class TextBlock:
    def __init__(self, heading_path: str | None, text: str) -> None:
        self.heading_path = heading_path
        self.text = text


class _PageParser(HTMLParser):
    def __init__(self, capture_outside_main: bool) -> None:
        super().__init__(convert_charrefs=True)
        self.capture_outside_main = capture_outside_main
        self.stack: list[tuple[str, bool, bool]] = []
        self.in_main = False
        self.in_title = False
        self.title_parts: list[str] = []
        self.headings: list[str | None] = [None, None, None, None]
        self.buf: list[str] = []
        self.blocks: list[TextBlock] = []
        self.h1: str | None = None

    def _skipping(self) -> bool:
        return any(skipping for _, skipping, _ in self.stack)

    def _capturing(self) -> bool:
        if self._skipping() or self.in_title:
            return False
        return self.in_main or self.capture_outside_main

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        classes = " ".join(
            value.lower() for key, value in attrs if key.lower() == "class" and value
        )
        skip = tag in _SKIP_TAGS or any(part in classes for part in _SKIP_CLASS_PARTS)
        self.stack.append((tag, skip or self._skipping(), skip))
        if tag == "main":
            self.in_main = True
        if tag == "title":
            self.in_title = True
        if tag in _HEADINGS and self._capturing():
            self._flush()
        if tag in {"p", "li", "tr", "br"} and self._capturing():
            self.buf.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in _HEADINGS and self._capturing():
            self._flush(as_heading=int(tag[1]))
        elif tag in {"p", "li", "tr"} and self._capturing():
            self.buf.append("\n")
        if tag == "title":
            self.in_title = False
        if tag == "main":
            self.in_main = False
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
            return
        if not self._capturing():
            return
        text = " ".join(data.split())
        if text:
            self.buf.append(text + " ")

    def _flush(self, as_heading: int | None = None) -> None:
        text = " ".join("".join(self.buf).split())
        self.buf = []
        if not text:
            return
        if as_heading is not None:
            self.headings[as_heading] = text
            for level in range(as_heading + 1, len(self.headings)):
                self.headings[level] = None
            if as_heading == 1 and self.h1 is None:
                self.h1 = text
            return
        path = " / ".join(item for item in self.headings[2:] if item)
        self.blocks.append(TextBlock(path or None, text))

    def close(self) -> None:
        self._flush()
        super().close()


def extract_html(html: str) -> tuple[str | None, list[TextBlock]]:
    has_main = "<main" in html.lower()
    parser = _PageParser(capture_outside_main=not has_main)
    parser.feed(html)
    parser.close()
    title = parser.h1 or " ".join("".join(parser.title_parts).split()) or None
    return title, parser.blocks
