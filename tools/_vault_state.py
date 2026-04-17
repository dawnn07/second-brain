"""Vault-wide state snapshot for the dashboard and other read-only consumers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from tools._wiki_io import Article, iter_articles


DECAY_TABLE: dict[str, tuple[float, float]] = {
    # (multiplier, period in days)
    "slow": (0.95, 365.0),
    "medium": (0.90, 182.5),
    "fast": (0.80, 91.25),
}


@dataclass
class ArticleSnapshot:
    title: str
    path: Path
    topic: str
    confidence: float | None
    effective_confidence: float | None
    decay: str | None
    updated: str


@dataclass
class VaultState:
    wiki_root: Path
    articles: list[ArticleSnapshot] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    orphans: list[str] = field(default_factory=list)
    recent_log: list[str] = field(default_factory=list)

    @property
    def article_count(self) -> int:
        return len(self.articles)

    @property
    def topic_count(self) -> int:
        return len(self.topics)

    @property
    def average_effective_confidence(self) -> float | None:
        values = [a.effective_confidence for a in self.articles if a.effective_confidence is not None]
        return sum(values) / len(values) if values else None


def _parse_date(value: str) -> date | None:
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None


def _effective_confidence(art: Article, today: date) -> float | None:
    if art.confidence is None:
        return None
    decay_key = (art.decay or "slow").lower()
    if decay_key not in DECAY_TABLE:
        return art.confidence
    multiplier, period_days = DECAY_TABLE[decay_key]
    updated = _parse_date(art.updated)
    if not updated:
        return art.confidence
    elapsed = max(0, (today - updated).days)
    periods = elapsed / period_days
    return art.confidence * (multiplier ** periods)


def _recent_log(wiki_root: Path, limit: int = 10) -> list[str]:
    log_path = wiki_root / "log.md"
    if not log_path.exists():
        return []
    entries: list[str] = []
    for line in reversed(log_path.read_text(encoding="utf-8").splitlines()):
        if line.startswith("## ["):
            entries.append(line.lstrip("# ").strip())
            if len(entries) >= limit:
                break
    return list(reversed(entries))


def collect_vault_state(wiki_root: Path, today: str | None = None) -> VaultState:
    today_date = _parse_date(today) if today else date.today()
    if today_date is None:
        today_date = date.today()

    articles = list(iter_articles(wiki_root))
    inbound: set[str] = set()
    for art in articles:
        for _, link in art.relationships:
            target = (art.path.parent / link).resolve()
            try:
                rel = target.relative_to(wiki_root.resolve())
                inbound.add(str(rel).replace("\\", "/"))
            except ValueError:
                inbound.add(link)

    snapshots: list[ArticleSnapshot] = []
    topics: set[str] = set()
    orphans: list[str] = []
    for art in articles:
        topics.add(art.topic)
        node_id = f"{art.topic}/{art.slug}"
        snapshots.append(
            ArticleSnapshot(
                title=art.title,
                path=art.path,
                topic=art.topic,
                confidence=art.confidence,
                effective_confidence=_effective_confidence(art, today_date),
                decay=art.decay,
                updated=art.updated,
            )
        )
        has_outbound = bool(art.relationships)
        has_inbound = node_id in inbound
        if not has_outbound and not has_inbound:
            orphans.append(node_id)

    return VaultState(
        wiki_root=wiki_root,
        articles=snapshots,
        topics=sorted(topics),
        orphans=sorted(orphans),
        recent_log=_recent_log(wiki_root),
    )
