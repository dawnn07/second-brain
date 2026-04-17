from __future__ import annotations

from pathlib import Path

from tools._wiki_io import Article, iter_articles, parse_article


def test_parse_article_extracts_frontmatter_and_body(sample_wiki: Path) -> None:
    art = parse_article(sample_wiki / "ml" / "transformers.md")
    assert art.title == "Transformers"
    assert art.topic == "ml"
    assert art.confidence == 0.9
    assert art.decay == "slow"
    assert ("supersedes", "rnn-encoders.md") in art.relationships
    assert ("related-to", "attention.md") in art.relationships
    assert "attention-based sequence models" in art.body


def test_parse_article_handles_missing_relationships(sample_wiki: Path) -> None:
    art = parse_article(sample_wiki / "ml" / "rnn-encoders.md")
    assert art.relationships == []


def test_iter_articles_skips_index_and_log(sample_wiki: Path) -> None:
    titles = sorted(a.title for a in iter_articles(sample_wiki))
    assert titles == ["Attention", "RNN Encoders", "Transformers"]


def test_article_slug_is_filename_stem(sample_wiki: Path) -> None:
    art = parse_article(sample_wiki / "ml" / "transformers.md")
    assert art.slug == "transformers.md"
    assert isinstance(art, Article)
