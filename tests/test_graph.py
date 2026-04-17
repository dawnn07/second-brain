from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "tools.graph", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )


def test_build_reports_node_and_edge_counts(sample_wiki: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = _run(["build", "--wiki", str(sample_wiki)], cwd=repo_root)
    payload = json.loads(result.stdout)
    assert payload["nodes"] == 3
    assert payload["edges"] >= 2


def test_query_returns_neighbors_by_relationship_type(sample_wiki: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = _run(
        ["query", "ml/transformers.md", "--type", "supersedes", "--wiki", str(sample_wiki)],
        cwd=repo_root,
    )
    payload = json.loads(result.stdout)
    targets = [hit["target"] for hit in payload["results"]]
    assert any("rnn-encoders.md" in t for t in targets)
    assert all(hit["type"] == "supersedes" for hit in payload["results"])


def test_stats_reports_orphans_and_top_connected(sample_wiki: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = _run(["stats", "--wiki", str(sample_wiki)], cwd=repo_root)
    payload = json.loads(result.stdout)
    assert "orphans" in payload
    assert "most_connected" in payload
    assert payload["node_count"] == 3


def test_viz_dot_emits_digraph(sample_wiki: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = _run(["viz", "--format", "dot", "--wiki", str(sample_wiki)], cwd=repo_root)
    assert "digraph" in result.stdout
    assert "transformers.md" in result.stdout
