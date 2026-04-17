from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "tools.search", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )


def test_index_then_query_returns_relevant_article(sample_wiki: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    _run(["index", "--wiki", str(sample_wiki), "--no-embeddings"], cwd=repo_root)

    result = _run(
        ["query", "self-attention transformer", "--wiki", str(sample_wiki), "--top", "2", "--no-embeddings"],
        cwd=repo_root,
    )
    payload = json.loads(result.stdout)
    paths = [hit["path"] for hit in payload["results"]]
    assert any(p.endswith("transformers.md") for p in paths)


def test_stats_reports_article_count(sample_wiki: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    _run(["index", "--wiki", str(sample_wiki), "--no-embeddings"], cwd=repo_root)
    result = _run(["stats", "--wiki", str(sample_wiki)], cwd=repo_root)
    payload = json.loads(result.stdout)
    assert payload["article_count"] == 3
    assert payload["bm25_ready"] is True
