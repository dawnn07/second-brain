from __future__ import annotations

from pathlib import Path

from tools._vault_state import VaultState, collect_vault_state


def test_collect_vault_state_counts_articles_and_topics(sample_wiki: Path) -> None:
    state = collect_vault_state(sample_wiki)
    assert state.article_count == 3
    assert state.topic_count == 1
    assert "ml" in state.topics


def test_collect_vault_state_computes_effective_confidence(sample_wiki: Path) -> None:
    state = collect_vault_state(sample_wiki, today="2026-04-17")
    by_title = {a.title: a for a in state.articles}
    # transformers.md: stored 0.9, Updated 2026-04-10, Decay slow → very close to 0.9
    assert by_title["Transformers"].effective_confidence > 0.85
    # rnn-encoders.md: stored 0.6, Updated 2024-01-15, Decay medium → decayed several times
    assert by_title["RNN Encoders"].effective_confidence < 0.6


def test_collect_vault_state_reads_recent_log_entries(tmp_path: Path, sample_wiki: Path) -> None:
    (sample_wiki / "log.md").write_text(
        "# Wiki Log\n\n"
        "## [2026-04-01] ingest | Transformers\n"
        "## [2026-04-02] lint | 0 issues found, 0 auto-fixed\n",
        encoding="utf-8",
    )
    state = collect_vault_state(sample_wiki)
    assert any("ingest | Transformers" in line for line in state.recent_log)
    assert any("lint" in line for line in state.recent_log)


def test_vault_state_orphans_exclude_pages_with_inbound_edges(sample_wiki: Path) -> None:
    state = collect_vault_state(sample_wiki)
    # rnn-encoders is pointed to by transformers (supersedes) → not an orphan
    # attention is pointed to by transformers (related-to) → not an orphan
    # transformers is pointed to by attention (related-to) → not an orphan
    assert state.orphans == []
    assert isinstance(state, VaultState)
