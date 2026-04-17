"""Shared frontmatter/body parsing for wiki article files."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.DOTALL)
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
SKIP_FILENAMES = {"index.md", "log.md"}


@dataclass
class Article:
    path: Path
    topic: str
    slug: str
    title: str
    sources: str
    raw: str
    updated: str
    confidence: float | None
    decay: str | None
    relationships: list[tuple[str, str]] = field(default_factory=list)
    see_also: list[str] = field(default_factory=list)
    body: str = ""


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    block, body = match.group(1), match.group(2)
    fields: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields, body


def _parse_relationships(value: str) -> list[tuple[str, str]]:
    if not value:
        return []
    out: list[tuple[str, str]] = []
    for entry in value.split(";"):
        entry = entry.strip()
        if not entry or ":" not in entry:
            continue
        rel_type, _, rest = entry.partition(":")
        link = LINK_RE.search(rest)
        if not link:
            continue
        out.append((rel_type.strip(), link.group(2).strip()))
    return out


def parse_article(path: Path) -> Article:
    text = path.read_text(encoding="utf-8")
    fields, body = _parse_frontmatter(text)
    confidence = fields.get("Confidence")
    return Article(
        path=path,
        topic=path.parent.name,
        slug=path.name,
        title=fields.get("Title", path.stem),
        sources=fields.get("Sources", ""),
        raw=fields.get("Raw", ""),
        updated=fields.get("Updated", ""),
        confidence=float(confidence) if confidence else None,
        decay=fields.get("Decay"),
        relationships=_parse_relationships(fields.get("Relationships", "")),
        body=body.strip(),
    )


def iter_articles(wiki_root: Path) -> Iterator[Article]:
    for path in sorted(wiki_root.rglob("*.md")):
        if path.name in SKIP_FILENAMES:
            continue
        if path.parent == wiki_root:
            continue
        yield parse_article(path)
