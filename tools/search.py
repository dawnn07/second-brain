"""Hybrid BM25 + FAISS search over wiki/ articles.

Usage:
    python -m tools.search index   [--wiki PATH] [--no-embeddings]
    python -m tools.search query Q [--wiki PATH] [--top N] [--no-embeddings]
    python -m tools.search stats   [--wiki PATH]

Output is JSON on stdout so the skill can parse it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rank_bm25 import BM25Okapi

from tools._wiki_io import Article, iter_articles


TOKEN_RE = re.compile(r"[A-Za-z0-9']+")


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]


def _index_dir(wiki_root: Path) -> Path:
    return wiki_root.parent / "search_index"


def _wiki_signature(wiki_root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(wiki_root.rglob("*.md")):
        stat = path.stat()
        h.update(str(path).encode())
        h.update(str(stat.st_mtime_ns).encode())
        h.update(str(stat.st_size).encode())
    return h.hexdigest()


@dataclass
class Index:
    signature: str
    paths: list[str]
    titles: list[str]
    tokens: list[list[str]]
    embeddings: Any | None  # numpy array or None


def _load_articles(wiki_root: Path) -> list[Article]:
    return list(iter_articles(wiki_root))


def _build_embeddings(texts: list[str]):
    try:
        from sentence_transformers import SentenceTransformer
    except Exception:
        return None
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return model.encode(texts, normalize_embeddings=True)


def cmd_index(args: argparse.Namespace) -> int:
    wiki = Path(args.wiki).resolve()
    articles = _load_articles(wiki)
    tokens = [_tokenize(a.title + "\n" + a.body) for a in articles]
    embeddings = None
    if not args.no_embeddings:
        texts = [a.title + "\n\n" + a.body for a in articles]
        embeddings = _build_embeddings(texts)

    index_dir = _index_dir(wiki)
    index_dir.mkdir(parents=True, exist_ok=True)
    payload = Index(
        signature=_wiki_signature(wiki),
        paths=[str(a.path.relative_to(wiki)) for a in articles],
        titles=[a.title for a in articles],
        tokens=tokens,
        embeddings=embeddings,
    )
    (index_dir / "index.pkl").write_bytes(pickle.dumps(payload))
    print(json.dumps({"indexed": len(articles), "embeddings": embeddings is not None}))
    return 0


def _load_index(wiki_root: Path) -> Index:
    pkl = _index_dir(wiki_root) / "index.pkl"
    if not pkl.exists():
        raise SystemExit("No index. Run: python -m tools.search index")
    return pickle.loads(pkl.read_bytes())


def cmd_query(args: argparse.Namespace) -> int:
    wiki = Path(args.wiki).resolve()
    idx = _load_index(wiki)
    bm25 = BM25Okapi(idx.tokens)
    bm25_scores = bm25.get_scores(_tokenize(args.q))

    scores = bm25_scores
    if not args.no_embeddings and idx.embeddings is not None:
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np

            model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            q_vec = model.encode([args.q], normalize_embeddings=True)[0]
            vec_scores = idx.embeddings @ q_vec
            # normalize each component to [0,1] before blending
            def _norm(x: np.ndarray) -> np.ndarray:
                r = x.max() - x.min()
                return (x - x.min()) / r if r > 0 else x * 0
            scores = 0.5 * _norm(bm25_scores) + 0.5 * _norm(vec_scores)
        except Exception:
            pass

    order = sorted(range(len(idx.paths)), key=lambda i: scores[i], reverse=True)
    results = [
        {"path": idx.paths[i], "title": idx.titles[i], "score": float(scores[i])}
        for i in order[: args.top]
    ]
    print(json.dumps({"query": args.q, "results": results}))
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    wiki = Path(args.wiki).resolve()
    idx_path = _index_dir(wiki) / "index.pkl"
    if not idx_path.exists():
        print(json.dumps({"article_count": 0, "bm25_ready": False, "embeddings_ready": False}))
        return 0
    idx: Index = pickle.loads(idx_path.read_bytes())
    fresh = idx.signature == _wiki_signature(wiki)
    print(
        json.dumps(
            {
                "article_count": len(idx.paths),
                "bm25_ready": True,
                "embeddings_ready": idx.embeddings is not None,
                "fresh": fresh,
            }
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools.search")
    parser.add_argument("--wiki", default="wiki", help="Path to wiki/ directory")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_index = sub.add_parser("index")
    p_index.add_argument("--wiki", default="wiki", help="Path to wiki/ directory")
    p_index.add_argument("--no-embeddings", action="store_true")
    p_index.set_defaults(func=cmd_index)

    p_query = sub.add_parser("query")
    p_query.add_argument("--wiki", default="wiki", help="Path to wiki/ directory")
    p_query.add_argument("q")
    p_query.add_argument("--top", type=int, default=5)
    p_query.add_argument("--no-embeddings", action="store_true")
    p_query.set_defaults(func=cmd_query)

    p_stats = sub.add_parser("stats")
    p_stats.add_argument("--wiki", default="wiki", help="Path to wiki/ directory")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
