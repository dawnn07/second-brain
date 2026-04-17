"""NetworkX-backed graph traversal and visualization for the wiki.

Usage:
    python -m tools.graph build  [--wiki PATH]
    python -m tools.graph query NODE [--type T] [--direction out|in|both] [--wiki PATH]
    python -m tools.graph stats  [--wiki PATH]
    python -m tools.graph viz    [--format dot|tui] [--wiki PATH]

JSON on stdout for build/query/stats. DOT text on stdout for viz --format dot.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import networkx as nx

from tools._wiki_io import iter_articles


def build_graph(wiki_root: Path) -> nx.MultiDiGraph:
    g: nx.MultiDiGraph = nx.MultiDiGraph()
    articles = list(iter_articles(wiki_root))
    for art in articles:
        node_id = f"{art.topic}/{art.slug}"
        g.add_node(node_id, title=art.title, topic=art.topic)
    for art in articles:
        src = f"{art.topic}/{art.slug}"
        for rel_type, link in art.relationships:
            # link is relative to the article's file. Normalize to "topic/slug".
            target = (art.path.parent / link).resolve()
            try:
                rel = target.relative_to(wiki_root.resolve())
                tgt_id = str(rel).replace("\\", "/")
            except ValueError:
                tgt_id = link
            g.add_edge(src, tgt_id, type=rel_type)
    return g


def cmd_build(args: argparse.Namespace) -> int:
    wiki = Path(args.wiki).resolve()
    g = build_graph(wiki)
    print(json.dumps({"nodes": g.number_of_nodes(), "edges": g.number_of_edges()}))
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    wiki = Path(args.wiki).resolve()
    g = build_graph(wiki)
    results = []
    direction = args.direction
    if direction in ("out", "both"):
        for _, tgt, data in g.out_edges(args.node, data=True):
            if args.type and data.get("type") != args.type:
                continue
            results.append({"source": args.node, "target": tgt, "type": data.get("type"), "direction": "out"})
    if direction in ("in", "both"):
        for src, _, data in g.in_edges(args.node, data=True):
            if args.type and data.get("type") != args.type:
                continue
            results.append({"source": src, "target": args.node, "type": data.get("type"), "direction": "in"})
    print(json.dumps({"node": args.node, "results": results}))
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    wiki = Path(args.wiki).resolve()
    g = build_graph(wiki)
    degrees = dict(g.degree())
    orphans = sorted(n for n, d in degrees.items() if d == 0)
    most = sorted(degrees.items(), key=lambda kv: kv[1], reverse=True)[:5]
    print(
        json.dumps(
            {
                "node_count": g.number_of_nodes(),
                "edge_count": g.number_of_edges(),
                "orphans": orphans,
                "most_connected": [{"node": n, "degree": d} for n, d in most],
            }
        )
    )
    return 0


def _emit_dot(g: nx.MultiDiGraph) -> str:
    lines = ["digraph wiki {", '  rankdir="LR";']
    for node, data in g.nodes(data=True):
        label = data.get("title", node).replace('"', '\\"')
        lines.append(f'  "{node}" [label="{label}"];')
    for src, tgt, data in g.edges(data=True):
        rel = data.get("type", "")
        lines.append(f'  "{src}" -> "{tgt}" [label="{rel}"];')
    lines.append("}")
    return "\n".join(lines)


def _run_tui(g: nx.MultiDiGraph) -> int:
    try:
        from textual.app import App, ComposeResult
        from textual.widgets import Header, Footer, Tree
    except Exception as exc:
        print(json.dumps({"error": f"textual not installed: {exc}"}), file=sys.stderr)
        return 1

    class GraphApp(App):
        TITLE = "wiki graph"

        def compose(self) -> ComposeResult:
            yield Header()
            tree: Tree[str] = Tree("wiki")
            tree.root.expand()
            by_topic: dict[str, list[str]] = {}
            for node, data in g.nodes(data=True):
                by_topic.setdefault(data.get("topic", ""), []).append(node)
            for topic, nodes in sorted(by_topic.items()):
                t = tree.root.add(topic or "(root)", expand=True)
                for node in sorted(nodes):
                    leaf = t.add(node)
                    for _, tgt, data in g.out_edges(node, data=True):
                        leaf.add_leaf(f"--{data.get('type','?')}--> {tgt}")
            yield tree
            yield Footer()

    GraphApp().run()
    return 0


def cmd_viz(args: argparse.Namespace) -> int:
    wiki = Path(args.wiki).resolve()
    g = build_graph(wiki)
    if args.format == "dot":
        print(_emit_dot(g))
        return 0
    return _run_tui(g)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools.graph")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_build = sub.add_parser("build")
    p_build.add_argument("--wiki", default="wiki")
    p_build.set_defaults(func=cmd_build)

    p_query = sub.add_parser("query")
    p_query.add_argument("node")
    p_query.add_argument("--type")
    p_query.add_argument("--direction", choices=["out", "in", "both"], default="out")
    p_query.add_argument("--wiki", default="wiki")
    p_query.set_defaults(func=cmd_query)

    p_stats = sub.add_parser("stats")
    p_stats.add_argument("--wiki", default="wiki")
    p_stats.set_defaults(func=cmd_stats)

    p_viz = sub.add_parser("viz")
    p_viz.add_argument("--format", choices=["dot", "tui"], default="tui")
    p_viz.add_argument("--wiki", default="wiki")
    p_viz.set_defaults(func=cmd_viz)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
